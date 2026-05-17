import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import type { SessionFormValues } from "../types/learning";
import GoogleSignIn from "./GoogleSignIn";

const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"] as const;

type Level = (typeof LEVELS)[number];

type FormState = Omit<SessionFormValues, "user_id"> & { user_id: string };

const defaultForm: FormState = {
  user_id: "test-user",
  level: "A1",
  target_language: "Spanish",
  native_language: "English",
};

type UserFormProps = {
  onSubmit: (values: SessionFormValues) => void;
  disabled: boolean;
  error: string;
};

export default function UserForm({ onSubmit, disabled, error }: UserFormProps) {
  const { user, googleEnabled, signOut, loading: authLoading } = useAuth();
  const [values, setValues] = useState<FormState>(defaultForm);

  function handleChange<K extends keyof FormState>(
    field: K,
    value: FormState[K],
  ) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const user_id = googleEnabled
      ? user?.user_id ?? ""
      : values.user_id.trim();
    if (!user_id) {
      return;
    }
    onSubmit({
      user_id,
      level: values.level,
      target_language: values.target_language.trim() || "English",
      native_language: values.native_language.trim() || "English",
    });
  }

  const formDisabled = disabled || authLoading;
  const needsGoogleSignIn = googleEnabled && !user;

  return (
    <section className="card">
      <h2>Start session</h2>

      {googleEnabled ? (
        <div className="auth-panel">
          {user ? (
            <div className="auth-user">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt=""
                  className="auth-avatar"
                  width={40}
                  height={40}
                />
              ) : null}
              <div>
                <p className="auth-name">{user.name}</p>
                <p className="auth-email">{user.email}</p>
              </div>
              <button
                type="button"
                className="btn ghost"
                onClick={signOut}
                disabled={formDisabled}
              >
                Sign out
              </button>
            </div>
          ) : (
            <>
              <p className="hint">Sign in with Google to save progress per account.</p>
              <GoogleSignIn disabled={formDisabled} />
            </>
          )}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="form">
        {!googleEnabled ? (
          <label className="field">
            <span>User ID</span>
            <input
              type="text"
              name="user_id"
              value={values.user_id}
              onChange={(e) => handleChange("user_id", e.target.value)}
              placeholder="e.g. learner-1"
              autoComplete="username"
              disabled={formDisabled}
              required
            />
          </label>
        ) : null}
        <label className="field">
          <span>Level (CEFR)</span>
          <select
            name="level"
            value={values.level}
            onChange={(e) => handleChange("level", e.target.value as Level)}
            disabled={formDisabled}
          >
            {LEVELS.map((lv) => (
              <option key={lv} value={lv}>
                {lv}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Target language</span>
          <input
            type="text"
            name="target_language"
            value={values.target_language}
            onChange={(e) => handleChange("target_language", e.target.value)}
            placeholder="e.g. Spanish"
            disabled={formDisabled}
          />
        </label>
        <label className="field">
          <span>Native language</span>
          <input
            type="text"
            name="native_language"
            value={values.native_language}
            onChange={(e) => handleChange("native_language", e.target.value)}
            placeholder="e.g. English"
            disabled={formDisabled}
          />
        </label>
        {error ? <p className="form-error">{error}</p> : null}
        <button
          type="submit"
          className="btn primary"
          disabled={formDisabled || needsGoogleSignIn}
        >
          {formDisabled ? "Starting…" : "Start lesson"}
        </button>
      </form>
    </section>
  );
}
