import { useEffect, useRef } from "react";
import { CloseIcon } from "../icons/Icon";

export function Modal({ title, subtitle, onClose, children, labelledBy }) {
  const sheetRef = useRef(null);
  const titleId = labelledBy || "modal-title";

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    const firstField = sheetRef.current?.querySelector("input, select, button");
    firstField?.focus();
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-sheet" role="dialog" aria-modal="true" aria-labelledby={titleId} ref={sheetRef}>
        <div className="modal-header">
          <div>
            <h2 className="modal-title" id={titleId}>
              {title}
            </h2>
            {subtitle && <p className="modal-subtitle">{subtitle}</p>}
          </div>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close dialog">
            <CloseIcon size={16} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
