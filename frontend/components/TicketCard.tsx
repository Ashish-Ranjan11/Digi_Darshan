"use client";

import { QRCodeSVG } from "qrcode.react";
import { formatDate } from "@/lib/api";

type TicketBooking = {
  id: number;
  temple_id?: number;
  temple_name?: string;
  temple_city?: string;
  slot_start?: string;
  slot_end?: string;
  ticket_code: string;
  source?: string;
  visit_purpose?: string;
  primary_name?: string;
  primary_age?: number;
  primary_gender?: string;
  primary_phone?: string;
  primary_email?: string;
  city?: string;
  state?: string;
  visitor_count: number;
  senior_count?: number;
  differently_abled_count?: number;
  arrival_mode?: string;
  expected_duration_minutes?: number;
  preferred_language?: string;
  needs_assistance?: boolean;
  family_contact_name?: string;
  family_contact_phone?: string;
  status: string;
  gate?: string;
  checked_in_at?: string;
  checked_out_at?: string;
};

function statusClass(status: string) {
  if (status === "booked") return "bg-blue-100 text-blue-700";
  if (status === "checked_in") return "bg-green-100 text-green-700";
  if (status === "completed") return "bg-gray-100 text-gray-700";
  if (status === "cancelled") return "bg-red-100 text-red-700";
  return "bg-orange-100 text-orange-700";
}

function purposeLabel(value?: string) {
  const labels: Record<string, string> = {
    darshan: "Quick Darshan",
    aarti: "Aarti Viewing",
    special_puja: "Special Puja",
    festival_mela: "Festival / Mela",
    senior_sathi: "SeniorSathi Darshan",
    vip_visit: "VIP Visit",
    group_visit: "Group Visit",
    walk_in: "Walk-in Token",
  };

  return labels[value || "darshan"] || value || "Darshan";
}

export default function TicketCard({ booking }: { booking: TicketBooking }) {
  async function copyTicketCode() {
    await navigator.clipboard.writeText(booking.ticket_code);
    alert("Ticket code copied.");
  }

  function printTicket() {
    window.print();
  }

  const isSeniorSathi =
    booking.needs_assistance ||
    (booking.senior_count || 0) > 0 ||
    (booking.differently_abled_count || 0) > 0;

  return (
    <div className="rounded-3xl border border-orange-100 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div>
          <p className="text-xs font-black uppercase tracking-widest text-orange-600">
            Digii-Darshan Secure QR Ticket
          </p>

          <h3 className="mt-2 text-2xl font-black text-temple">
            {booking.temple_name || "Temple Darshan"}
          </h3>

          <p className="mt-1 text-sm text-gray-600">
            {booking.temple_city || "Gujarat"} • Booking #{booking.id}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <span
              className={`inline-flex rounded-full px-3 py-1 text-xs font-black uppercase ${statusClass(
                booking.status
              )}`}
            >
              {booking.status.replace("_", " ")}
            </span>

            <span className="inline-flex rounded-full bg-orange-100 px-3 py-1 text-xs font-black uppercase text-orange-700">
              {purposeLabel(booking.visit_purpose)}
            </span>

            {isSeniorSathi ? (
              <span className="inline-flex rounded-full bg-purple-100 px-3 py-1 text-xs font-black uppercase text-purple-700">
                SeniorSathi Priority
              </span>
            ) : null}
          </div>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-orange-50 p-4">
          <QRCodeSVG value={booking.ticket_code} size={150} />
        </div>
      </div>

      <div className="mt-6 rounded-3xl bg-gray-900 p-5 text-orange-100">
        <p className="text-xs font-black uppercase tracking-widest text-orange-300">
          Scanner Ticket Code
        </p>

        <p className="mt-2 break-all font-mono text-2xl font-black text-white">
          {booking.ticket_code}
        </p>

        <p className="mt-2 text-xs text-orange-200">
          Gate staff should scan this QR or enter this ticket code manually.
        </p>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Pilgrim:</b> {booking.primary_name || "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Phone:</b> {booking.primary_phone || "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Age/Gender:</b> {booking.primary_age || "-"} /{" "}
          {booking.primary_gender || "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>City:</b> {booking.city || "-"}, {booking.state || "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Visitors:</b> {booking.visitor_count}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Senior Citizens:</b> {booking.senior_count ?? 0}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Differently Abled:</b> {booking.differently_abled_count ?? 0}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Arrival Mode:</b> {booking.arrival_mode || "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Expected Stay:</b> {booking.expected_duration_minutes || 30} minutes
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Language:</b> {booking.preferred_language || "Hindi"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Gate:</b> {booking.gate || "Not scanned yet"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Source:</b> {booking.source || "online"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Slot Start:</b>{" "}
          {booking.slot_start ? formatDate(booking.slot_start) : "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Slot End:</b>{" "}
          {booking.slot_end ? formatDate(booking.slot_end) : "-"}
        </div>

        <div className="rounded-2xl bg-green-50 p-4 text-sm text-green-700">
          <b>Checked In:</b>{" "}
          {booking.checked_in_at ? formatDate(booking.checked_in_at) : "No"}
        </div>

        <div className="rounded-2xl bg-gray-50 p-4 text-sm text-gray-700">
          <b>Checked Out:</b>{" "}
          {booking.checked_out_at ? formatDate(booking.checked_out_at) : "No"}
        </div>
      </div>

      {isSeniorSathi ? (
        <div className="mt-5 rounded-3xl bg-purple-50 p-4 text-sm text-purple-800">
          <p className="font-black">SeniorSathi Assistance Requested</p>
          <p className="mt-1">
            Priority gate: <b>{booking.gate || "SeniorSathi Gate"}</b>
          </p>
          <p className="mt-1">
            Family contact: {booking.family_contact_name || "-"}{" "}
            {booking.family_contact_phone ? `(${booking.family_contact_phone})` : ""}
          </p>
        </div>
      ) : null}

      <div className="mt-5 flex flex-wrap gap-3">
        <button onClick={copyTicketCode} className="btn-primary">
          Copy Ticket Code
        </button>

        <button onClick={printTicket} className="btn-secondary">
          Print Ticket
        </button>
      </div>
    </div>
  );
}