"use client";

import { useEffect, useState } from "react";

function getStoredUser() {
  if (typeof window === "undefined") return null;

  const raw =
    localStorage.getItem("dd_user") ||
    localStorage.getItem("user") ||
    localStorage.getItem("digidarshan_user");

  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function getToken() {
  if (typeof window === "undefined") return null;

  return (
    localStorage.getItem("dd_token") ||
    localStorage.getItem("token") ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("digidarshan_token")
  );
}

function cleanRole(role?: string) {
  return String(role || "pilgrim")
    .replace("UserRole.", "")
    .replace("Role.", "")
    .trim()
    .toLowerCase();
}

function routeForRole(role?: string) {
  const r = cleanRole(role);

  if (
    r === "admin" ||
    r === "super_admin" ||
    r === "temple_admin" ||
    r === "emergency_operator"
  ) {
    return "/admin";
  }

  if (r === "scanner") return "/scanner";
  if (r === "kiosk_operator") return "/kiosk";
  if (r === "senior_sathi_volunteer") return "/senior-sathi";
  if (r === "vip_coordinator") return "/vip";

  return "/dashboard";
}

export default function RoleRouterPage() {
  const [message, setMessage] = useState("Checking role...");

  useEffect(() => {
    const token = getToken();
    const user = getStoredUser();

    if (!token || !user) {
      setMessage("No session found. Returning to login...");
      setTimeout(() => {
        window.location.replace("/login");
      }, 600);
      return;
    }

    const nextPath = routeForRole(user.role);

    setMessage(`Role detected: ${user.role}. Opening ${nextPath}...`);

    setTimeout(() => {
      window.location.replace(nextPath);
    }, 700);
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
