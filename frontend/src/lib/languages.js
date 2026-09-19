import { API_BASE_URL } from "./socket";

// Mirrors app/utils/languages.py - used only until the live /api/languages
// response arrives, so the selector never renders empty on first paint.
export const FALLBACK_LANGUAGES = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "fr", name: "French", nativeName: "Français" },
  { code: "de", name: "German", nativeName: "Deutsch" },
  { code: "es", name: "Spanish", nativeName: "Español" },
  { code: "pt", name: "Portuguese", nativeName: "Português" },
  { code: "it", name: "Italian", nativeName: "Italiano" },
  { code: "nl", name: "Dutch", nativeName: "Nederlands" },
  { code: "sv", name: "Swedish", nativeName: "Svenska" },
  { code: "ar", name: "Arabic", nativeName: "العربية" },
  { code: "zh-CN", name: "Chinese (Simplified)", nativeName: "中文" },
  { code: "ja", name: "Japanese", nativeName: "日本語" },
  { code: "ko", name: "Korean", nativeName: "한국어" },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी" },
  { code: "ak", name: "Twi", nativeName: "Twi" },
  { code: "ee", name: "Ewe", nativeName: "Eʋegbe" },
];

export async function fetchSupportedLanguages() {
  const response = await fetch(`${API_BASE_URL}/api/languages`);
  if (!response.ok) {
    throw new Error("Failed to load supported languages");
  }
  const data = await response.json();
  return data.languages;
}

export function languageName(code, languages) {
  const match = (languages || FALLBACK_LANGUAGES).find((lang) => lang.code === code);
  return match ? match.name : code;
}
