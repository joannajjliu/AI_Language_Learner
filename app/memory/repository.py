"""PostgreSQL persistence for normalized learner memory tables."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.memory.constants import DEFAULT_MEMORY
from app.memory.updates import extract_vocab_from_lesson

_KNOWN_STATUSES = frozenset({"learning", "known", "mastered"})


class PostgresMemoryRepository:
    """Read/write users, vocabulary, SRS state, reviews, and JSON snapshots."""

    def __init__(self, conninfo: str) -> None:
        self._conninfo = conninfo

    def ensure_user(
        self,
        user_id: str,
        *,
        email: str,
        display_name: str,
        native_language: str,
        target_language: str,
        cefr_level: str,
    ) -> None:
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (
                        id,
                        email,
                        display_name,
                        native_language,
                        target_language,
                        cefr_level
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        email = EXCLUDED.email,
                        display_name = EXCLUDED.display_name,
                        native_language = EXCLUDED.native_language,
                        target_language = EXCLUDED.target_language,
                        cefr_level = EXCLUDED.cefr_level,
                        updated_at = NOW()
                    """,
                    (
                        user_id,
                        email,
                        display_name,
                        native_language,
                        target_language,
                        cefr_level,
                    ),
                )
            conn.commit()

    def sync_user_languages(
        self,
        user_id: str,
        *,
        native_language: str,
        target_language: str,
        cefr_level: str,
    ) -> None:
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users SET
                        native_language = %s,
                        target_language = %s,
                        cefr_level = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (native_language, target_language, cefr_level, user_id),
                )
            conn.commit()

    def load_memory(self, user_id: str) -> Dict[str, Any]:
        payload = self._load_json_payload(user_id)
        known_vocab = self._load_known_vocab_lemmas(user_id)
        memory = deepcopy(DEFAULT_MEMORY)
        memory["completed_topics"] = list(payload.get("completed_topics") or [])
        memory["mistakes"] = list(payload.get("mistakes") or [])
        memory["known_vocab"] = known_vocab
        return memory

    def save_memory(
        self,
        user_id: str,
        memory: Dict[str, Any],
        *,
        target_language: str,
        lesson: Dict[str, Any] | None = None,
        evaluation: Dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "completed_topics": list(memory.get("completed_topics") or []),
            "mistakes": list(memory.get("mistakes") or []),
        }
        lesson_entries = extract_vocab_from_lesson(lesson or {})
        correct = not bool((evaluation or {}).get("needs_review"))

        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                self._upsert_json_payload(cur, user_id, payload)
                for entry in lesson_entries:
                    vocab_id = self._upsert_vocabulary_item(
                        cur,
                        language=target_language,
                        lemma=entry["lemma"],
                        translation=entry["translation"],
                    )
                    self._upsert_user_vocab_state(
                        cur,
                        user_id=user_id,
                        vocab_id=vocab_id,
                        correct=correct,
                    )
                    self._insert_review(
                        cur,
                        user_id=user_id,
                        vocab_id=vocab_id,
                        correct=correct,
                    )
            conn.commit()

    def _load_json_payload(self, user_id: str) -> Dict[str, Any]:
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT payload FROM learner_memory WHERE user_id = %s",
                    (user_id,),
                )
                row = cur.fetchone()
        if not row:
            return {}
        payload = row["payload"]
        return payload if isinstance(payload, dict) else {}

    def _load_known_vocab_lemmas(self, user_id: str) -> List[str]:
        with psycopg.connect(self._conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT vi.lemma
                    FROM user_vocab_state uvs
                    JOIN vocabulary_items vi ON vi.id = uvs.vocab_id
                    WHERE uvs.user_id = %s
                      AND (
                        uvs.status = ANY(%s)
                        OR uvs.familiarity_score >= 0.4
                        OR uvs.times_correct > 0
                      )
                    ORDER BY uvs.updated_at DESC
                    """,
                    (user_id, list(_KNOWN_STATUSES)),
                )
                rows = cur.fetchall()
        return [str(row["lemma"]) for row in rows if row.get("lemma")]

    def _upsert_json_payload(
        self,
        cur: psycopg.Cursor,
        user_id: str,
        payload: Dict[str, Any],
    ) -> None:
        cur.execute(
            """
            INSERT INTO learner_memory (user_id, payload)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                payload = EXCLUDED.payload,
                updated_at = NOW()
            """,
            (user_id, Json(deepcopy(payload))),
        )

    def _upsert_vocabulary_item(
        self,
        cur: psycopg.Cursor,
        *,
        language: str,
        lemma: str,
        translation: str,
    ) -> int:
        cur.execute(
            """
            INSERT INTO vocabulary_items (lemma, translation, language)
            VALUES (%s, %s, %s)
            ON CONFLICT (language, lemma) DO UPDATE SET
                translation = EXCLUDED.translation
            RETURNING id
            """,
            (lemma, translation, language),
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Failed to upsert vocabulary item")
        return int(row["id"])

    def _upsert_user_vocab_state(
        self,
        cur: psycopg.Cursor,
        *,
        user_id: str,
        vocab_id: int,
        correct: bool,
    ) -> None:
        familiarity_delta = 0.1 if correct else -0.05
        status = "known" if correct else "learning"
        cur.execute(
            """
            INSERT INTO user_vocab_state (
                user_id,
                vocab_id,
                familiarity_score,
                memory_strength,
                times_seen,
                times_correct,
                times_wrong,
                last_reviewed_at,
                status
            )
            VALUES (
                %s, %s,
                GREATEST(0, LEAST(1, %s)),
                CASE WHEN %s THEN 0.2 ELSE 0.1 END,
                1,
                CASE WHEN %s THEN 1 ELSE 0 END,
                CASE WHEN %s THEN 0 ELSE 1 END,
                NOW(),
                %s
            )
            ON CONFLICT (user_id, vocab_id) DO UPDATE SET
                familiarity_score = GREATEST(
                    0,
                    LEAST(1, user_vocab_state.familiarity_score + %s)
                ),
                memory_strength = GREATEST(
                    user_vocab_state.memory_strength,
                    CASE WHEN %s THEN 0.2 ELSE user_vocab_state.memory_strength END
                ),
                times_seen = user_vocab_state.times_seen + 1,
                times_correct = user_vocab_state.times_correct
                    + CASE WHEN %s THEN 1 ELSE 0 END,
                times_wrong = user_vocab_state.times_wrong
                    + CASE WHEN %s THEN 0 ELSE 1 END,
                last_reviewed_at = NOW(),
                status = CASE
                    WHEN %s AND user_vocab_state.familiarity_score + %s >= 0.6
                        THEN 'known'
                    ELSE 'learning'
                END,
                updated_at = NOW()
            """,
            (
                user_id,
                vocab_id,
                familiarity_delta if correct else 0.0,
                correct,
                correct,
                correct,
                status,
                familiarity_delta,
                correct,
                correct,
                correct,
                correct,
                familiarity_delta,
            ),
        )

    def _insert_review(
        self,
        cur: psycopg.Cursor,
        *,
        user_id: str,
        vocab_id: int,
        correct: bool,
    ) -> None:
        cur.execute(
            """
            INSERT INTO review_history (user_id, vocab_id, result)
            VALUES (%s, %s, %s)
            """,
            (user_id, vocab_id, "correct" if correct else "incorrect"),
        )
