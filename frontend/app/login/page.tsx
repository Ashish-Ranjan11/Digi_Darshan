"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import Nav from "@/components/Nav";
import { apiFetch, setSession } from "@/lib/api";
import { User } from "@/lib/types";

type LoginResponse = { access_token: string; user: User };

const demos = [
  ["Admin", "admin@digidarshan.in", "Admin@123"],
  ["Operator", "operator@digidarshan.in", "Operator@123"],
  ["Scanner", "scanner@digidarshan.in", "Scanner@123"],
  ["Pilgrim", "pilgrim@digidarshan.in", "Pilgrim@123"]
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("pilgrim@digidarshan.in");
  const [password, setPassword] = useState("Pilgrim@123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch<LoginResponse>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setSession(data.access_token, data.user);
      if (data.user.role === "admin" || data.user.role === "emergency_operator") router.push("/admin");
      else if (data.user.role === "scanner") router.push("/scanner");
      else router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />
      <section className="mx-auto grid max-w-6xl gap-8 px-6 py-10 lg:grid-cols-2 lg:items-center">
        <div>
          <p className="font-black uppercase tracking-widest text-orange-600">Secure Access</p>
          <h1 className="mt-3 text-5xl font-black text-temple">Login to Digii-Darshan</h1>
          <p className="mt-5 text-lg leading-8 text-gray-700">
            Use role-based dashboards for pilgrims, control-room admins, emergency operators, and QR gate scanners.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            {demos.map(([label, mail, pass]) => (
              <button
                type="button"
                key={label}
                onClick={() => {
                  setEmail(mail);
                  setPassword(pass);
                }}
                className="rounded-2xl border border-orange-100 bg-white p-4 text-left shadow-sm transition hover:border-orange-300"
              >
                <p className="font-black text-temple">{label}</p>
                <p className="mt-1 text-xs text-gray-500">{mail}</p>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={submit} className="card p-7">
          <h2 className="text-2xl font-black text-temple">Welcome back</h2>
          <p className="mt-1 text-sm text-gray-500">Enter credentials or click a demo account.</p>
          <label className="mt-6 block text-sm font-bold text-gray-700">Email</label>
          <input className="input mt-2" value={email} onChange={(e) => setEmail(e.target.value)} />
          <label className="mt-4 block text-sm font-bold text-gray-700">Password</label>
          <input className="input mt-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error ? <p className="mt-4 rounded-2xl bg-red-50 p-3 text-sm font-bold text-red-700">{error}</p> : null}
          <button disabled={loading} className="btn-primary mt-6 w-full" type="submit">
            {loading ? "Logging in..." : "Login"}
          </button>
          <p className="mt-5 text-center text-sm text-gray-600">
            New pilgrim? <Link className="font-black text-orange-700" href="/register">Create account</Link>
          </p>
        </form>
      </section>
    </main>
  );
}
