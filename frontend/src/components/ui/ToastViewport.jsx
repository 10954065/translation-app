import { useToast } from "../../context/ToastContext";
import { AlertIcon, CheckIcon, CloseIcon } from "../icons/Icon";

const ICONS = {
  success: CheckIcon,
  error: AlertIcon,
  warning: AlertIcon,
  info: CheckIcon,
};

export function ToastViewport() {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-viewport" aria-live="polite" aria-atomic="false">
      {toasts.map((toast) => {
        const Icon = ICONS[toast.type] || CheckIcon;
        return (
          <div key={toast.id} className={`toast toast--${toast.type}`} role="status">
            <Icon size={16} />
            <span className="toast-message">{toast.message}</span>
            <button className="toast-dismiss" onClick={() => dismiss(toast.id)} aria-label="Dismiss notification">
              <CloseIcon size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
