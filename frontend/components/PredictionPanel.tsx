"use client";

import { useEffect, useState } from "react";

import CrowdHeatmap from "@/components/CrowdHeatmap";
import { apiFetch, formatDate } from "@/lib/api";

type ForecastItem = {
  minutes: number;
  predicted_occupancy: number;
  predicted_percent: number;
  risk: string;
  action: string;
};

type HeatmapZone = {
  zone: string;
  crowd_percent: number;
  level: string;
  role: string;
  advice: string;
};

type PredictionPayload = {
  temple_id: number;
  temple_name: string;
  city: string;
  festival_mode: boolean;
  current_occupancy: number;
  max_capacity: number;
  occupancy_percent: number;
  current_risk: string;
  inflow_per_min: number;
  outflow_per_min: number;
  net_flow_per_min: number;
  trend: string;
  forecast: ForecastItem[];
  heatmap: HeatmapZone[];
  highest_predicted_risk: string;
  recommended_action: string;
  safe_exit_route: string;
  parking_advice: string;
  generated_at: string;
};

function riskClass(risk: string) {
  if (risk === "critical") return "border-red-200 bg-red-50 text-red-700";
  if (risk === "high") return "border-orange-200 bg-orange-50 text-orange-700";
  if (risk === "medium") return "border-yellow-200 bg-yellow-50 text-yellow-700";
  return "border-green-200 bg-green-50 text-green-700";
}

export default function PredictionPanel({ templeId }: { templeId: number }) {
  const [prediction, setPrediction] = useState<PredictionPayload | null>(null);
  const [festivalMode, setFestivalMode] = useState(false);
  const [loading, setLoading] = useState(false);

  async function loadPrediction(nextFestivalMode = festivalMode) {
    setLoading(true);

    try {
      const data = await apiFetch<PredictionPayload>(
        `/api/prediction/${templeId}?festival_mode=${nextFestivalMode}`
      );

      setPrediction(data);
    } finally {
      setLoading(false);
    }
  }

  function toggleFestivalMode() {
    const next = !festivalMode;
    setFestivalMode(next);
    loadPrediction(next).catch(console.error);
  }

  useEffect(() => {
    loadPrediction().catch(console.error);
  }, [templeId]);

  return (
    <div className="space-y-5">
      <div className="card p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-black uppercase tracking-widest text-orange-600">
              AI Crowd Prediction
            </p>

            <h2 className="mt-1 text-2xl font-black text-temple">
              Predictive Crowd Intelligence
            </h2>

            <p className="mt-1 text-sm text-gray-600">
              Forecasts next 15, 30, and 60 minutes using live inflow/outflow
              readings.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => loadPrediction().catch(console.error)}
              className="btn-secondary"
              disabled={loading}
            >
              {loading ? "Refreshing..." : "Refresh Prediction"}
            </button>

            <button onClick={toggleFestivalMode} className="btn-primary">
              {festivalMode ? "Festival Mode ON" : "Festival Mode OFF"}
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-3xl border border-orange-100 bg-orange-50 p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Current Risk
            </p>
            <p className="mt-2 text-2xl font-black uppercase text-temple">
              {prediction?.current_risk || "-"}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 bg-white p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Highest Risk
            </p>
            <p className="mt-2 text-2xl font-black uppercase text-temple">
              {prediction?.highest_predicted_risk || "-"}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 bg-white p-4">
            <p className="text-xs font-black uppercase text-gray-500">Trend</p>
            <p className="mt-2 text-2xl font-black text-temple">
              {prediction?.trend?.replace("_", " ") || "-"}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 bg-white p-4">
            <p className="text-xs font-black uppercase text-gray-500">
              Net Flow/min
            </p>
            <p className="mt-2 text-2xl font-black text-temple">
              {prediction?.net_flow_per_min ?? 0}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {prediction?.forecast?.map((item) => (
            <div
              key={item.minutes}
              className={`rounded-3xl border p-5 ${riskClass(item.risk)}`}
            >
              <p className="text-xs font-black uppercase">
                After {item.minutes} minutes
              </p>

              <p className="mt-2 text-3xl font-black">
                {item.predicted_percent}%
              </p>

              <p className="text-sm font-semibold">
                {item.predicted_occupancy}/{prediction.max_capacity} pilgrims
              </p>

              <span className="mt-3 inline-flex rounded-full bg-white px-3 py-1 text-xs font-black uppercase">
                {item.risk}
              </span>

              <p className="mt-3 text-xs font-semibold">{item.action}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-3xl border border-orange-100 p-5">
            <p className="text-xs font-black uppercase text-orange-600">
              Recommended Action
            </p>
            <p className="mt-2 text-sm font-semibold text-gray-700">
              {prediction?.recommended_action || "Waiting for prediction..."}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 p-5">
            <p className="text-xs font-black uppercase text-orange-600">
              Safe Exit Route
            </p>
            <p className="mt-2 text-sm font-semibold text-gray-700">
              {prediction?.safe_exit_route || "Waiting for heatmap..."}
            </p>
          </div>

          <div className="rounded-3xl border border-orange-100 p-5">
            <p className="text-xs font-black uppercase text-orange-600">
              Parking Advice
            </p>
            <p className="mt-2 text-sm font-semibold text-gray-700">
              {prediction?.parking_advice || "Waiting for parking advice..."}
            </p>
          </div>
        </div>

        <p className="mt-5 text-xs text-gray-500">
          Last generated:{" "}
          {prediction?.generated_at ? formatDate(prediction.generated_at) : "-"}
        </p>
      </div>

      {prediction?.heatmap?.length ? (
        <CrowdHeatmap zones={prediction.heatmap} />
      ) : null}
    </div>
  );
}
