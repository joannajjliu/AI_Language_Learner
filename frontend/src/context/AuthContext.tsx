import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { verifyGoogleCredential } from "../services/auth";
import type { AuthUser } from "../types/auth";

const STORAGE_KEY = "language-tutor-auth";

type StoredAuth = {
  user: AuthUser;
  credential: string;
};

type AuthContextValue = {
  user: AuthUser | null;
  credential: string | null;
  loading: boolean;
  error: string;
  signInWithGoogle: (credential: string) => Promise<void>;
  signOut: () => void;
  clearError: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function readStoredAuth(): StoredAuth | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredAuth;
    if (!parsed?.user?.user_id || !parsed.credential) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeStoredAuth(value: StoredAuth | null) {
  if (!value) {
    sessionStorage.removeItem(STORAGE_KEY);
    return;
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(value));
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [stored] = useState(() => readStoredAuth());
  const [user, setUser] = useState<AuthUser | null>(stored?.user ?? null);
  const [credential, setCredential] = useState<string | null>(
    stored?.credential ?? null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const signInWithGoogle = useCallback(async (googleCredential: string) => {
    setLoading(true);
    setError("");
    try {
      const verified = await verifyGoogleCredential(googleCredential);
      const next = { user: verified, credential: googleCredential };
      writeStoredAuth(next);
      setUser(verified);
      setCredential(googleCredential);
    } catch (err) {
      writeStoredAuth(null);
      setUser(null);
      setCredential(null);
      setError(err instanceof Error ? err.message : String(err));
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const signOut = useCallback(() => {
    writeStoredAuth(null);
    setUser(null);
    setCredential(null);
    setError("");
  }, []);

  const clearError = useCallback(() => setError(""), []);

  const value = useMemo(
    () => ({
      user,
      credential,
      loading,
      error,
      signInWithGoogle,
      signOut,
      clearError,
    }),
    [user, credential, loading, error, signInWithGoogle, signOut, clearError],
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
