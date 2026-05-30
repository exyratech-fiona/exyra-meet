import { cn, getStatusColor } from "@/lib/utils";

interface BadgeProps {
  status: string;
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: BadgeProps) {
  return (
    <span className={cn("badge", getStatusColor(status), className)}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-80" />
      {label || status}
    </span>
  );
}

export function Badge({ children, variant = "default", className }: {
  children: React.ReactNode;
  variant?: "default" | "primary" | "success" | "warning" | "danger";
  className?: string;
}) {
  const variants = {
    default: "bg-white/10 text-white/60 border-white/10",
    primary: "bg-indigo-500/20 text-indigo-300 border-indigo-500/20",
    success: "bg-green-500/20 text-green-400 border-green-500/20",
    warning: "bg-yellow-500/20 text-yellow-400 border-yellow-500/20",
    danger: "bg-red-500/20 text-red-400 border-red-500/20",
  };
  return (
    <span className={cn("badge", variants[variant], className)}>
      {children}
    </span>
  );
}
