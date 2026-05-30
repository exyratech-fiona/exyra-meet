"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard, Users, BookOpen, Calendar,
  Bell, ClipboardList, Settings, LogOut, Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/lib/store";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/batches", icon: BookOpen, label: "Batches" },
  { href: "/students", icon: Users, label: "Students" },
  { href: "/schedule", icon: Calendar, label: "Schedule" },
  { href: "/notifications", icon: Bell, label: "Notifications" },
  { href: "/attendance", icon: ClipboardList, label: "Attendance" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-[#0c0c1d] border-r border-white/5 flex flex-col z-40">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-white/5">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-glow">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-base leading-tight">Exyra</p>
            <p className="text-white/30 text-[10px] uppercase tracking-widest">Technologies</p>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link key={href} href={href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                  active
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/20"
                    : "text-white/50 hover:text-white/80 hover:bg-white/5"
                )}
              >
                <Icon size={16} className={active ? "text-indigo-400" : ""} />
                {label}
                {active && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="px-3 py-4 border-t border-white/5">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
            {user?.full_name?.[0]?.toUpperCase() || "A"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-xs font-medium truncate">{user?.full_name || "Admin"}</p>
            <p className="text-white/30 text-[10px] capitalize">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="text-white/30 hover:text-red-400 transition-colors"
            title="Logout"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
}
