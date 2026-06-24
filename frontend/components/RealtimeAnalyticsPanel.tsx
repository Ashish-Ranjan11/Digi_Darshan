"use client";

import { useEffect, useState } from "react";
import { apiFetch, formatDate } from "@/lib/api";

type Anomaly = {
  type: string;
  severity: string;
  title: string;
  message: string;
};

type Intervention = {
  priority: string;
  primary_action: string;
  secondary_action: string;
  message: string;
  recommended_command: string;
};

type RealtimeAnalysis = {
  temple_id: number;
  temple_name: string;
  city: string;
  window_minutes: number;
  readings_count: number;
  current_occupancy: number;
  max_capacity: number;
  current_occupancy_percent: number;
  average_occupancy: number;
  average_occupancy_percent: number;
  peak_occupancy: number;
  peak_occupancy_percent: number;
  average_inflow_per_min: number;
  average_outflow_per_min: number;
  net_flow_per_min: number;
  growth_rate_percent: number;
  average_density_score: number;
  risk_level: string;
  risk_score: number;
  trend: string;
  system_stability_score: number;
  anomalies: Anomaly[];
  recommended_intervention: Intervention;
  generated_at: string;
};

function riskClass(level: string) {
  if (level === "critical") return "border-red-200 bg-red-50 text-red-700";
  if (level === "high") return "border-orange-200 bg-orange-50 text-orange-700";
  if (level === "medium") return "border-yellow-200 bg-yellow-50 text-yellow-700";
  return "border-green-200 bg-green-50 text-green-700";
}

function stabilityLabel(score: number) {
  if (score >= 80) return "Stable";
  if (score >= 60) return "Watch";
  if (score >= 40) return "Unstable";
  return "Critical";
}

