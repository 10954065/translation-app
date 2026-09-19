import { useEffect, useState } from "react";
import { FALLBACK_LANGUAGES, fetchSupportedLanguages } from "../lib/languages";

export function useLanguages() {
  const [languages, setLanguages] = useState(FALLBACK_LANGUAGES);
  const [source, setSource] = useState("fallback");

  useEffect(() => {
    let cancelled = false;
    fetchSupportedLanguages()
      .then((list) => {
        if (!cancelled && Array.isArray(list) && list.length > 0) {
          setLanguages(list);
          setSource("live");
        }
      })
      .catch(() => {
        // Backend unreachable at mount time - fallback list keeps the form usable.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { languages, source };
}
