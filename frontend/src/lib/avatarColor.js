const PALETTE = [
  "oklch(58% 0.16 25)",
  "oklch(58% 0.14 70)",
  "oklch(56% 0.14 140)",
  "oklch(55% 0.13 190)",
  "oklch(52% 0.19 288)",
  "oklch(55% 0.18 320)",
  "oklch(58% 0.15 15)",
  "oklch(54% 0.12 230)",
];

export function avatarColor(seed) {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return PALETTE[hash % PALETTE.length];
}

export function initials(name) {
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase() || "").join("") || "?";
}