export default function RealtimeAnalyticsPanel({
  templeId,
}: {
  templeId: number;
}) {
  const [analysis, setAnalysis] = useState<RealtimeAnalysis | null>(null);
  const [windowMinutes, setWindowMinutes] = useState(30);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadAnalysis(minutes = windowMinutes) {
    setLoading(true);
    setMessage("");

    try {
      const data = await apiFetch<RealtimeAnalysis>(
        `/api/analytics/realtime/${templeId}?window_minutes=${minutes}`
      );
      setAnalysis(data);
    } catch (err: any) {
      setMessage(err.message || "Unable to load real-time analytics");
    } finally {
      setLoading(false);
    }
  }

  function changeWindow(minutes: number) {
    setWindowMinutes(minutes);
    loadAnalysis(minutes).catch(console.error);
  }

  useEffect(() => {
    loadAnalysis().catch(console.error);
  }, [templeId]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadAnalysis().catch(console.error);
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh, templeId, windowMinutes]);

  const stability = analysis?.system_stability_score ?? 0;

  return (
    <div className="card p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-black uppercase tracking-widest text-orange-600">
            Real-Time Data Analysis Core
          </p>

          <h2 className="mt-1 text-2xl font-black text-temple">
            Stability, Trends & Anomaly Detection
          </h2>

          <p className="mt-1 text-sm text-gray-600">
            Analyzes live readings across time windows to detect spikes, flow
            imbalance, density risk, and system stability.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {[5, 15, 30, 60].map((minutes) => (
            <button
              key={minutes}
              onClick={() => changeWindow(minutes)}
              className={
                windowMinutes === minutes ? "btn-primary" : "btn-secondary"
              }
            >
              {minutes}m
            </button>
          ))}

          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className="btn-secondary"
          >
            {autoRefresh ? "Auto ON" : "Auto OFF"}
          </button>

          <button
            onClick={() => loadAnalysis().catch(console.error)}
            className="btn-primary"
            disabled={loading}
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {message ? (
        <p className="mt-5 rounded-2xl bg-red-50 p-3 text-sm font-bold text-red-700">
          {message}
        </p>
      ) : null}

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <div className={`rounded-3xl border p-4 ${riskClass(analysis?.risk_level || "low")}`}>
          <p className="text-xs font-black uppercase">Risk Level</p>
          <p className="mt-2 text-2xl font-black uppercase">
            {analysis?.risk_level || "-"}
          </p>
          <p className="text-sm">Score {analysis?.risk_score ?? 0}/100</p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Stability
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {stabilityLabel(stability)}
          </p>
          <p className="text-sm text-gray-500">{stability}/100</p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Growth Rate
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {analysis?.growth_rate_percent ?? 0}%
          </p>
          <p className="text-sm text-gray-500">
            {analysis?.trend?.replace("_", " ") || "stable"}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Readings Used
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {analysis?.readings_count ?? 0}
          </p>
          <p className="text-sm text-gray-500">
            Last {analysis?.window_minutes ?? windowMinutes} minutes
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-3xl border border-orange-100 bg-orange-50 p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Current Occupancy
          </p>
          <p className="mt-2 text-3xl font-black text-temple">
            {analysis?.current_occupancy ?? 0}
          </p>
          <p className="text-sm text-gray-500">
            {analysis?.current_occupancy_percent ?? 0}% of capacity
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Average Occupancy
          </p>
          <p className="mt-2 text-3xl font-black text-temple">
            {analysis?.average_occupancy ?? 0}
          </p>
          <p className="text-sm text-gray-500">
            {analysis?.average_occupancy_percent ?? 0}% average
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-white p-4">
          <p className="text-xs font-black uppercase text-gray-500">
            Peak Occupancy
          </p>
          <p className="mt-2 text-3xl font-black text-temple">
            {analysis?.peak_occupancy ?? 0}
          </p>
          <p className="text-sm text-gray-500">
            {analysis?.peak_occupancy_percent ?? 0}% peak
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <div className="rounded-3xl border border-orange-100 p-4">
          <p className="text-xs font-black uppercase text-orange-600">
            Avg Inflow/min
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {analysis?.average_inflow_per_min ?? 0}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 p-4">
          <p className="text-xs font-black uppercase text-orange-600">
            Avg Outflow/min
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {analysis?.average_outflow_per_min ?? 0}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 p-4">
          <p className="text-xs font-black uppercase text-orange-600">
            Net Flow/min
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {analysis?.net_flow_per_min ?? 0}
          </p>
        </div>

        <div className="rounded-3xl border border-orange-100 p-4">
          <p className="text-xs font-black uppercase text-orange-600">
            Avg Density
          </p>
          <p className="mt-2 text-2xl font-black text-temple">
            {analysis?.average_density_score ?? 0}
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-3xl border border-orange-100 bg-gray-900 p-5 text-orange-50">
        <p className="text-xs font-black uppercase text-orange-300">
          Recommended Intervention
        </p>

        <h3 className="mt-2 text-xl font-black text-white">
          {analysis?.recommended_intervention?.primary_action ||
            "Continue Monitoring"}
        </h3>

        <p className="mt-2 text-sm">
          {analysis?.recommended_intervention?.message ||
            "Waiting for enough readings."}
        </p>

        <p className="mt-3 text-xs text-orange-200">
          Suggested command:{" "}
          <b>
            {analysis?.recommended_intervention?.recommended_command ||
              "resume_normal_flow"}
          </b>
        </p>
      </div>

      <div className="mt-6">
        <h3 className="text-xl font-black text-temple">Detected Anomalies</h3>

        <div className="mt-4 space-y-3">
          {analysis?.anomalies?.length ? (
            analysis.anomalies.map((anomaly) => (
              <div
                key={anomaly.type}
                className={`rounded-3xl border p-4 ${riskClass(
                  anomaly.severity
                )}`}
              >
                <p className="text-xs font-black uppercase">
                  {anomaly.severity}
                </p>
                <h4 className="mt-1 font-black">{anomaly.title}</h4>
                <p className="mt-1 text-sm font-semibold">
                  {anomaly.message}
                </p>
              </div>
            ))
          ) : (
            <p className="rounded-3xl border border-green-100 bg-green-50 p-4 text-sm font-bold text-green-700">
              No major anomaly detected in this time window.
            </p>
          )}
        </div>
      </div>

      <p className="mt-5 text-xs text-gray-500">
        Last analyzed:{" "}
        {analysis?.generated_at ? formatDate(analysis.generated_at) : "-"}
      </p>
    </div>
  );
}
