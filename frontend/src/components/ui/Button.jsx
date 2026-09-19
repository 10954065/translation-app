import { LoaderIcon } from "../icons/Icon";

export function Button({
  as: Component = "button",
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  icon = null,
  iconPosition = "left",
  className = "",
  children,
  ...rest
}) {
  const isDisabled = disabled || loading;
  return (
    <Component
      className={`btn btn-${variant} btn-${size} ${className}`.trim()}
      disabled={Component === "button" ? isDisabled : undefined}
      aria-disabled={isDisabled}
      {...rest}
    >
      {loading && <LoaderIcon size={16} />}
      {!loading && icon && iconPosition === "left" && icon}
      <span>{children}</span>
      {!loading && icon && iconPosition === "right" && icon}
    </Component>
  );
}
