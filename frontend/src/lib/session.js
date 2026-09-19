const STORAGE_KEY = "dmt_session";

export function saveSession({ name, language, roomCode }) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ name, language, roomCode }));
  } catch {
    // sessionStorage unavailable (private browsing lockdown, etc.) - not fatal.
  }
}

export function loadSession() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearSession() {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
