const classes: Record<string, string> = {
  low: "bg-emerald-100 text-emerald-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800"
};

export default function CrowdBadge({ level }: { level?: string }) {
  const key = level || "low";
  return <span className={`rounded-full px-3 py-1 text-xs font-black uppercase ${classes[key] || classes.low}`}>{key}</span>;
}
