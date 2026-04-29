import { useState, type FormEvent } from "react";
import type { SessionFormValues } from "../types/learning";

const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"] as const;

type Level = (typeof LEVELS)[number];

type FormState = SessionFormValues;

const defaultForm: FormState = {
  user_id: "",
  level: "A1",
  target_language: "",
  native_language: "",
};

type UserFormProps = {
  onSubmit: (values: SessionFormValues) => void;
  disabled: boolean;
  error: string;
};

export default function UserForm({ onSubmit, disabled, error }: UserFormProps) {
  const [values, setValues] = useState<FormState>(defaultForm);

  function handleChange<K extends keyof FormState>(field: K, value: FormState[K]) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const user_id = values.user_id.trim();
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

  return (
    <section className="card">
      <h2>Start session</h2>
      <form onSubmit={handleSubmit} className="form">
        <label className="field">
          <span>User ID</span>
          <input
            type="text"
            name="user_id"
            value={values.user_id}
            onChange={(e) => handleChange("user_id", e.target.value)}
            placeholder="e.g. learner-1"
            autoComplete="username"
            disabled={disabled}
            required
          />
        </label>
        <label className="field">
          <span>Level (CEFR)</span>
          <select
            name="level"
            value={values.level}
            onChange={(e) => handleChange("level", e.target.value as Level)}
            disabled={disabled}
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
            disabled={disabled}
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
            disabled={disabled}
          />
        </label>
        {error ? <p className="form-error">{error}</p> : null}
        <button type="submit" className="btn primary" disabled={disabled}>
          {disabled ? "Starting…" : "Start lesson"}
        </button>
      </form>
    </section>
  );
}
