import { useCallback, useState } from "react";
import { useAuth } from "./context/AuthContext";
import UserForm from "./components/UserForm";
import LessonView from "./components/LessonView";
import PracticeView from "./components/PracticeView";
import FeedbackView from "./components/FeedbackView";
import { callLearnAPI } from "./services/api";
import type {
  LearnRequestPayload,
  LearningState,
  SessionFormValues,
} from "./types/learning";
import "./styles.css";

export default function App() {
  const { credential, user } = useAuth();
  const [learningState, setLearningState] = useState<LearningState | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runLearn = useCallback(async (payload: LearnRequestPayload) => {
    setLoading(true);
    setError("");
    try {
      if (!credential) {
        throw new Error("Sign in with Google to continue.");
      }
      const state = await callLearnAPI(payload, credential);
      setLearningState(state);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [credential]);

  function handleStartSession(formValues: SessionFormValues) {
    runLearn({
      action: "full",
      user_id: formValues.user_id,
      level: formValues.level,
      target_language: formValues.target_language,
      native_language: formValues.native_language,
      user_answers: [],
    });
  }

  function handleSubmitAnswers(userAnswers: string[]) {
    if (!learningState) return;
    runLearn({
      action: "submit_answers",
      user_id: learningState.user_id,
      level: learningState.level,
      target_language: learningState.target_language,
      native_language: learningState.native_language,
      lesson: learningState.lesson,
      exercises: learningState.exercises,
      user_answers: userAnswers,
    });
  }

  function handleNewQuestions() {
    if (!learningState) return;
    runLearn({
      action: "new_exercises",
      user_id: learningState.user_id,
      level: learningState.level,
      target_language: learningState.target_language,
      native_language: learningState.native_language,
      lesson: learningState.lesson,
      user_answers: [],
    });
  }

  function handleReset() {
    setLearningState(null);
    setError("");
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Language tutor</h1>
        <p className="tagline">
          Start a session, read the lesson, complete exercises, and review
          feedback.
        </p>
      </header>

      {loading ? <div className="banner loading">Loading…</div> : null}

      {!learningState ? (
        <UserForm
          onSubmit={handleStartSession}
          disabled={loading}
          error={error}
        />
      ) : (
        <>
          {user ? (
            <p className="hint session-user">Signed in as {user.email}</p>
          ) : null}
          <div className="toolbar">
            <button
              type="button"
              className="btn ghost"
              onClick={handleReset}
              disabled={loading}
            >
              New session
            </button>
          </div>
          <LessonView lesson={learningState.lesson} />
          <PracticeView
            exercises={learningState.exercises}
            userAnswersFromServer={learningState.user_answers}
            onSubmitAnswers={handleSubmitAnswers}
            onNewQuestions={handleNewQuestions}
            disabled={loading}
            error={error}
          />
          <FeedbackView
            evaluation={learningState.evaluation}
            memory={learningState.memory}
          />
        </>
      )}
    </div>
  );
}
