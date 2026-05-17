import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { GOOGLE_CLIENT_ID } from "./config";

const el = document.getElementById("root");
if (!el) {
  throw new Error('Missing root element with id "root"');
}

createRoot(el).render(
  <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
    <AuthProvider>
      <App />
    </AuthProvider>
  </GoogleOAuthProvider>,
);
