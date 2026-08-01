"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import { apiFetch } from "@/lib/api";
import { Temple } from "@/lib/types";

export default function ContactPage() {
  const [temples, setTemples] = useState<Temple[]>([]);

  useEffect(() => {
    apiFetch<Temple[]>("/api/temples")
      .then(setTemples)
      .catch(() => setTemples([]));
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />

      <section className="mx-auto max-w-6xl px-6 pb-16">
        <div className="mt-8 rounded-[2rem] bg-gradient-to-r from-orange-800 to-amber-500 p-8 text-white shadow-xl">
          <p className="font-black uppercase tracking-[0.3em] text-orange-100">
            Help & Authorities
          </p>

          <h1 className="mt-3 text-4xl font-black">
            Contact Temple Authorities
          </h1>

          <p className="mt-3 max-w-2xl text-orange-50">
            Find control room, emergency, SeniorSathi, and kiosk support details.
          </p>
        </div>

        <div className="mt-8 grid gap-5 md:grid-cols-2">
          {temples.map((temple) => (
            <div key={temple.id} className="card p-6">
              <h2 className="text-2xl font-black text-temple">
                {temple.name}
              </h2>

              <p className="mt-1 text-gray-600">{temple.city}, Gujarat</p>

              <div className="mt-5 space-y-3 text-sm">
                <div className="rounded-2xl bg-orange-50 p-4">
                  <b>Temple Control Room</b>
                  <p className="mt-1">Crowd, route, and gate guidance.</p>
                  <p className="mt-1 font-black text-orange-700">
                    Helpline: {(temple as any).emergency_contact || "108"}
                  </p>
                </div>

                <div className="rounded-2xl bg-white p-4 shadow-sm">
                  <b>SeniorSathi Desk</b>
                  <p className="mt-1">
                    Priority help for seniors and differently-abled pilgrims.
                  </p>
                  <p className="mt-1 font-black text-orange-700">
                    Available near SeniorSathi Gate
                  </p>
                </div>

                <div className="rounded-2xl bg-white p-4 shadow-sm">
                  <b>Offline Booking Kiosk</b>
                  <p className="mt-1">
                    For pilgrims without phone or internet access.
                  </p>
                  <p className="mt-1 font-black text-orange-700">
                    Ask for printed QR ticket at helpdesk.
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
