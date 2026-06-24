"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import ControlActionPanel from "@/components/ControlActionPanel";
import CrowdBadge from "@/components/CrowdBadge";
import LiveCrowdPanel from "@/components/LiveCrowdPanel";
import Nav from "@/components/Nav";
import PredictionPanel from "@/components/PredictionPanel";
import RealtimeAnalyticsPanel from "@/components/RealtimeAnalyticsPanel";
import StatCard from "@/components/StatCard";
import {
  apiFetch,
  clearSession,
  formatDate,
  getStoredUser,
  getToken,
} from "@/lib/api";
import { Alert, Temple, User } from "@/lib/types";

type Reading = {
  id: number;
  temple_id: number;
  occupancy: number;
  source: string;
  created_at: string;
  notes?: string;
};

type Overview = {
  temples: number;
  active_alerts: number;
  bookings_today: number;
  visitors_expected_today: number;
  total_current_occupancy: number;
  average_occupancy_percent: number;
  latest_readings: Reading[];
  active_alert_list: Alert[];
};

function localInputOffset(hours = 0) {
  const d = new Date(Date.now() + hours * 60 * 60 * 1000);
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}

export default function AdminPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [temples, setTemples] = useState<Temple[]>([]);
  const [selectedTempleId, setSelectedTempleId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  const [crowdForm, setCrowdForm] = useState({
    occupancy: 1000,
    inflow_per_min: 30,
    outflow_per_min: 20,
    density_score: 0.35,
    notes: "Manual control room update",
  });

  const [alertForm, setAlertForm] = useState({
    title: "High density near Gate A",
    message: "Please slow down movement near Gate A.",
    severity: "warning",
    location: "Gate A",
    instruction: "Follow volunteers and use Gate B alternate corridor.",
  });

  const [slotForm, setSlotForm] = useState({
    start_time: localInputOffset(1),
    end_time: localInputOffset(2),
    capacity: 250,
    senior_reserved_capacity: 40,
  });

  const selectedTemple = useMemo(
    () => temples.find((temple) => temple.id === selectedTempleId),
    [temples, selectedTempleId]
  );

  async function load() {
    const [overviewData, templeData] = await Promise.all([
      apiFetch<Overview>("/api/dashboard/overview"),
      apiFetch<Temple[]>("/api/temples"),
    ]);

    setOverview(overviewData);
    setTemples(templeData);

    if (!selectedTempleId && templeData[0]) {
      setSelectedTempleId(templeData[0].id);

      setCrowdForm((form) => ({
        ...form,
        occupancy: templeData[0].current_occupancy,
      }));
    }
  }

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }

    const stored = getStoredUser();
    setUser(stored);

    if (stored?.role === "pilgrim" || stored?.role === "scanner") {
      router.push("/dashboard");
      return;
    }

    load().catch((err) => setMessage(err.message));
  }, []);

  function handleTempleChange(id: number) {
    setSelectedTempleId(id);

    const temple = temples.find((item) => item.id === id);

    if (temple) {
      setCrowdForm((form) => ({
        ...form,
        occupancy: temple.current_occupancy,
      }));
    }
  }

  async function submitCrowd(event: FormEvent) {
    event.preventDefault();

    if (!selectedTempleId) return;

    setMessage("");

    try {
      await apiFetch("/api/crowd/readings", {
        method: "POST",
        body: JSON.stringify({
          temple_id: selectedTempleId,
          source: "manual",
          ...crowdForm,
        }),
      });

      setMessage("Crowd reading pushed to live dashboard.");
      await load();
    } catch (err: any) {
      setMessage(err.message || "Unable to update crowd reading");
    }
  }

  async function submitAlert(event: FormEvent) {
    event.preventDefault();

    if (!selectedTempleId) return;

    setMessage("");

    try {
      await apiFetch("/api/alerts", {
        method: "POST",
        body: JSON.stringify({
          temple_id: selectedTempleId,
          ...alertForm,
        }),
      });

      setMessage("Emergency alert broadcasted.");
      await load();
    } catch (err: any) {
      setMessage(err.message || "Unable to create alert");
    }
  }

  async function submitSlot(event: FormEvent) {
    event.preventDefault();

    if (!selectedTempleId) return;

    setMessage("");

    try {
      await apiFetch("/api/slots", {
        method: "POST",
        body: JSON.stringify({
          temple_id: selectedTempleId,
          start_time: new Date(slotForm.start_time).toISOString(),
          end_time: new Date(slotForm.end_time).toISOString(),
          capacity: Number(slotForm.capacity),
          senior_reserved_capacity: Number(slotForm.senior_reserved_capacity),
        }),
      });

      setMessage("New darshan slot created.");
      await load();
    } catch (err: any) {
      setMessage(err.message || "Unable to create slot");
    }
  }

  async function resolveAlert(alertId: number) {
    try {
      await apiFetch(`/api/alerts/${alertId}/resolve`, {
        method: "PATCH",
      });

      setMessage("Alert resolved.");
      await load();
    } catch (err: any) {
      setMessage(err.message || "Unable to resolve alert");
    }
  }

  function logout() {
    clearSession();
    router.push("/login");
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />

      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-black uppercase tracking-widest text-orange-600">
              Control Room
            </p>

            <h1 className="mt-2 text-4xl font-black text-temple">
              Digii-CrowdControl Dashboard
            </h1>

            <p className="mt-2 text-gray-600">
              Role: {user?.role || "admin"}. Manage live occupancy, real-time
              analytics, AI prediction, alerts, slots, and command actions.
            </p>
          </div>

          <button onClick={logout} className="btn-secondary">
            Logout
          </button>
        </div>

        <div className="grid gap-4 md:grid-cols-5">
          <StatCard label="Temples" value={overview?.temples ?? "-"} />

          <StatCard
            label="Active Alerts"
            value={overview?.active_alerts ?? "-"}
          />

          <StatCard
            label="Bookings Today"
            value={overview?.bookings_today ?? "-"}
          />

          <StatCard
            label="Visitors Expected"
            value={overview?.visitors_expected_today ?? "-"}
          />

          <StatCard
            label="Avg Occupancy"
            value={`${overview?.average_occupancy_percent ?? 0}%`}
          />
        </div>

        {message ? (
          <p className="mt-6 rounded-2xl bg-white p-4 text-sm font-bold text-orange-800 shadow">
            {message}
          </p>
        ) : null}

        <div className="mt-8 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="card p-6">
            <label className="text-sm font-bold text-gray-700">
              Select Temple
            </label>

            <select
              className="input mt-2"
              value={selectedTempleId || ""}
              onChange={(e) => handleTempleChange(Number(e.target.value))}
            >
              {temples.map((temple) => (
                <option key={temple.id} value={temple.id}>
                  {temple.name}
                </option>
              ))}
            </select>

            {selectedTemple ? (
              <div className="mt-6 rounded-3xl bg-orange-50 p-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-temple">
                      {selectedTemple.name}
                    </h2>

                    <p className="text-sm text-gray-600">
                      {selectedTemple.city}
                    </p>
                  </div>

                  <CrowdBadge level={selectedTemple.crowd_level} />
                </div>

                <div className="mt-5 h-3 rounded-full bg-white">
                  <div
                    className="h-3 rounded-full bg-orange-600"
                    style={{
                      width: `${Math.min(
                        selectedTemple.occupancy_percent,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <p className="mt-3 text-sm text-gray-600">
                  {selectedTemple.current_occupancy}/
                  {selectedTemple.max_capacity} pilgrims currently inside.
                </p>
              </div>
            ) : null}

            <form onSubmit={submitCrowd} className="mt-6">
              <h2 className="text-xl font-black text-temple">
                Manual Crowd Reading
              </h2>

              <div className="mt-5 grid gap-4">
                <input
                  className="input"
                  type="number"
                  value={crowdForm.occupancy}
                  onChange={(e) =>
                    setCrowdForm({
                      ...crowdForm,
                      occupancy: Number(e.target.value),
                    })
                  }
                  placeholder="Occupancy"
                />

                <input
                  className="input"
                  type="number"
                  value={crowdForm.inflow_per_min}
                  onChange={(e) =>
                    setCrowdForm({
                      ...crowdForm,
                      inflow_per_min: Number(e.target.value),
                    })
                  }
                  placeholder="Inflow per minute"
                />

                <input
                  className="input"
                  type="number"
                  value={crowdForm.outflow_per_min}
                  onChange={(e) =>
                    setCrowdForm({
                      ...crowdForm,
                      outflow_per_min: Number(e.target.value),
                    })
                  }
                  placeholder="Outflow per minute"
                />

                <input
                  className="input"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={crowdForm.density_score}
                  onChange={(e) =>
                    setCrowdForm({
                      ...crowdForm,
                      density_score: Number(e.target.value),
                    })
                  }
                  placeholder="Density score"
                />

                <input
                  className="input"
                  value={crowdForm.notes}
                  onChange={(e) =>
                    setCrowdForm({
                      ...crowdForm,
                      notes: e.target.value,
                    })
                  }
                  placeholder="Notes"
                />
              </div>

              <button className="btn-primary mt-5 w-full" type="submit">
                Push Manual Reading
              </button>
            </form>
          </div>

          <div className="space-y-5">
            {selectedTempleId ? (
              <>
                <LiveCrowdPanel templeId={selectedTempleId} />

                <RealtimeAnalyticsPanel templeId={selectedTempleId} />

                <PredictionPanel templeId={selectedTempleId} />

                <ControlActionPanel
                  templeId={selectedTempleId}
                  onActionDone={load}
                />
              </>
            ) : null}
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <form onSubmit={submitAlert} className="card p-6">
            <h2 className="text-2xl font-black text-temple">
              Broadcast Digii-Suraksha Alert
            </h2>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <input
                className="input"
                value={alertForm.title}
                onChange={(e) =>
                  setAlertForm({
                    ...alertForm,
                    title: e.target.value,
                  })
                }
                placeholder="Alert title"
              />

              <select
                className="input"
                value={alertForm.severity}
                onChange={(e) =>
                  setAlertForm({
                    ...alertForm,
                    severity: e.target.value,
                  })
                }
              >
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="critical">Critical</option>
              </select>

              <input
                className="input"
                value={alertForm.location}
                onChange={(e) =>
                  setAlertForm({
                    ...alertForm,
                    location: e.target.value,
                  })
                }
                placeholder="Location"
              />

              <input
                className="input"
                value={alertForm.instruction}
                onChange={(e) =>
                  setAlertForm({
                    ...alertForm,
                    instruction: e.target.value,
                  })
                }
                placeholder="Instruction"
              />

              <textarea
                className="input sm:col-span-2"
                value={alertForm.message}
                onChange={(e) =>
                  setAlertForm({
                    ...alertForm,
                    message: e.target.value,
                  })
                }
                placeholder="Message"
              />
            </div>

            <button className="btn-primary mt-5" type="submit">
              Broadcast Alert
            </button>
          </form>

          <form onSubmit={submitSlot} className="card p-6">
            <h2 className="text-2xl font-black text-temple">
              Create Darshan Time Slot
            </h2>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <input
                className="input"
                type="datetime-local"
                value={slotForm.start_time}
                onChange={(e) =>
                  setSlotForm({
                    ...slotForm,
                    start_time: e.target.value,
                  })
                }
              />

              <input
                className="input"
                type="datetime-local"
                value={slotForm.end_time}
                onChange={(e) =>
                  setSlotForm({
                    ...slotForm,
                    end_time: e.target.value,
                  })
                }
              />

              <input
                className="input"
                type="number"
                value={slotForm.capacity}
                onChange={(e) =>
                  setSlotForm({
                    ...slotForm,
                    capacity: Number(e.target.value),
                  })
                }
                placeholder="Capacity"
              />

              <input
                className="input"
                type="number"
                value={slotForm.senior_reserved_capacity}
                onChange={(e) =>
                  setSlotForm({
                    ...slotForm,
                    senior_reserved_capacity: Number(e.target.value),
                  })
                }
                placeholder="Senior reserve"
              />
            </div>

            <button className="btn-primary mt-5" type="submit">
              Create Slot
            </button>
          </form>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h2 className="text-2xl font-black text-temple">Active Alerts</h2>

            <div className="mt-5 space-y-3">
              {overview?.active_alert_list?.length ? (
                overview.active_alert_list.map((alert) => (
                  <div
                    key={alert.id}
                    className="rounded-2xl border border-orange-100 p-4"
                  >
                    <p className="text-xs font-black uppercase text-orange-600">
                      {alert.severity} • {alert.temple_name}
                    </p>

                    <h3 className="mt-1 font-black text-temple">
                      {alert.title}
                    </h3>

                    <p className="mt-1 text-sm text-gray-600">
                      {alert.instruction || alert.message}
                    </p>

                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="btn-secondary mt-3 py-2"
                    >
                      Resolve
                    </button>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">
                  No active alerts right now.
                </p>
              )}
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-2xl font-black text-temple">
              Latest Crowd Readings
            </h2>

            <div className="mt-5 space-y-3">
              {overview?.latest_readings?.length ? (
                overview.latest_readings.map((reading) => (
                  <div
                    key={reading.id}
                    className="rounded-2xl border border-orange-100 p-4 text-sm"
                  >
                    <b>Temple #{reading.temple_id}</b> • Occupancy{" "}
                    {reading.occupancy} • {reading.source}

                    <p className="text-gray-500">
                      {formatDate(reading.created_at)}
                      {reading.notes ? ` • ${reading.notes}` : ""}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">
                  No crowd readings available yet.
                </p>
              )}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}