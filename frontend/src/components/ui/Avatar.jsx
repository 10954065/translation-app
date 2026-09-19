import { avatarColor, initials } from "../../lib/avatarColor";

export function Avatar({ name, size = 36 }) {
  return (
    <span
      className="avatar"
      style={{ "--avatar-color": avatarColor(name || "?"), width: size, height: size, fontSize: size * 0.4 }}
      title={name}
    >
      {initials(name || "?")}
    </span>
  );
}
