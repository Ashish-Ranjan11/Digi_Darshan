"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import Nav from "@/components/Nav";
import { apiFetch, setSession } from "@/lib/api";
import { User } from "@/lib/types";

type RegisterResponse = { access_token: string; user: User };

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch<RegisterResponse>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ ...form, role: "pilgrim" })
      });
      setSession(data.access_token, data.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <Nav />
      <section className="mx-auto max-w-3xl px-6 py-10">
        <form onSubmit={submit} className="card p-7">
          <p className="font-black uppercase tracking-widest text-orange-600">Pilgrim Signup</p>
          <h1 className="mt-3 text-4xl font-black text-temple">Create your darshan account</h1>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm font-bold text-gray-700">Full name</label>
              <input className="input mt-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div>
              <label className="text-sm font-bold text-gray-700">Phone</label>
              <input className="input mt-2" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div>
              <label className="text-sm font-bold text-gray-700">Email</label>
              <input className="input mt-2" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div>
              <label className="text-sm font-bold text-gray-700">Password</label>
              <input className="input mt-2" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
          </div>
          {error ? <p className="mt-4 rounded-2xl bg-red-50 p-3 text-sm font-bold text-red-700">{error}</p> : null}
          <button disabled={loading} className="btn-primary mt-6" type="submit">
            {loading ? "Creating..." : "Create account"}
          </button>
          <p className="mt-5 text-sm text-gray-600">
            Already have an account? <Link href="/login" className="font-black text-orange-700">Login</Link>
          </p>
        </form>
      </section>
    </main>
  );
}
