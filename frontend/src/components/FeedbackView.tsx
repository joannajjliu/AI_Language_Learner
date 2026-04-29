import type { Evaluation, MemoryState } from "../types/learning";

type FeedbackViewProps = {
  evaluation: Evaluation | null | undefined;
  memory: MemoryState | null | undefined;
};

export default function FeedbackView({
  evaluation,
  memory,
}: FeedbackViewProps) {
  const ev =
    evaluation && typeof evaluation === "object" ? evaluation : null;
  const mem = memory && typeof memory === "object" ? memory : null;

  if (!ev && !mem) {
    return null;
  }

  const score = ev?.score;
  const feedback = ev?.feedback;
  const needsReview = ev?.needs_review;

  return (
    <section className="card feedback">
      <h2>Feedback</h2>
      {ev ? (
        <div className="feedback-body">
          {score != null && (
            <p>
              <strong>Score:</strong> {score}
            </p>
          )}
          {typeof needsReview === "boolean" && (
            <p>
              <strong>Correctness / review:</strong>{" "}
              {needsReview
                ? "Needs more review — keep practicing."
                : "On track — nice work."}
            </p>
          )}
          {feedback ? (
            <div className="feedback-text">
              <strong>Explanation</strong>
              <p>{feedback}</p>
            </div>
          ) : null}
          {!feedback && score == null && needsReview == null ? (
            <p className="muted">No evaluation details returned.</p>
          ) : null}
        </div>
      ) : null}
      {mem ? (
        <div className="memory-block">
          <h3>Memory snapshot</h3>
          {Array.isArray(mem.completed_topics) &&
          mem.completed_topics.length > 0 ? (
            <p>
              <strong>Completed topics:</strong>{" "}
              {mem.completed_topics.join(", ")}
            </p>
          ) : null}
          {Array.isArray(mem.mistakes) && mem.mistakes.length > 0 ? (
            <div>
              <strong>Corrections / notes</strong>
              <ul>
                {mem.mistakes.map((m, i) => (
                  <li key={i}>
                    {m.topic ? `${m.topic}: ` : ""}
                    {m.reason ?? JSON.stringify(m)}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {Array.isArray(mem.known_vocab) && mem.known_vocab.length > 0 ? (
            <p>
              <strong>Known vocabulary (sample):</strong>{" "}
              {mem.known_vocab.join(", ")}
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
