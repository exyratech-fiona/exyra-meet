import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "@/types";
import Cookies from "js-cookie";

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setAuth: (user, token) => {
        Cookies.set("token", token, { expires: 1 });
        localStorage.setItem("token", token);
        set({ user, token });
      },
      logout: () => {
        Cookies.remove("token");
        localStorage.removeItem("token");
        set({ user: null, token: null });
        window.location.href = "/auth/login";
      },
    }),
    { name: "exyra-auth" }
  )
);
