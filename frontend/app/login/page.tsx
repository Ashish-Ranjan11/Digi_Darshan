"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import gsap from "gsap";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type LoginResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    name: string;
    email: string;
    phone?: string;
    role: string;
    assigned_temples?: number[];
  };
};

const demoUsers = [
  {
    label: "Pilgrim",
    email: "pilgrim@digidarshan.in",
    password: "Pilgrim@123",
    desc: "Book darshan, view QR tickets and check live crowd slots.",
  },
  {
    label: "Admin",
    email: "admin@digidarshan.in",
    password: "Admin@123",
    desc: "Open command center with live crowd, AI prediction and alerts.",
  },
  {
    label: "Scanner",
    email: "scanner@digidarshan.in",
    password: "Scanner@123",
    desc: "Validate QR passes and handle check-in / check-out.",
  },
  {
    label: "Kiosk",
    email: "kiosk@digidarshan.in",
    password: "Kiosk@123",
    desc: "Generate offline QR passes for walk-in pilgrims.",
  },
];

function cleanRole(role?: string) {
  return String(role || "pilgrim")
    .replace("UserRole.", "")
    .replace("Role.", "")
    .trim()
    .toLowerCase();
}

function routeForRole(role?: string) {
  const r = cleanRole(role);

  if (
    r === "admin" ||
    r === "super_admin" ||
    r === "temple_admin" ||
    r === "emergency_operator"
  ) {
    return "/admin";
  }

  if (r === "scanner") return "/scanner";
  if (r === "kiosk_operator") return "/kiosk";
  if (r === "senior_sathi_volunteer") return "/senior-sathi";
  if (r === "vip_coordinator") return "/vip";

  return "/dashboard";
}

function clearSession() {
  if (typeof window === "undefined") return;

  [
    "dd_token",
    "token",
    "access_token",
    "digidarshan_token",
    "authToken",
    "auth_token",
    "accessToken",
    "jwt",
    "dd_user",
    "user",
    "digidarshan_user",
    "currentUser",
    "auth_user",
  ].forEach((key) => localStorage.removeItem(key));
}

function saveSession(data: LoginResponse) {
  const user = {
    ...data.user,
    role: cleanRole(data.user.role),
  };

  localStorage.setItem("dd_token", data.access_token);
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("digidarshan_token", data.access_token);
  localStorage.setItem("authToken", data.access_token);
  localStorage.setItem("auth_token", data.access_token);
  localStorage.setItem("accessToken", data.access_token);
  localStorage.setItem("jwt", data.access_token);

  localStorage.setItem("dd_user", JSON.stringify(user));
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("digidarshan_user", JSON.stringify(user));
  localStorage.setItem("currentUser", JSON.stringify(user));
  localStorage.setItem("auth_user", JSON.stringify(user));

  return user;
}

export default function LoginPage() {
  const [email, setEmail] = useState("pilgrim@digidarshan.in");
  const [password, setPassword] = useState("Pilgrim@123");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    clearSession();

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".dd-animate-nav",
        { opacity: 0, y: -28 },
        { opacity: 1, y: 0, duration: 0.85, ease: "power3.out" }
      );

      gsap.fromTo(
        ".dd-login-intro",
        { opacity: 0, x: -44, filter: "blur(12px)" },
        {
          opacity: 1,
          x: 0,
          filter: "blur(0px)",
          duration: 1,
          delay: 0.15,
          ease: "power3.out",
        }
      );

      gsap.fromTo(
        ".dd-login-card",
        { opacity: 0, y: 44, scale: 0.96 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 1,
          delay: 0.28,
          ease: "power3.out",
        }
      );

      gsap.fromTo(
        ".dd-demo-grid button",
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.65,
          stagger: 0.08,
          delay: 0.55,
          ease: "power3.out",
        }
      );
    });

    return () => ctx.revert();
  }, []);

  async function handleLogin() {
    if (loading) return;

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data: LoginResponse & { detail?: string; message?: string } =
        await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Login failed");
      }

      const user = saveSession(data);
      const nextRoute = routeForRole(user.role);

      setMessage(`Login successful. Opening ${nextRoute}...`);

      window.setTimeout(() => {
        window.location.assign(nextRoute);
      }, 350);
    } catch (error: any) {
      clearSession();
      setMessage(error.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  function fillUser(user: (typeof demoUsers)[number]) {
    setEmail(user.email);
    setPassword(user.password);
    setMessage("");
  }

  return (
    <main className="dd-login-root">
      <video
        className="dd-login-video"
        src="/videos/digidarshan-hero.mp4"
        autoPlay
        muted
        loop
        playsInline
      />

      <div className="dd-login-overlay" />
      <div className="dd-grain" />

      <header className="dd-landing-nav dd-animate-nav">
        <Link href="/" className="dd-brand">
          <span className="dd-brand-mark">⌂</span>
          <span>
            <strong>Digii-Darshan</strong>
            <small>Crowd AI</small>
          </span>
        </Link>

        <nav>
          <Link href="/">Home</Link>
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
        </nav>
      </header>

      <section className="dd-login-shell">
        <div className="dd-login-intro">
          <p>Role Based Access</p>

          <h1>
            Enter the correct
            <span> command portal.</span>
          </h1>

          <p className="dd-login-desc">
            Pilgrims, admins, kiosk operators and scanner staff each open their
            own dedicated dashboard after login.
          </p>

          <div className="dd-demo-grid">
            {demoUsers.map((user) => (
              <button key={user.email} onClick={() => fillUser(user)} type="button">
                <strong>{user.label}</strong>
                <span>{user.desc}</span>
                <small>{user.email}</small>
              </button>
            ))}
          </div>
        </div>

        <div className="dd-login-card">
          <p className="dd-login-label">Login</p>

          <h2>Access dashboard</h2>

          {message ? <div className="dd-login-message">{message}</div> : null}

          <div>
            <label>Email</label>
            <input
              value={email}
              type="email"
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
            />

            <label>Password</label>
            <input
              value={password}
              type="password"
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              onKeyDown={(event) => {
                if (event.key === "Enter") handleLogin();
              }}
            />

            <button disabled={loading} type="button" onClick={handleLogin}>
              {loading ? "Authenticating..." : "Enter Portal"}
            </button>
          </div>

          <p className="dd-register-line">
            New pilgrim? <Link href="/register">Create account</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
