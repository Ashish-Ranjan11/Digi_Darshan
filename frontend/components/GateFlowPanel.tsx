"use client";

import { useEffect, useState } from "react";
import { apiFetch, formatDate } from "@/lib/api";

type GateCount = {
  gate: string;
  check_ins: number;
  check_outs: number;
  net_flow: number;
};

type ScannerLog = {
  id: number;
  ticket_code: string;
  action: string;
  gate: string;
  status: string;
  message?: string;
  created_at: string;
};

type GateFlowStats = {
  temple_id: number;
  temple_name: string;
  city: string;
  current_occupancy: number;
  max_capacity: number;
  occupancy_percent: number;
  crowd_level: string;
  total_checkins_today: number;
  total_checkouts_today: number;
  net_flow_today: number;
  gate_counts: GateCount[];
  recent_logs: ScannerLog[];
  generated_at: string;
};

function levelClass(level: string) {
  if (level === "critical") return "border-red-200 bg-red-50 text-red-700";
  if (level === "high") return "border-orange-200 bg-orange-50 text-orange-700";
  if (level === "medium") return "border-yellow-200 bg-yellow-50 text-yellow-700";
  return "border-green-200 bg-green-50 text-green-700";
}

function statusClass(status: string) {
  if (status === "success") return "bg-green-100 text-green-700";
  return "bg-red-100 text-red-700";
}

export default function GateFlowPanel({
  templeId,
  refreshKey = 0,
}: {
  templeId: number;
  refreshKey?: number;
}) {
  const [stats, setStats] = useState<GateFlowStats | null>(null);
  const [message, setMessage] = useState("");

  async function loadStats() {
    try {
      const data = await apiFetch<GateFlowStats>(
        `/api/scanner/gate-flow/${templeId}`
      );
      setStats(data);
    } catch (err: any) {
      setMessage(err.message || "Unable to load gate flow data");
    }
  }

  useEffect(() => {
    loadStats().catch(console.error);

    const interval = setInterval(() => {
      loadStats().catch(console.error);
    }, 5000);

    return () => clearInterval(interval);
  }, [templeId, refreshKey]);

  return (
    <div className="space-y-5">
      <div className="card p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-black uppercase tracking-widest text-orange-600">
              Gate-Level Flow System
            </p>

            <h2 className="mt-1 text-2xl font-black text-temple">
              {stats?.temple_name || "Temple Gate Flow"}
            </h2>

            <p className="mt-1 text-sm text-gray-600">
              Real scanner activity converted into live crowd data.
            </p>
          </div>

          <span
            className={`rounded-full border px-4 py-2 text-xs font-black uppercase ${levelClass(
              stats?.crowd_level || "low"
            )}`}
          >
            {stats?.crowd_level || "low"}
          </span>
        </div>

        {message ? (
          <p className="mt-5 rounded-2xl bg-red-50 p-3 text-sm font-bold text-red-700">
            {message}
          </p>
        ) : null}

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-3xl border border-orange-100 bg-orange-50 p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Occupancy
            </p>
            <p className="mt-2 text-3xl font-black text-temple">
              {stats?.current_occupancy ?? 0}
            </p>
            <p className="text-sm text-gray-500">
              {stats?.occupancy_percent ?? 0}% of capacity
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 bg-white p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Check-ins Today
            </p>
            <p className="mt-2 text-3xl font-black text-temple">
              {stats?.total_checkins_today ?? 0}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 bg-white p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Check-outs Today
            </p>
            <p className="mt-2 text-3xl font-black text-temple">
              {stats?.total_checkouts_today ?? 0}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 bg-white p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Net Flow Today
            </p>
            <p className="mt-2 text-3xl font-black text-temple">
              {stats?.net_flow_today ?? 0}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {stats?.gate_counts?.length ? (
            stats.gate_counts.map((gate) => (
              <div
                key={gate.gate}
                className="rounded-3xl border border-orange-100 p-4"
              >
                <h3 className="font-black text-temple">{gate.gate}</h3>

                <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
                  <p className="rounded-2xl bg-green-50 p-3 font-bold text-green-700">
                    In: {gate.check_ins}
                  </p>

                  <p className="rounded-2xl bg-red-50 p-3 font-bold text-red-700">
                    Out: {gate.check_outs}
                  </p>

                  <p className="rounded-2xl bg-orange-50 p-3 font-bold text-orange-700">
                    Net: {gate.net_flow}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p className="rounded-3xl bg-orange-50 p-4 text-sm font-semibold text-orange-800">
              No gate events yet. Scan a ticket to generate real flow data.
            </p>
          )}
        </div>

        <p className="mt-5 text-xs text-gray-500">
          Last updated: {stats?.generated_at ? formatDate(stats.generated_at) : "-"}
        </p>
      </div>

      <div className="card p-6">
        <h3 className="text-xl font-black text-temple">Recent Scanner Logs</h3>

        <div className="mt-5 space-y-3">
          {stats?.recent_logs?.length ? (
            stats.recent_logs.map((log) => (
              <div
                key={log.id}
                className="rounded-2xl border border-orange-100 p-4 text-sm"
              >
                <div className="flex items-center justify-between gap-3">
                  <b className="font-mono text-temple">{log.ticket_code}</b>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-black uppercase ${statusClass(
                      log.status
                    )}`}
                  >
                    {log.status}
                  </span>
                </div>

                <p className="mt-1 text-gray-600">
                  {log.action} • {log.gate}
                </p>

                <p className="mt-1 text-xs text-gray-500">
                  {log.message} • {formatDate(log.created_at)}
                </p>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No scanner logs yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
