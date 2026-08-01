"use client";

import { useEffect, useMemo, useRef, useState } from "react";

export default function QRCameraScanner({
  onScan,
}: {
  onScan: (ticketCode: string) => void;
}) {
  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");
  const lockedRef = useRef(false);

  const elementId = useMemo(
    () => `qr-reader-${Math.random().toString(36).slice(2)}`,
    []
  );

  useEffect(() => {
    if (!cameraOn) return;

    let scanner: any = null;
    lockedRef.current = false;

    async function startScanner() {
      try {
        const { Html5QrcodeScanner } = await import("html5-qrcode");

        scanner = new Html5QrcodeScanner(
          elementId,
          {
            fps: 10,
            qrbox: {
              width: 250,
              height: 250,
            },
            rememberLastUsedCamera: true,
          },
          false
        );

        scanner.render(
          (decodedText: string) => {
            if (lockedRef.current) return;

            lockedRef.current = true;
            onScan(decodedText.trim().toUpperCase());

            scanner
              .clear()
              .catch(() => null)
              .finally(() => setCameraOn(false));
          },
          () => {
            // Ignore frame-level scan failures.
          }
        );
      } catch (err: any) {
        setError(err.message || "Unable to start camera scanner.");
        setCameraOn(false);
      }
    }

    startScanner();

    return () => {
      if (scanner) {
        scanner.clear().catch(() => null);
      }
    };
  }, [cameraOn, elementId, onScan]);

  return (
    <div className="rounded-3xl border border-orange-100 bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-black uppercase tracking-widest text-orange-600">
            Camera QR Scanner
          </p>
          <h2 className="mt-1 text-xl font-black text-temple">
            Scan Pilgrim Ticket
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            Use this for real gate-level check-in and check-out.
          </p>
        </div>

        <button
          onClick={() => {
            setError("");
            setCameraOn(!cameraOn);
          }}
          className={cameraOn ? "btn-secondary" : "btn-primary"}
        >
          {cameraOn ? "Stop Camera" : "Start Camera"}
        </button>
      </div>

      {error ? (
        <p className="mt-4 rounded-2xl bg-red-50 p-3 text-sm font-bold text-red-700">
          {error}
        </p>
      ) : null}

      {cameraOn ? (
        <div className="mt-5 overflow-hidden rounded-3xl border border-orange-100">
          <div id={elementId} />
        </div>
      ) : (
        <p className="mt-5 rounded-3xl bg-orange-50 p-4 text-sm font-semibold text-orange-800">
          Camera is off. You can still enter the ticket code manually.
        </p>
      )}
    </div>
  );
}
