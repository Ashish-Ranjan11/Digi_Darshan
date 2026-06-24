type HeatmapZone = {
  zone: string;
  crowd_percent: number;
  level: string;
  role: string;
  advice: string;
};

function levelClass(level: string) {
  if (level === "critical") return "border-red-200 bg-red-50 text-red-700";
  if (level === "high") return "border-orange-200 bg-orange-50 text-orange-700";
  if (level === "medium") return "border-yellow-200 bg-yellow-50 text-yellow-700";
  return "border-green-200 bg-green-50 text-green-700";
}

export default function CrowdHeatmap({ zones }: { zones: HeatmapZone[] }) {
  return (
    <div className="rounded-3xl border border-orange-100 bg-white p-5 shadow-sm">
      <div>
        <p className="font-black uppercase tracking-widest text-orange-600">
          Temple Heatmap
        </p>
        <h3 className="mt-1 text-xl font-black text-temple">
          Zone-wise Crowd Density
        </h3>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {zones.map((zone) => (
          <div
            key={zone.zone}
            className={`rounded-3xl border p-4 ${levelClass(zone.level)}`}
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <h4 className="font-black">{zone.zone}</h4>
                <p className="mt-1 text-xs opacity-80">{zone.role}</p>
              </div>

              <span className="rounded-full bg-white px-3 py-1 text-xs font-black uppercase">
                {zone.level}
              </span>
            </div>

            <div className="mt-4 h-3 rounded-full bg-white">
              <div
                className="h-3 rounded-full bg-current transition-all"
                style={{ width: `${Math.min(zone.crowd_percent, 100)}%` }}
              />
            </div>

            <p className="mt-2 text-sm font-bold">
              {zone.crowd_percent}% crowd pressure
            </p>

            <p className="mt-1 text-xs opacity-90">{zone.advice}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
