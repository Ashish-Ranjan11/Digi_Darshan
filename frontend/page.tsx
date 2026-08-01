"use client";

import { useEffect, useState } from "react";
import { getStoredUser, getToken, routeForRole } from "@/lib/api";

export default function RoleRouterPage() {
  const [message, setMessage] = useState("Checking your role...");

  useEffect(() => {
    const token = getToken();
    const user = getStoredUser();

    if (!token || !user) {
      setMessage("No active session found. Redirecting to login...");
      setTimeout(() => {
        window.location.replace("/login");
      }, 600);
      return;
    }

    const nextRoute = routeForRole(user.role);

    setMessage(`Logged in as ${user.role}. Opening ${nextRoute}...`);

    setTimeout(() => {
      window.location.replace(nextRoute);
    }, 500);
  }, []);

  return (
    <main className="grid min-h-screen place-items-center bg-black px-6 text-white">
      <div className="rounded-[2rem] border border-white/15 bg-white/[0.08] p-8 text-center shadow-2xl backdrop-blur-xl">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[#d6c4a6]">
          Digii-Darshan
        </p>

        <h1 className="mt-4 text-3xl font-semibold">Routing Portal</h1>

        <p className="mt-4 text-white/70">{message}</p>
      </div>
    </main>
  );
}
