import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";

const googleClientId = (process.env.REACT_APP_GOOGLE_CLIENT_ID || "").trim();

const el = document.getElementById("root");
if (!el) {
  throw new Error('Missing root element with id "root"');
}

const app = (
  <AuthProvider>
    <App />
  </AuthProvider>
);

createRoot(el).render(
  googleClientId ? (
    <GoogleOAuthProvider clientId={googleClientId}>{app}</GoogleOAuthProvider>
  ) : (
    app
  ),
);
