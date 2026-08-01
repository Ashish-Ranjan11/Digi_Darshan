"use client";

import Link from "next/link";
import Nav from "@/components/Nav";

export default function BookTicketPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-amber-50">
      <Nav />

      <section className="mx-auto max-w-6xl px-6 pb-16">
        <div className="mt-8 rounded-[2rem] bg-gradient-to-r from-orange-800 to-amber-500 p-8 text-white shadow-xl">
          <p className="font-black uppercase tracking-[0.3em] text-orange-100">
            Book Darshan Ticket
          </p>

          <h1 className="mt-3 text-4xl font-black">
            Online Pilgrim Booking
          </h1>

          <p className="mt-3 max-w-2xl text-orange-50">
            This page is reserved for the detailed pilgrim booking form. For
            now, use the kiosk/offline ticket panel or we will paste the full
            pilgrim booking form here next.
          </p>
        </div>

        <div className="mt-8 grid gap-5 md:grid-cols-2">
          <Link href="/kiosk" className="card p-6 transition hover:-translate-y-1 hover:shadow-xl">
            <p className="text-4xl">🖨️</p>
            <h2 className="mt-4 text-2xl font-black text-temple">
              Use Kiosk Ticket Panel
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Create offline QR tickets for walk-in pilgrims.
            </p>
          </Link>

          <Link href="/dashboard/slots" className="card p-6 transition hover:-translate-y-1 hover:shadow-xl">
            <p className="text-4xl">🌅</p>
            <h2 className="mt-4 text-2xl font-black text-temple">
              Check Slots First
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Check available slots and crowd status before booking.
            </p>
          </Link>
        </div>
      </section>
    </main>
  );
}
