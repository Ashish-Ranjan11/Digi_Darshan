import Link from "next/link";
import Nav from "@/components/Nav";

const modules = [
  {
    title: "DigiiQueue & E-Ticketing",
    text: "Pilgrims choose darshan time slots, receive digital tokens, and track queue position before reaching the temple."
  },
  {
    title: "Digii-CrowdControl",
    text: "Authorities monitor live occupancy, density level, slot utilisation, and gate movement from a single dashboard."
  },
  {
    title: "Digii-Suraksha",
    text: "Emergency operators create instant alerts with clear safety instructions for panic, medical, or congestion events."
  },
  {
    title: "Digii-Flowmaster",
    text: "Parking availability, shuttle routes, traffic hints, and alternate routes reduce congestion near pilgrimage areas."
  },
  {
    title: "SeniorSathi",
    text: "Senior citizens and differently-abled pilgrims receive priority slots, safer gates, and family-friendly booking support."
  }
];

const temples = ["Somnath", "Dwarka", "Ambaji", "Pavagadh"];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,#fed7aa,transparent_35%),linear-gradient(180deg,#fff7ed,#ffffff)]">
      <Nav />

      <section className="mx-auto grid max-w-7xl gap-10 px-6 pb-16 pt-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div>
          <div className="mb-5 inline-flex rounded-full border border-orange-200 bg-white/80 px-4 py-2 text-sm font-bold text-orange-700">
            SIH 2025 • Temple & Pilgrimage Crowd Management
          </div>
          <h1 className="text-5xl font-black leading-tight text-temple md:text-7xl">
            Digii-Darshan for safer, smoother, smarter devotion.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-700">
            A deployable web platform for Gujarat pilgrimage sites that combines slot-based e-ticketing, live crowd monitoring, emergency alerts, parking guidance, and senior-friendly darshan support.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="btn-primary" href="/register">Book Darshan</Link>
            <Link className="btn-secondary" href="/admin">Open Control Room</Link>
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            {temples.map((temple) => (
              <span key={temple} className="rounded-full bg-white px-4 py-2 text-sm font-bold text-gray-700 shadow">
                {temple}
              </span>
            ))}
          </div>
        </div>

        <div className="card relative p-6">
          <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-orange-200 blur-2xl" />
          <div className="rounded-3xl bg-gradient-to-br from-orange-600 to-amber-500 p-6 text-white">
            <p className="text-sm font-bold uppercase tracking-widest text-orange-100">Live Temple Snapshot</p>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-white/15 p-5 backdrop-blur">
                <p className="text-sm text-orange-100">Current Occupancy</p>
                <p className="mt-2 text-4xl font-black">42%</p>
              </div>
              <div className="rounded-2xl bg-white/15 p-5 backdrop-blur">
                <p className="text-sm text-orange-100">Queue Delay</p>
                <p className="mt-2 text-4xl font-black">18m</p>
              </div>
              <div className="rounded-2xl bg-white/15 p-5 backdrop-blur">
                <p className="text-sm text-orange-100">Parking Open</p>
                <p className="mt-2 text-4xl font-black">600+</p>
              </div>
              <div className="rounded-2xl bg-white/15 p-5 backdrop-blur">
                <p className="text-sm text-orange-100">Alert Level</p>
                <p className="mt-2 text-4xl font-black">Low</p>
              </div>
            </div>
          </div>
          <div className="mt-5 rounded-3xl border border-orange-100 bg-orange-50 p-5">
            <p className="font-black text-temple">How it works</p>
            <ol className="mt-3 space-y-2 text-sm text-gray-700">
              <li>1. Pilgrim selects temple and time slot.</li>
              <li>2. System issues QR ticket and gate suggestion.</li>
              <li>3. Control room monitors occupancy and alerts.</li>
              <li>4. Scanner check-in/out updates live crowd count.</li>
            </ol>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="mb-8 max-w-3xl">
          <p className="font-black uppercase tracking-widest text-orange-600">Feature Modules</p>
          <h2 className="mt-2 text-3xl font-black text-temple md:text-5xl">Everything needed for the MVP demo.</h2>
        </div>
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {modules.map((item) => (
            <div key={item.title} className="card p-6">
              <div className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-orange-100 text-xl">✦</div>
              <h3 className="text-xl font-black text-temple">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-gray-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
