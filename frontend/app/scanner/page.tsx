"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import Nav from "@/components/Nav";
import { apiFetch, clearSession, formatDate, getStoredUser, getToken } from "@/lib/api";
import { Booking, User } from "@/lib/types";

export default function ScannerPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [ticketCode, setTicketCode] = useState("");
  const [gate, setGate] = useState("Gate A");
  const [result, setResult] = useState<Booking | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    const stored = getStoredUser();
    setUser(stored);
    if (stored?.role === "pilgrim") router.push("/dashboard");
  }, []);

  async function scan(event: FormEvent, mode: "check-in" | "check-out") {
    event.preventDefault();
    setMessage("");
    setResult(null);
    try {
      const data = await apiFetch<Booking>(`/api/scanner/${mode}`, {
        method: "POST",
        body: JSON.stringify({ ticket_code: ticketCode, gate })
      });
      setResult(data);
      setMessage(mode === "check-in" ? "Check-in successful." : "Check-out successful.");
    } catch (err: any) {
      setMessage(err.message || "Scan failed");
    }
  }

  function logout() {
    clearSession();
    router.push("/login");
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />
      <section className="mx-auto max-w-4xl px-6 pb-16">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-black uppercase tracking-widest text-orange-600">Gate Scanner</p>
            <h1 className="mt-2 text-4xl font-black text-temple">QR Ticket Check-in / Check-out</h1>
            <p className="mt-2 text-gray-600">Logged in as {user?.name || "scanner"}.</p>
          </div>
          <button onClick={logout} className="btn-secondary">Logout</button>
        </div>

        <form className="card p-7">
          <label className="text-sm font-bold text-gray-700">Ticket Code</label>
          <input className="input mt-2 font-mono" value={ticketCode} onChange={(e) => setTicketCode(e.target.value.toUpperCase())} placeholder="DD-XXXXXXXXXX" />
          <label className="mt-4 block text-sm font-bold text-gray-700">Gate</label>
          <select className="input mt-2" value={gate} onChange={(e) => setGate(e.target.value)}>
            <option>Gate A</option>
            <option>Gate B</option>
            <option>Gate C</option>
            <option>Emergency Gate</option>
          </select>
          <div className="mt-6 flex flex-wrap gap-3">
            <button className="btn-primary" onClick={(event) => scan(event, "check-in")}>Check In</button>
            <button className="btn-secondary" onClick={(event) => scan(event, "check-out")}>Check Out</button>
          </div>
        </form>

        {message ? <p className="mt-6 rounded-2xl bg-white p-4 text-sm font-bold text-orange-800 shadow">{message}</p> : null}

        {result ? (
          <div className="card mt-6 p-6">
            <p className="text-xs font-black uppercase tracking-widest text-orange-600">Verified Ticket</p>
            <h2 className="mt-2 text-2xl font-black text-temple">{result.temple_name}</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <p className="rounded-2xl bg-orange-50 p-4 text-sm"><b>Ticket:</b> {result.ticket_code}</p>
              <p className="rounded-2xl bg-orange-50 p-4 text-sm"><b>Status:</b> {result.status}</p>
              <p className="rounded-2xl bg-orange-50 p-4 text-sm"><b>Gate:</b> {result.gate}</p>
              <p className="rounded-2xl bg-orange-50 p-4 text-sm"><b>Slot:</b> {formatDate(result.slot_start)}</p>
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
