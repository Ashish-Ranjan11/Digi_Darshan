"use client";

import { useEffect, useRef, useState } from "react";
import { apiFetch, formatDate, WS_URL } from "@/lib/api";

type LiveCrowdPayload = {
  type: string;
  temple_id: number;
  temple_name: string;
  city: string;
  source: string;
  occupancy: number;
  max_capacity: number;
  occupancy_percent: number;
  inflow_per_min: number;
  outflow_per_min: number;
  net_flow_per_min: number;
  density_score: number;
  crowd_level: string;
  trend: string;
  recommendation: string;
  entry_gate_status: string;
  exit_gate_status: string;
  recommended_gate_action: string;
  notes?: string;
  timestamp: string;
};

function levelStyle(level?: string) {
  if (level === "critical") return "bg-red-100 text-red-700 border-red-200";
  if (level === "high") return "bg-orange-100 text-orange-700 border-orange-200";
  if (level === "medium") return "bg-yellow-100 text-yellow-700 border-yellow-200";
  return "bg-green-100 text-green-700 border-green-200";
}

export default function LiveCrowdPanel({ templeId }: { templeId: number }) {
  const [live, setLive] = useState<LiveCrowdPayload | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [socketStatus, setSocketStatus] = useState("connecting");

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function loadCurrent() {
    const data = await apiFetch<LiveCrowdPayload>(`/api/crowd/live/${templeId}`);
    setLive(data);
  }

  async function simulateOnce() {
    const data = await apiFetch<LiveCrowdPayload>(
      `/api/crowd/simulate/${templeId}`,
      {
        method: "POST",
      }
    );

    setLive(data);
  }

  function startSimulation() {
    setIsSimulating(true);

    simulateOnce().catch(console.error);

    intervalRef.current = setInterval(() => {
      simulateOnce().catch(console.error);
    }, 3000);
  }

  function stopSimulation() {
    setIsSimulating(false);

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  useEffect(() => {
    loadCurrent().catch(console.error);

    const ws = new WebSocket(`${WS_URL}/ws/temples/${templeId}`);

    ws.onopen = () => {
      setSocketStatus("connected");
      ws.send("admin-live-panel-connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "crowd_update") {
        setLive(data);
      }
    };

    ws.onerror = () => {
      setSocketStatus("error");
    };

    ws.onclose = () => {
      setSocketStatus("closed");
    };

    return () => {
      ws.close();

      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [templeId]);

  const percent = live?.occupancy_percent ?? 0;

  return (
    <div className="card p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-black uppercase tracking-widest text-orange-600">
            Real-Time Crowd Engine
          </p>

          <h2 className="mt-1 text-2xl font-black text-temple">
            {live?.temple_name || "Live Temple Monitor"}
          </h2>

          <p className="mt-1 text-sm text-gray-600">
            WebSocket: <b>{socketStatus}</b> • Source:{" "}
            <b>{live?.source || "waiting"}</b>
          </p>
        </div>

        <div className="flex gap-2">
          {!isSimulating ? (
            <button onClick={startSimulation} className="btn-primary">
              Start Live Simulation
            </button>
          ) : (
            <button onClick={stopSimulation} className="btn-secondary">
              Stop Simulation
            </button>
          )}
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <div className="rounded-3xl border border-orange-100 bg-orange-50 p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Occupancy
          </p>
          <p className="mt-2 text-3xl font-black text-temple">
            {live?.occupancy ?? 0}
          </p>
          <p className="text-sm text-gray-500">
            of {live?.max_capacity ?? 0}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Inflow/min
          </p>
          <p className="mt-2 text-3xl font-black text-temple">
            {live?.inflow_per_min ?? 0}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Outflow/min
          </p>
          <p className="mt-2 text-3xl font-black text-temple">
            {live?.outflow_per_min ?? 0}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">Density</p>
          <p className="mt-2 text-3xl font-black text-temple">
            {live?.density_score ?? 0}
          </p>
        </div>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-bold text-gray-700">
            Crowd capacity usage
          </p>

          <span
            className={`rounded-full border px-3 py-1 text-xs font-black uppercase ${levelStyle(
              live?.crowd_level
            )}`}
          >
            {live?.crowd_level || "low"}
          </span>
        </div>

        <div className="mt-3 h-4 rounded-full bg-orange-100">
          <div
            className="h-4 rounded-full bg-orange-600 transition-all"
            style={{ width: `${Math.min(percent, 100)}%` }}
          />
        </div>

        <p className="mt-2 text-sm text-gray-600">{percent}% occupied</p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-3xl border border-orange-100 p-5">
          <p className="text-xs font-black uppercase text-orange-600">
            Recommended Action
          </p>

          <p className="mt-2 text-sm font-semibold text-gray-700">
            {live?.recommendation || "Waiting for live reading..."}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 p-5">
          <p className="text-xs font-black uppercase text-orange-600">
            Gate Control
          </p>

          <p className="mt-2 text-sm text-gray-700">
            Entry: <b>{live?.entry_gate_status || "-"}</b>
          </p>

          <p className="text-sm text-gray-700">
            Exit: <b>{live?.exit_gate_status || "-"}</b>
          </p>

          <p className="mt-2 text-sm font-semibold text-gray-700">
            {live?.recommended_gate_action || "No gate instruction yet."}
          </p>
        </div>
      </div>

      <div className="mt-5 rounded-3xl bg-gray-900 p-4 text-xs text-orange-100">
        <p className="font-bold text-white">Latest live event</p>

        <p className="mt-1">
          Trend: {live?.trend || "-"} • Net flow/min:{" "}
          {live?.net_flow_per_min ?? 0}
        </p>

        <p className="mt-1">
          Updated: {live?.timestamp ? formatDate(live.timestamp) : "-"}
        </p>
      </div>
    </div>
  );
}