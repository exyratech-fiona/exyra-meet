import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: "indigo" | "green" | "yellow" | "purple" | "blue" | "red";
  trend?: { value: number; label: string };
}

const colors = {
  indigo: "bg-indigo-500/15 text-indigo-400",
  green: "bg-green-500/15 text-green-400",
  yellow: "bg-yellow-500/15 text-yellow-400",
  purple: "bg-purple-500/15 text-purple-400",
  blue: "bg-blue-500/15 text-blue-400",
  red: "bg-red-500/15 text-red-400",
};

export function StatCard({ title, value, subtitle, icon: Icon, color = "indigo", trend }: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="stat-card"
    >
      <div className="flex items-start justify-between">
        <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0", colors[color])}>
          <Icon size={18} />
        </div>
        {trend && (
          <span className={cn(
            "text-xs font-medium",
            trend.value >= 0 ? "text-green-400" : "text-red-400"
          )}>
            {trend.value >= 0 ? "+" : ""}{trend.value}%
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="text-3xl font-bold text-white">{value}</p>
        <p className="text-white/40 text-sm mt-0.5">{title}</p>
        {subtitle && <p className="text-white/25 text-xs mt-1">{subtitle}</p>}
      </div>
    </motion.div>
  );
}
