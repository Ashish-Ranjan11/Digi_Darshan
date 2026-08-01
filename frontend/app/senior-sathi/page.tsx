"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import { getStoredUser, getToken, routeForRole } from "@/lib/api";

function canAccess(role?: string) {
  return (
    role === "senior_sathi_volunteer" ||
    role === "admin" ||
    role === "super_admin" ||
    role === "temple_admin" ||
    role === "emergency_operator"
  );
}

export default function SeniorSathiPage() {
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
    return <main className="grid min-h-screen place-items-center bg-black text-white">Opening SeniorSathi...</main>;
  }

  return (
    <main className="min-h-screen bg-[#050301] text-white">
      <Nav />
      <section className="px-6 pb-20 pt-36">
        <div className="mx-auto max-w-6xl rounded-[2.5rem] border border-white/12 bg-white/[0.06] p-8 shadow-2xl backdrop-blur-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[#d6c4a6]">SeniorSathi Desk</p>
          <h1 className="mt-5 font-serif text-5xl font-semibold text-[#fff4dd] md:text-7xl">Assistance Workflow</h1>
          <p className="mt-5 max-w-3xl text-white/65">
            Logged in as {user.name}. Handle senior citizen and differently-abled pilgrim assistance.
          </p>
        </div>
      </section>
    </main>
  );
}
