const GOOGLE_CLIENT_ID = (process.env.REACT_APP_GOOGLE_CLIENT_ID || "").trim();

if (!GOOGLE_CLIENT_ID) {
  throw new Error(
    "REACT_APP_GOOGLE_CLIENT_ID is required. Set it in frontend/.env.local (same OAuth Web client as GOOGLE_CLIENT_ID on the API).",
  );
}

export { GOOGLE_CLIENT_ID };
