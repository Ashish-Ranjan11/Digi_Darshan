"use client";

import Nav from "@/components/Nav";
import PilgrimAssistantBot from "@/components/PilgrimAssistantBot";

export default function AssistantPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />

      <section className="mx-auto max-w-5xl px-6 pb-16">
        <div className="mt-8 rounded-[2rem] bg-gradient-to-r from-orange-800 to-amber-500 p-8 text-white shadow-xl">
          <p className="font-black uppercase tracking-[0.3em] text-orange-100">
            AI Pilgrim Helpdesk
          </p>

          <h1 className="mt-3 text-4xl font-black">Digii AI Sathi</h1>

          <p className="mt-3 max-w-2xl text-orange-50">
            Ask about darshan booking, crowd rush, tomorrow slots, aarti,
            SeniorSathi, offline kiosk help, and temple contact details.
          </p>
        </div>

        <div className="mt-8">
          <PilgrimAssistantBot />
        </div>
      </section>
    </main>
  );
}
