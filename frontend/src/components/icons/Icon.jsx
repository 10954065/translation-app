const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

function Svg({ size = 18, children, ...rest }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" {...base} {...rest}>
      {children}
    </svg>
  );
}

export function SendIcon(props) {
  return (
    <Svg {...props}>
      <path d="M4 12 20 4l-6 16-3-7-7-1Z" />
    </Svg>
  );
}

export function PaperclipIcon(props) {
  return (
    <Svg {...props}>
      <path d="M18.5 10.5 11 18a4 4 0 0 1-5.6-5.6l8-8a2.7 2.7 0 0 1 3.8 3.8l-7.9 7.9a1.3 1.3 0 0 1-1.9-1.9l7.1-7.1" />
    </Svg>
  );
}

export function CopyIcon(props) {
  return (
    <Svg {...props}>
      <rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2.5" />
      <path d="M15.5 8.5V6.5A2 2 0 0 0 13.5 4.5h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" />
    </Svg>
  );
}

export function CheckIcon(props) {
  return (
    <Svg {...props}>
      <path d="m4 12.5 5 5L20 6.5" />
    </Svg>
  );
}

export function UsersIcon(props) {
  return (
    <Svg {...props}>
      <circle cx="9" cy="8" r="3.25" />
      <path d="M2.75 19a6.25 6.25 0 0 1 12.5 0" />
      <path d="M16 5.5c1.6.4 2.75 1.86 2.75 3.5 0 1.64-1.15 3.1-2.75 3.5" />
      <path d="M18.5 14.5c2 .6 3.5 2.4 3.5 4.5" />
    </Svg>
  );
}

export function CloseIcon(props) {
  return (
    <Svg {...props}>
      <path d="m5 5 14 14M19 5 5 19" />
    </Svg>
  );
}

export function ChevronDownIcon(props) {
  return (
    <Svg {...props}>
      <path d="m5 8.5 7 7 7-7" />
    </Svg>
  );
}

export function AlertIcon(props) {
  return (
    <Svg {...props}>
      <path d="M12 3.5 21.5 20h-19L12 3.5Z" />
      <path d="M12 10v4.2" />
      <circle cx="12" cy="17.3" r="0.15" fill="currentColor" stroke="none" />
    </Svg>
  );
}

export function GlobeIcon(props) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3c2.6 2.6 4 6 4 9s-1.4 6.4-4 9c-2.6-2.6-4-6-4-9s1.4-6.4 4-9Z" />
    </Svg>
  );
}

export function LoaderIcon(props) {
  return (
    <Svg {...props} className={`icon-spin ${props.className || ""}`}>
      <path d="M12 3v3.2M12 17.8V21M5.6 5.6l2.3 2.3M16.1 16.1l2.3 2.3M3 12h3.2M17.8 12H21M5.6 18.4l2.3-2.3M16.1 7.9l2.3-2.3" />
    </Svg>
  );
}

export function ArrowRightIcon(props) {
  return (
    <Svg {...props}>
      <path d="M4.5 12h15M13 5.5l6.5 6.5-6.5 6.5" />
    </Svg>
  );
}

export function DownloadIcon(props) {
  return (
    <Svg {...props}>
      <path d="M12 3.5v11.5M7 10.5l5 5 5-5" />
      <path d="M4.5 18v1.5A1.5 1.5 0 0 0 6 21h12a1.5 1.5 0 0 0 1.5-1.5V18" />
    </Svg>
  );
}

export function FileTextIcon(props) {
  return (
    <Svg {...props}>
      <path d="M7 3.5h7l4 4V20a.75.75 0 0 1-.75.75H7A.75.75 0 0 1 6.25 20V4.25A.75.75 0 0 1 7 3.5Z" />
      <path d="M14 3.5V8h4" />
      <path d="M9 13h6M9 16.3h6" />
    </Svg>
  );
}

export function DoorExitIcon(props) {
  return (
    <Svg {...props}>
      <path d="M9 4H6.5A1.5 1.5 0 0 0 5 5.5v13A1.5 1.5 0 0 0 6.5 20H9" />
      <path d="M14 12H21M18 8.5 21.5 12 18 15.5" />
      <path d="M9 4v16" />
    </Svg>
  );
}

export function TranslateArrowsIcon(props) {
  return (
    <Svg {...props}>
      <path d="M4 6h9M8.5 3.5v2.7M6 6c.2 3.5 2.2 6.2 5.5 7.7M11.5 6c-.5 2-1.6 3.7-3 5" />
      <path d="M13.5 20 18 10l4.5 10M14.7 17.3h6.6" />
    </Svg>
  );
}
