"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import { getStoredUser, getToken, routeForRole } from "@/lib/api";

function canAccess(role?: string) {
  return role === "kiosk_operator" || role === "admin" || role === "super_admin" || role === "temple_admin";
}

export default function KioskPage() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = getToken();
    const storedUser = getStoredUser();

    if (!token || !storedUser) {
      window.location.replace("/login");
      return;
    }

    if (!canAccess(storedUser.role)) {
      window.location.replace(routeForRole(storedUser.role));
      return;
    }

    setUser(storedUser);
  }, []);

  if (!user) {
    return <main className="grid min-h-screen place-items-center bg-black text-white">Opening kiosk...</main>;
  }

  return (
    <main className="min-h-screen bg-[#050301] text-white">
      <Nav />
      <section className="px-6 pb-20 pt-36">
        <div className="mx-auto max-w-6xl rounded-[2.5rem] border border-white/12 bg-white/[0.06] p-8 shadow-2xl backdrop-blur-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[#d6c4a6]">Kiosk Operator Portal</p>
          <h1 className="mt-5 font-serif text-5xl font-semibold text-[#fff4dd] md:text-7xl">Offline QR Ticketing</h1>
          <p className="mt-5 max-w-3xl text-white/65">
            Logged in as {user.name}. Generate QR passes for walk-in pilgrims and offline counters.
          </p>
          <div className="mt-10 rounded-3xl border border-white/10 bg-black/35 p-6">
            <h2 className="text-2xl font-semibold">Kiosk module active</h2>
            <p className="mt-3 text-white/60">Offline ticket form can be connected here.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
