import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDateTime(dateStr: string, fmt = "dd MMM yyyy, hh:mm a") {
  try {
    return format(parseISO(dateStr), fmt);
  } catch {
    return dateStr;
  }
}

export function formatRelative(dateStr: string) {
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function getStatusColor(status: string) {
  const map: Record<string, string> = {
    active: "bg-green-500/20 text-green-400 border-green-500/30",
    scheduled: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    ongoing: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    completed: "bg-gray-500/20 text-gray-400 border-gray-500/30",
    cancelled: "bg-red-500/20 text-red-400 border-red-500/30",
    rescheduled: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    paused: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    inactive: "bg-gray-500/20 text-gray-400 border-gray-500/30",
    sent: "bg-green-500/20 text-green-400 border-green-500/30",
    failed: "bg-red-500/20 text-red-400 border-red-500/30",
    pending: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    present: "bg-green-500/20 text-green-400 border-green-500/30",
    absent: "bg-red-500/20 text-red-400 border-red-500/30",
    late: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  };
  return map[status] || "bg-gray-500/20 text-gray-400 border-gray-500/30";
}

export function getInitials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export const WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export const BATCH_COLORS = [
  "#6366f1", "#8b5cf6", "#ec4899", "#f59e0b",
  "#10b981", "#3b82f6", "#ef4444", "#06b6d4",
];

export const TIMEZONES = [
  "Asia/Kolkata",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Paris",
  "Asia/Dubai",
  "Asia/Singapore",
  "Australia/Sydney",
];
