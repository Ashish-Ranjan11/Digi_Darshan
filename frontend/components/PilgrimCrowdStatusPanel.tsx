"use client";

import { useEffect, useState } from "react";
import { apiFetch, formatDate, WS_URL } from "@/lib/api";

type LiveCrowdPayload = {
  temple_id: number;
  temple_name: string;
  city: string;
  occupancy: number;
  max_capacity: number;
  occupancy_percent: number;
  crowd_level: string;
  recommendation: string;
  timestamp: string;
};

function levelClass(level?: string) {
  if (level === "critical") return "border-red-200 bg-red-50 text-red-700";
  if (level === "high") return "border-orange-200 bg-orange-50 text-orange-700";
  if (level === "medium") return "border-yellow-200 bg-yellow-50 text-yellow-700";
  return "border-green-200 bg-green-50 text-green-700";
}

function pilgrimMessage(level?: string) {
  if (level === "critical") {
    return "Temple is heavily crowded right now. Please choose a later slot if possible.";
  }

  if (level === "high") {
    return "Crowd is high. Senior citizens and families should prefer a later low-density slot.";
  }

  if (level === "medium") {
    return "Moderate crowd at the temple. You can book, but arrive close to your selected slot.";
  }

  return "Crowd is low. This is a good time to book your darshan slot.";
}

export default function PilgrimCrowdStatusPanel({
  templeId,
}: {
  templeId: number;
}) {
  const [live, setLive] = useState<LiveCrowdPayload | null>(null);
  const [isUpdating, setIsUpdating] = useState(true);

  async function loadCurrent() {
    try {
      const data = await apiFetch<LiveCrowdPayload>(
        `/api/crowd/live/${templeId}`
      );

      setLive(data);
    } catch {
      // Do not show technical backend/API errors to pilgrims.
      setLive(null);
    } finally {
      setIsUpdating(false);
    }
  }

  useEffect(() => {
    setIsUpdating(true);
    loadCurrent().catch(console.error);

    const interval = setInterval(() => {
      loadCurrent().catch(console.error);
    }, 5000);

    const ws = new WebSocket(`${WS_URL}/ws/temples/${templeId}`);

    ws.onopen = () => {
      ws.send("pilgrim-live-crowd-view");
    };

    ws.onmessage = () => {
      loadCurrent().catch(console.error);
    };

    ws.onerror = () => {
      // Silent for pilgrim UI.
    };

    ws.onclose = () => {
      // Silent for pilgrim UI.
    };

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, [templeId]);

  const percent = live?.occupancy_percent ?? 0;
  const level = live?.crowd_level || "low";

  return (
    <div className="rounded-3xl border border-orange-100 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-black uppercase tracking-widest text-orange-600">
            Live Crowd Status
          </p>

          <h3 className="mt-1 text-xl font-black text-temple">
            {live?.temple_name || "Selected Temple"}
          </h3>

          <p className="mt-1 text-sm text-gray-600">
            Check crowd level before selecting your darshan slot.
          </p>
        </div>

        <span
          className={`rounded-full border px-4 py-2 text-xs font-black uppercase ${levelClass(
            level
          )}`}
        >
          {level}
        </span>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl bg-orange-50 p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Current Crowd
          </p>

          <p className="mt-2 text-2xl font-black text-temple">
            {live ? `${live.occupancy}/${live.max_capacity}` : "Updating..."}
          </p>
        </div>

        <div className="rounded-2xl bg-white p-4 shadow-sm">
          <p className="text-xs font-black uppercase text-gray-500">
            Capacity Used
          </p>

          <p className="mt-2 text-2xl font-black text-temple">
            {live ? `${percent}%` : "Updating..."}
          </p>
        </div>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between text-sm font-bold text-gray-700">
          <span>Crowd pressure</span>
          <span>{live ? `${percent}%` : "Updating"}</span>
        </div>

        <div className="mt-2 h-3 rounded-full bg-orange-100">
          <div
            className="h-3 rounded-full bg-orange-600 transition-all"
            style={{ width: `${Math.min(percent, 100)}%` }}
          />
        </div>
      </div>

      <div className="mt-5 rounded-3xl bg-gray-900 p-4 text-sm text-orange-100">
        <p className="font-bold text-white">Booking Guidance</p>

        <p className="mt-1">
          {isUpdating
            ? "Live crowd status is updating. You can still continue booking."
            : live?.recommendation || pilgrimMessage(level)}
        </p>

        <p className="mt-2 text-xs text-orange-200">
          Last updated: {live?.timestamp ? formatDate(live.timestamp) : "Just now"}
        </p>
      </div>
    </div>
  );
}