"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { useAuthStore } from "@/lib/store";
import { motion } from "framer-motion";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, token } = useAuthStore();

  useEffect(() => {
    if (!user || !token) {
      router.replace("/auth/login");
    }
  }, [user, token, router]);

  if (!user) return null;

  return (
    <div className="flex min-h-screen bg-[#080818]">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="p-8"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
