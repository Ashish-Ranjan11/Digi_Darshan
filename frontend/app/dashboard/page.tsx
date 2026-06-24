"use client";

import Link from "next/link";
import { QRCodeCanvas } from "qrcode.react";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import CrowdBadge from "@/components/CrowdBadge";
import Nav from "@/components/Nav";
import StatCard from "@/components/StatCard";
import { apiFetch, clearSession, formatDate, getStoredUser, getToken, WS_URL } from "@/lib/api";
import { Alert, Booking, ParkingZone, Slot, Temple, User } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [temples, setTemples] = useState<Temple[]>([]);
  const [selectedTempleId, setSelectedTempleId] = useState<number | null>(null);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [parking, setParking] = useState<ParkingZone[]>([]);
  const [visitorCount, setVisitorCount] = useState(1);
  const [seniorCount, setSeniorCount] = useState(0);
  const [differentlyAbledCount, setDifferentlyAbledCount] = useState(0);
  const [message, setMessage] = useState("");
  const [liveEvent, setLiveEvent] = useState<any>(null);

  const selectedTemple = useMemo(() => temples.find((temple) => temple.id === selectedTempleId), [temples, selectedTempleId]);

  async function loadBase() {
    const [templeData, bookingData, alertData] = await Promise.all([
      apiFetch<Temple[]>("/api/temples"),
      apiFetch<Booking[]>("/api/bookings/me"),
      apiFetch<Alert[]>("/api/alerts")
    ]);
    setTemples(templeData);
    setBookings(bookingData);
    setAlerts(alertData);
    if (!selectedTempleId && templeData[0]) setSelectedTempleId(templeData[0].id);
  }

  async function loadTempleDetails(templeId: number) {
    const [slotData, parkingData] = await Promise.all([
      apiFetch<Slot[]>(`/api/slots?temple_id=${templeId}`),
      apiFetch<ParkingZone[]>(`/api/mobility/parking?temple_id=${templeId}`)
    ]);
    setSlots(slotData);
    setParking(parkingData);
    setSelectedSlotId(slotData[0]?.id || null);
  }

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    setUser(getStoredUser());
    loadBase().catch((err) => setMessage(err.message));
  }, []);

  useEffect(() => {
    if (!selectedTempleId) return;
    loadTempleDetails(selectedTempleId).catch((err) => setMessage(err.message));
    const ws = new WebSocket(`${WS_URL}/ws/temples/${selectedTempleId}`);
    ws.onmessage = (event) => setLiveEvent(JSON.parse(event.data));
    ws.onopen = () => ws.send("ping");
    return () => ws.close();
  }, [selectedTempleId]);

  async function createBooking(event: FormEvent) {
    event.preventDefault();
    if (!selectedTempleId || !selectedSlotId) return;
    setMessage("");
    try {
      await apiFetch<Booking>("/api/bookings", {
        method: "POST",
        body: JSON.stringify({
          temple_id: selectedTempleId,
          slot_id: selectedSlotId,
          visitor_count: visitorCount,
          senior_count: seniorCount,
          differently_abled_count: differentlyAbledCount
        })
      });
      setMessage("Booking successful. Your QR ticket is visible below.");
      await loadBase();
      await loadTempleDetails(selectedTempleId);
    } catch (err: any) {
      setMessage(err.message || "Booking failed");
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
            <p className="font-black uppercase tracking-widest text-orange-600">Pilgrim Dashboard</p>
            <h1 className="mt-2 text-4xl font-black text-temple">Namaste {user?.name || "Pilgrim"}</h1>
            <p className="mt-2 text-gray-600">Book a slot, view queue status, receive alerts, and carry your QR ticket.</p>
          </div>
          <button onClick={logout} className="btn-secondary">Logout</button>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <StatCard label="Temples" value={temples.length} hint="Active Gujarat sites" />
          <StatCard label="My Tickets" value={bookings.length} hint="Booked / checked-in" />
          <StatCard label="Active Alerts" value={alerts.length} hint="Safety messages" />
          <StatCard label="Live Event" value={liveEvent?.type || "Ready"} hint={liveEvent?.message || "Connected after temple selection"} />
        </div>

        {message ? <p className="mt-6 rounded-2xl bg-white p-4 text-sm font-bold text-orange-800 shadow">{message}</p> : null}

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <form onSubmit={createBooking} className="card p-6">
            <h2 className="text-2xl font-black text-temple">Book Darshan Slot</h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-bold text-gray-700">Temple</label>
                <select className="input mt-2" value={selectedTempleId || ""} onChange={(e) => setSelectedTempleId(Number(e.target.value))}>
                  {temples.map((temple) => (
                    <option key={temple.id} value={temple.id}>{temple.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-bold text-gray-700">Slot</label>
                <select className="input mt-2" value={selectedSlotId || ""} onChange={(e) => setSelectedSlotId(Number(e.target.value))}>
                  {slots.map((slot) => (
                    <option key={slot.id} value={slot.id}>
                      {formatDate(slot.start_time)} • {slot.available_count} left
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-bold text-gray-700">Total visitors</label>
                <input className="input mt-2" type="number" min={1} max={10} value={visitorCount} onChange={(e) => setVisitorCount(Number(e.target.value))} />
              </div>
              <div>
                <label className="text-sm font-bold text-gray-700">Senior citizens</label>
                <input className="input mt-2" type="number" min={0} max={10} value={seniorCount} onChange={(e) => setSeniorCount(Number(e.target.value))} />
              </div>
              <div>
                <label className="text-sm font-bold text-gray-700">Differently-abled visitors</label>
                <input className="input mt-2" type="number" min={0} max={10} value={differentlyAbledCount} onChange={(e) => setDifferentlyAbledCount(Number(e.target.value))} />
              </div>
            </div>
            <button className="btn-primary mt-6" type="submit">Confirm E-Ticket</button>
          </form>

          <div className="card p-6">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-2xl font-black text-temple">Live Temple Status</h2>
                <p className="mt-1 text-sm text-gray-500">Updates from control room and scanner gates.</p>
              </div>
              <CrowdBadge level={selectedTemple?.crowd_level} />
            </div>
            {selectedTemple ? (
              <div className="mt-5 space-y-4">
                <div>
                  <div className="flex justify-between text-sm font-bold text-gray-600">
                    <span>{selectedTemple.name}</span>
                    <span>{selectedTemple.occupancy_percent}%</span>
                  </div>
                  <div className="mt-2 h-3 rounded-full bg-orange-100">
                    <div className="h-3 rounded-full bg-orange-600" style={{ width: `${Math.min(selectedTemple.occupancy_percent, 100)}%` }} />
                  </div>
                </div>
                <p className="rounded-2xl bg-orange-50 p-4 text-sm text-gray-700">Current occupancy: <b>{selectedTemple.current_occupancy}</b> / {selectedTemple.max_capacity}. Suggested gate will be printed on your ticket.</p>
                <div>
                  <p className="mb-2 font-black text-temple">Parking guidance</p>
                  <div className="space-y-2">
                    {parking.map((zone) => (
                      <div key={zone.id} className="rounded-2xl border border-orange-100 p-3 text-sm">
                        <b>{zone.name}</b> • {zone.available_slots}/{zone.total_slots} free
                        <p className="text-gray-500">{zone.distance_label} {zone.route_hint}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h2 className="text-2xl font-black text-temple">My Tickets</h2>
            <div className="mt-5 space-y-4">
              {bookings.length === 0 ? <p className="text-sm text-gray-500">No bookings yet.</p> : null}
              {bookings.map((booking) => (
                <div key={booking.id} className="rounded-3xl border border-orange-100 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="text-lg font-black text-temple">{booking.temple_name}</p>
                      <p className="mt-1 text-sm text-gray-600">{formatDate(booking.slot_start)} • {booking.gate}</p>
                      <p className="mt-2 rounded-full bg-orange-50 px-3 py-1 text-xs font-black uppercase text-orange-700">{booking.status}</p>
                    </div>
                    <div className="rounded-2xl bg-white p-2 shadow-sm">
                      <QRCodeCanvas value={booking.ticket_code} size={92} />
                    </div>
                  </div>
                  <p className="mt-3 font-mono text-sm font-black text-gray-700">{booking.ticket_code}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-2xl font-black text-temple">Safety Alerts</h2>
            <div className="mt-5 space-y-3">
              {alerts.length === 0 ? <p className="text-sm text-gray-500">No active alerts.</p> : null}
              {alerts.map((alert) => (
                <div key={alert.id} className="rounded-2xl border border-orange-100 bg-white p-4">
                  <p className="text-xs font-black uppercase text-orange-600">{alert.severity} • {alert.temple_name}</p>
                  <h3 className="mt-1 font-black text-temple">{alert.title}</h3>
                  <p className="mt-1 text-sm text-gray-600">{alert.instruction || alert.message}</p>
                </div>
              ))}
            </div>
            <Link href="/" className="btn-secondary mt-5 inline-block">Back to Home</Link>
          </div>
        </div>
      </section>
    </main>
  );
}
