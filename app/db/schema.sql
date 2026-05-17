-- Learner profile (id is google-{sub} from Google Sign-In).
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    display_name TEXT NOT NULL,
    native_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    cefr_level TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vocabulary_items (
    id BIGSERIAL PRIMARY KEY,
    lemma TEXT NOT NULL,
    translation TEXT NOT NULL,
    language TEXT NOT NULL,
    difficulty SMALLINT,
    part_of_speech TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (language, lemma)
);

CREATE TABLE IF NOT EXISTS user_vocab_state (
    user_id TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    vocab_id BIGINT NOT NULL REFERENCES vocabulary_items (id) ON DELETE CASCADE,
    familiarity_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    memory_strength DOUBLE PRECISION NOT NULL DEFAULT 0,
    ease_factor DOUBLE PRECISION NOT NULL DEFAULT 2.5,
    times_seen INTEGER NOT NULL DEFAULT 0,
    times_correct INTEGER NOT NULL DEFAULT 0,
    times_wrong INTEGER NOT NULL DEFAULT 0,
    last_reviewed_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, vocab_id)
);

CREATE INDEX IF NOT EXISTS idx_user_vocab_state_next_review
    ON user_vocab_state (next_review_at)
    WHERE next_review_at IS NOT NULL;

CREATE TABLE IF NOT EXISTS review_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    vocab_id BIGINT NOT NULL REFERENCES vocabulary_items (id) ON DELETE CASCADE,
    result TEXT NOT NULL,
    latency INTEGER,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_review_history_user_reviewed
    ON review_history (user_id, reviewed_at DESC);

-- Legacy JSON snapshot store (used by the LangGraph memory agent today).
CREATE TABLE IF NOT EXISTS learner_memory (
    user_id TEXT PRIMARY KEY,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
