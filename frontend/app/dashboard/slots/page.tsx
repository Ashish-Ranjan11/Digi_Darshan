"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import PilgrimCrowdStatusPanel from "@/components/PilgrimCrowdStatusPanel";
import { apiFetch, formatDate } from "@/lib/api";
import { Temple } from "@/lib/types";

type Slot = {
  id: number;
  temple_id: number;
  start_time: string;
  end_time: string;
  capacity: number;
  booked_count: number;
  available_capacity?: number;
  available_count?: number;
};

function getAvailable(slot: Slot) {
  if (typeof slot.available_capacity === "number") return slot.available_capacity;
  if (typeof slot.available_count === "number") return slot.available_count;
  return Math.max(slot.capacity - slot.booked_count, 0);
}

export default function SlotsPage() {
  const [temples, setTemples] = useState<Temple[]>([]);
  const [templeId, setTempleId] = useState<number | null>(null);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [message, setMessage] = useState("");

  async function loadSlots(id: number) {
    const data = await apiFetch<Slot[]>(`/api/slots/temple/${id}`);
    setSlots(data);
  }

  async function loadTemples() {
    const data = await apiFetch<Temple[]>("/api/temples");
    setTemples(data);

    if (data[0]) {
      setTempleId(data[0].id);
      await loadSlots(data[0].id);
    }
  }

  useEffect(() => {
    loadTemples().catch(() => {
      setMessage("Unable to load slots. Please check backend.");
    });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />

      <section className="mx-auto max-w-6xl px-6 pb-16">
        <div className="mt-8 rounded-[2rem] bg-gradient-to-r from-orange-800 to-amber-500 p-8 text-white shadow-xl">
          <p className="font-black uppercase tracking-[0.3em] text-orange-100">
            Slots & Crowd
          </p>

          <h1 className="mt-3 text-4xl font-black">
            Tomorrow Slots and Live Rush
          </h1>

          <p className="mt-3 max-w-2xl text-orange-50">
            Choose temple, check live crowd pressure, and see available darshan
            slots.
          </p>
        </div>

        {message ? (
          <div className="mt-6 rounded-2xl bg-red-50 p-4 text-sm font-bold text-red-700">
            {message}
          </div>
        ) : null}

        <div className="mt-8 card p-6">
          <label className="text-sm font-bold text-gray-700">
            Select Temple
          </label>

          <select
            className="input mt-2"
            value={templeId || ""}
            onChange={(event) => {
              const id = Number(event.target.value);
              setTempleId(id);
              loadSlots(id).catch(() => setMessage("Unable to load slots."));
            }}
          >
            {temples.map((temple) => (
              <option key={temple.id} value={temple.id}>
                {temple.name} - {temple.city}
              </option>
            ))}
          </select>
        </div>

        {templeId ? (
          <div className="mt-6">
            <PilgrimCrowdStatusPanel templeId={templeId} />
          </div>
        ) : null}

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {slots.map((slot) => (
            <div key={slot.id} className="card p-5">
              <p className="text-lg font-black text-temple">
                {formatDate(slot.start_time)} - {formatDate(slot.end_time)}
              </p>

              <p className="mt-2 text-sm text-gray-600">
                Booked: {slot.booked_count}/{slot.capacity}
              </p>

              <p className="mt-2 text-2xl font-black text-orange-700">
                {getAvailable(slot)} seats left
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

