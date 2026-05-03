/** Matches backend `LearningState` / API `state` payload. */

export interface LessonExample {
  target?: string;
  native?: string;
}

export interface Lesson {
  topic?: string;
  objective?: string;
  content?: string;
  examples?: (LessonExample | string)[];
  [key: string]: unknown;
}

export interface Exercise {
  id?: string;
  type?: string;
  question?: string;
  topic?: string;
  [key: string]: unknown;
}

export interface Evaluation {
  score?: number;
  feedback?: string;
  needs_review?: boolean;
  [key: string]: unknown;
}

export interface MemoryMistake {
  topic?: string;
  reason?: string;
}

export interface MemoryState {
  completed_topics?: string[];
  mistakes?: MemoryMistake[];
  known_vocab?: string[];
  [key: string]: unknown;
}

export interface LearningState {
  user_id: string;
  level: string;
  target_language: string;
  native_language: string;
  lesson: Lesson;
  exercises: Exercise[];
  user_answers: string[];
  evaluation: Evaluation;
  memory: MemoryState;
  loop_count: number;
}

/** POST /learn request body. */

export type LearnAction = "full" | "submit_answers" | "new_exercises";

export interface LearnRequestPayload {
  user_id: string;
  level: string;
  target_language: string;
  native_language: string;
  user_answers?: string[];
  action?: LearnAction;
  lesson?: Lesson;
  exercises?: Exercise[];
}

/** Fields collected from the start-session form (no answers). */
export type SessionFormValues = Pick<
  LearnRequestPayload,
  "user_id" | "level" | "target_language" | "native_language"
>;
