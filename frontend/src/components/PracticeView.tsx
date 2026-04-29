import { useEffect, useMemo, useState, type FormEvent } from "react";
import type { Exercise } from "../types/learning";

function answersFromState(
  exercises: Exercise[],
  userAnswersFromServer: string[] | undefined,
): string[] {
  const list = Array.isArray(userAnswersFromServer)
    ? userAnswersFromServer
    : [];
  return exercises.map((_, i) => list[i] ?? "");
}

type PracticeViewProps = {
  exercises: Exercise[] | undefined;
  userAnswersFromServer: string[] | undefined;
  onSubmitAnswers: (answers: string[]) => void;
  disabled: boolean;
  error: string;
};

export default function PracticeView({
  exercises,
  userAnswersFromServer,
  onSubmitAnswers,
  disabled,
  error,
}: PracticeViewProps) {
  const items = useMemo(
    () => (Array.isArray(exercises) ? exercises : []),
    [exercises],
  );
  const [answers, setAnswers] = useState<string[]>(() =>
    answersFromState(items, userAnswersFromServer),
  );

  useEffect(() => {
    setAnswers(answersFromState(items, userAnswersFromServer));
  }, [items, userAnswersFromServer]);

  function setAnswerAt(index: number, value: string) {
    setAnswers((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const normalized = items.map((_, i) => (answers[i] ?? "").trim());
    onSubmitAnswers(normalized);
  }

  if (items.length === 0) {
    return (
      <section className="card muted">
        <h2>Practice</h2>
        <p>No exercises for this lesson.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Practice</h2>
      <form onSubmit={handleSubmit} className="form">
        {items.map((ex, index) => (
          <div key={ex.id ?? String(index)} className="exercise-block">
            <p className="exercise-question">
              {ex.type ? (
                <span className="badge">{ex.type}</span>
              ) : null}{" "}
              {ex.question ?? "Question"}
            </p>
            <label className="field">
              <span>Your answer</span>
              <input
                type="text"
                value={answers[index] ?? ""}
                onChange={(e) => setAnswerAt(index, e.target.value)}
                disabled={disabled}
                placeholder="Type your answer"
              />
            </label>
          </div>
        ))}
        {error ? <p className="form-error">{error}</p> : null}
        <button type="submit" className="btn primary" disabled={disabled}>
          {disabled ? "Submitting…" : "Submit answers"}
        </button>
      </form>
    </section>
  );
}
