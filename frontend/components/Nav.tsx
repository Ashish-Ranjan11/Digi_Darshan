import Link from "next/link";

export default function Nav() {
  return (
    <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
      <Link href="/" className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-orange-600 text-xl font-black text-white">ॐ</div>
        <div>
          <p className="text-lg font-black text-temple">Digii-Darshan</p>
          <p className="text-xs font-semibold text-orange-700">Safe Devotion • Smart Pilgrimage</p>
        </div>
      </Link>
      <div className="hidden items-center gap-3 md:flex">
        <Link className="btn-secondary py-2" href="/dashboard">Pilgrim</Link>
        <Link className="btn-secondary py-2" href="/admin">Admin</Link>
        <Link className="btn-primary py-2" href="/login">Login</Link>
      </div>
    </nav>
  );
}
