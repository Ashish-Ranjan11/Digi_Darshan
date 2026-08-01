"use client";

import { QRCodeSVG } from "qrcode.react";
import { formatDate } from "@/lib/api";

type KioskBooking = {
  id: number;
  ticket_code: string;
  temple_name?: string;
  temple_city?: string;
  slot_start?: string;
  slot_end?: string;
  source?: string;
  visit_purpose?: string;
  primary_name?: string;
  primary_age?: number;
  primary_gender?: string;
  primary_phone?: string;
  city?: string;
  state?: string;
  visitor_count: number;
  senior_count?: number;
  differently_abled_count?: number;
  needs_assistance?: boolean;
  family_contact_name?: string;
  family_contact_phone?: string;
  status: string;
  gate?: string;
};

function purposeLabel(value?: string) {
  const labels: Record<string, string> = {
    darshan: "Quick Darshan",
    aarti: "Aarti Viewing",
    special_puja: "Special Puja",
    festival_mela: "Festival / Mela",
    senior_sathi: "SeniorSathi Darshan",
    group_visit: "Group Visit",
    walk_in: "Walk-in Token",
  };

  return labels[value || "darshan"] || value || "Darshan";
}

export default function KioskTicketPrint({
  booking,
}: {
  booking: KioskBooking;
}) {
  function printTicket() {
    window.print();
  }

  const needsPriority =
    booking.needs_assistance ||
    (booking.senior_count || 0) > 0 ||
    (booking.differently_abled_count || 0) > 0;

  return (
    <div className="rounded-3xl border border-orange-100 bg-white p-6 shadow-sm print:shadow-none">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div>
          <p className="text-xs font-black uppercase tracking-widest text-orange-600">
            Offline Kiosk QR Ticket
          </p>

          <h2 className="mt-2 text-2xl font-black text-temple">
            {booking.temple_name || "Temple Darshan"}
          </h2>

          <p className="mt-1 text-sm text-gray-600">
            {booking.temple_city || "Gujarat"} • Booking #{booking.id}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-black uppercase text-orange-700">
              {purposeLabel(booking.visit_purpose)}
            </span>

            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-black uppercase text-blue-700">
              Source: {booking.source || "kiosk"}
            </span>

            {needsPriority ? (
              <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-black uppercase text-purple-700">
                SeniorSathi Priority
              </span>
            ) : null}
          </div>
        </div>

        <div className="rounded-3xl border border-orange-100 bg-orange-50 p-4">
          <QRCodeSVG value={booking.ticket_code} size={160} />
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
          Show this QR at the temple scanner gate.
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
          <b>Seniors:</b> {booking.senior_count || 0}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Differently Abled:</b> {booking.differently_abled_count || 0}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Gate:</b> {booking.gate || "Scanner Gate"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Slot Start:</b>{" "}
          {booking.slot_start ? formatDate(booking.slot_start) : "-"}
        </div>

        <div className="rounded-2xl bg-orange-50 p-4 text-sm">
          <b>Slot End:</b>{" "}
          {booking.slot_end ? formatDate(booking.slot_end) : "-"}
        </div>
      </div>

      {needsPriority ? (
        <div className="mt-5 rounded-3xl bg-purple-50 p-4 text-sm text-purple-800">
          <p className="font-black">SeniorSathi Support Required</p>
          <p className="mt-1">
            Please guide pilgrim toward SeniorSathi/priority assistance counter.
          </p>
          <p className="mt-1">
            Family contact: {booking.family_contact_name || "-"}{" "}
            {booking.family_contact_phone
              ? `(${booking.family_contact_phone})`
              : ""}
          </p>
        </div>
      ) : null}

      <div className="mt-5 flex flex-wrap gap-3 print:hidden">
        <button onClick={printTicket} className="btn-primary">
          Print QR Ticket
        </button>

        <button
          onClick={() => navigator.clipboard.writeText(booking.ticket_code)}
          className="btn-secondary"
        >
          Copy Ticket Code
        </button>
      </div>
    </div>
  );
}
