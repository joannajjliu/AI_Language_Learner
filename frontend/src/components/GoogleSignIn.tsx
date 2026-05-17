import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { useAuth } from "../context/AuthContext";

type GoogleSignInProps = {
  disabled?: boolean;
};

export default function GoogleSignIn({ disabled }: GoogleSignInProps) {
  const { signInWithGoogle, loading, error, clearError } = useAuth();

  async function handleSuccess(response: CredentialResponse) {
    clearError();
    const credential = response.credential;
    if (!credential) {
      return;
    }
    try {
      await signInWithGoogle(credential);
    } catch {
      // Error state is set in context.
    }
  }

  const busy = Boolean(disabled || loading);

  return (
    <div className="google-sign-in">
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={() => clearError()}
        useOneTap={false}
        theme="outline"
        size="large"
        text="signin_with"
        shape="rectangular"
        width="320"
      />
      {busy ? <p className="hint">Verifying sign-in…</p> : null}
      {error ? <p className="form-error">{error}</p> : null}
    </div>
  );
}
