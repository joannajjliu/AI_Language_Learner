import type { Lesson, LessonExample } from "../types/learning";

type LessonViewProps = {
  lesson: Lesson | null | undefined;
};

export default function LessonView({ lesson }: LessonViewProps) {
  if (!lesson || typeof lesson !== "object") {
    return null;
  }

  const topic = lesson.topic;
  const objective = lesson.objective;
  const content = lesson.content;
  const examples = Array.isArray(lesson.examples) ? lesson.examples : [];

  const hasBody =
    Boolean(topic) ||
    Boolean(objective) ||
    Boolean(content) ||
    examples.length > 0;

  if (!hasBody) {
    return (
      <section className="card muted">
        <h2>Lesson</h2>
        <p>No lesson content yet.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Lesson</h2>
      {topic ? (
        <p className="lesson-meta">
          <strong>Topic:</strong> {topic}
        </p>
      ) : null}
      {objective ? (
        <p className="lesson-meta">
          <strong>Objective:</strong> {objective}
        </p>
      ) : null}
      {content ? <div className="lesson-body">{content}</div> : null}
      {examples.length > 0 ? (
        <div className="examples">
          <h3>Examples</h3>
          <ul>
            {examples.map((ex, i) => {
              if (typeof ex === "string") {
                return (
                  <li key={i}>
                    <div>{ex}</div>
                  </li>
                );
              }
              const row = ex as LessonExample;
              const hasTarget = row.target != null && row.target !== "";
              const hasNative = row.native != null && row.native !== "";
              return (
                <li key={i}>
                  {hasTarget ? (
                    <div>
                      <span className="label">Target:</span> {row.target}
                    </div>
                  ) : null}
                  {hasNative ? (
                    <div>
                      <span className="label">Native:</span> {row.native}
                    </div>
                  ) : null}
                  {!hasTarget && !hasNative ? (
                    <div>{JSON.stringify(row)}</div>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
