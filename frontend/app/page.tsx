"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";

export default function Home() {
  const router = useRouter();
  const { user } = useAuthStore();

  useEffect(() => {
    if (user) {
      router.replace("/dashboard");
    } else {
      router.replace("/auth/login");
    }
  }, [user, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#080818]">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center animate-pulse">
          <span className="text-white font-bold text-lg">E</span>
        </div>
        <p className="text-white/40 text-sm">Loading Exyra...</p>
      </div>
    </div>
  );
}
