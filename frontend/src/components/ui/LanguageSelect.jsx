import { ChevronDownIcon } from "../icons/Icon";

export function LanguageSelect({ id, value, onChange, languages, label = "Language", required = true }) {
  return (
    <div className="field">
      <label htmlFor={id} className="field-label">
        {label}
      </label>
      <div className="select-wrap">
        <select id={id} value={value} onChange={(e) => onChange(e.target.value)} required={required}>
          <option value="" disabled>
            Choose your language
          </option>
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name} {lang.nativeName && lang.nativeName !== lang.name ? `· ${lang.nativeName}` : ""}
            </option>
          ))}
        </select>
        <ChevronDownIcon size={16} className="select-chevron" />
      </div>
    </div>
  );
}
