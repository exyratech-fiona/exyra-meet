"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 30_000, retry: 1 },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#1a1a2e",
            color: "#e8e8f0",
            border: "1px solid #2d2d5a",
            borderRadius: "12px",
            fontSize: "14px",
          },
          success: { iconTheme: { primary: "#22c55e", secondary: "#1a1a2e" } },
          error: { iconTheme: { primary: "#ef4444", secondary: "#1a1a2e" } },
        }}
      />
    </QueryClientProvider>
  );
}
