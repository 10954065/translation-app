const LABELS = {
  connected: "Connected",
  connecting: "Connecting…",
  reconnecting: "Reconnecting…",
  disconnected: "Disconnected",
};

export function ConnectionBadge({ status }) {
  return (
    <span className={`connection-badge connection-badge--${status}`} role="status">
      <span className="connection-dot" aria-hidden="true" />
      {LABELS[status] || status}
    </span>
  );
}
