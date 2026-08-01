"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import gsap from "gsap";

const modules = [
  {
    title: "DigiQueue",
    tag: "Booking Layer",
    desc: "QR darshan booking, slot allocation, kiosk passes and scanner validation.",
  },
  {
    title: "CrowdControl",
    tag: "Live Density",
    desc: "Real-time occupancy, inflow-outflow, pressure status and crowd risk.",
  },
  {
    title: "AI Prediction",
    tag: "Forecast Engine",
    desc: "Predictive temple crowd intelligence for upcoming slot pressure and congestion.",
  },
  {
    title: "Digi Suraksha",
    tag: "Emergency Layer",
    desc: "SOS alerts, emergency response, safety routing and command escalation.",
  },
  {
    title: "Flowmaster",
    tag: "Movement Control",
    desc: "Gate pressure, route diversion, parking control and crowd-flow actions.",
  },
  {
    title: "SeniorSathi",
    tag: "Assisted Darshan",
    desc: "Priority support for senior citizens and differently-abled pilgrims.",
  },
];

const flow = [
  "Pilgrim books QR darshan slot",
  "Live crowd engine checks temple density",
  "AI predicts risk and pressure zones",
  "Scanner validates check-in and check-out",
  "Admin triggers route and gate actions",
  "SOS and SeniorSathi teams respond",
];

function IntelligenceCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!canvas || !ctx) return;

    let raf = 0;
    let time = 0;

    const particles = Array.from({ length: 58 }, () => ({
      x: Math.random(),
      y: Math.random(),
      vx: (Math.random() - 0.5) * 0.00042,
      vy: (Math.random() - 0.5) * 0.00042,
      r: Math.random() * 1.7 + 0.5,
      glow: Math.random() * Math.PI * 2,
    }));

    function resize() {
      const ratio = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * ratio;
      canvas.height = window.innerHeight * ratio;
    }

    function draw() {
      const ratio = window.devicePixelRatio || 1;
      const width = canvas.width;
      const height = canvas.height;

      time += 0.012;

      ctx.clearRect(0, 0, width, height);

      particles.forEach((point, index) => {
        point.x += point.vx;
        point.y += point.vy;

        if (point.x < 0.02 || point.x > 0.98) point.vx *= -1;
        if (point.y < 0.02 || point.y > 0.98) point.vy *= -1;

        const x = point.x * width;
        const y = point.y * height;
        const pulse = 0.18 + Math.sin(time + point.glow) * 0.12;

        ctx.beginPath();
        ctx.arc(x, y, point.r * ratio, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(214, 196, 166, ${0.24 + pulse})`;
        ctx.fill();

        for (let j = index + 1; j < particles.length; j++) {
          const next = particles[j];
          const nx = next.x * width;
          const ny = next.y * height;
          const dx = x - nx;
          const dy = y - ny;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const limit = 150 * ratio;

          if (distance < limit) {
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(nx, ny);
            ctx.strokeStyle = `rgba(214, 196, 166, ${
              0.09 * (1 - distance / limit)
            })`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      });

      raf = requestAnimationFrame(draw);
    }

    resize();
    draw();

    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="ddx-canvas" />;
}

export default function HomePage() {
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".ddx-nav",
        { opacity: 0, y: -28 },
        { opacity: 1, y: 0, duration: 0.9, ease: "power3.out" }
      );

      gsap.fromTo(
        ".ddx-kicker",
        { opacity: 0, y: 22, filter: "blur(12px)" },
        {
          opacity: 1,
          y: 0,
          filter: "blur(0px)",
          duration: 0.9,
          delay: 0.15,
          ease: "power3.out",
        }
      );

      gsap.fromTo(
        ".ddx-title-part",
        { opacity: 0, y: 90, filter: "blur(18px)" },
        {
          opacity: 1,
          y: 0,
          filter: "blur(0px)",
          duration: 1.18,
          stagger: 0.1,
          delay: 0.28,
          ease: "power4.out",
        }
      );

      gsap.fromTo(
        ".ddx-hero-reveal",
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          duration: 0.86,
          stagger: 0.08,
          delay: 0.88,
          ease: "power3.out",
        }
      );

      gsap.to(".ddx-glow", {
        scale: 1.08,
        opacity: 0.78,
        duration: 3.8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      gsap.to(".ddx-scan-line", {
        xPercent: 24,
        duration: 7,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      gsap.set(".ddx-reveal", {
        opacity: 0,
        y: 56,
      });

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;

            gsap.to(entry.target, {
              opacity: 1,
              y: 0,
              duration: 0.85,
              ease: "power3.out",
            });

            observer.unobserve(entry.target);
          });
        },
        {
          threshold: 0.18,
        }
      );

      document.querySelectorAll(".ddx-reveal").forEach((el) => {
        observer.observe(el);
      });

      return () => observer.disconnect();
    });

    return () => ctx.revert();
  }, []);

  return (
    <main className="ddx-root">
      <video
        className="ddx-video"
        src="/videos/digidarshan-hero.mp4"
        autoPlay
        muted
        loop
        playsInline
      />

      <div className="ddx-vignette" />
      <div className="ddx-bottom-fade" />
      <div className="ddx-grain" />
      <IntelligenceCanvas />

      <header className="ddx-nav">
        <Link href="/" className="ddx-brand">
          <span className="ddx-brand-icon">⌂</span>

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

      <section className="ddx-hero">
        <div className="ddx-glow" />

        <div className="ddx-hero-inner">
          <p className="ddx-kicker">AI Temple Crowd Intelligence</p>

          <h1 className="ddx-title">
            <span className="ddx-title-part">DIGII</span>
            <strong className="ddx-title-part">DARSHAN</strong>
          </h1>

          <p className="ddx-subtitle ddx-hero-reveal">
            Smart Pilgrimage Command System
          </p>

          <p className="ddx-copy ddx-hero-reveal">
            QR darshan booking, live crowd prediction, gate-flow control,
            emergency response, SeniorSathi support and AI-guided temple
            operations.
          </p>

          <div className="ddx-actions ddx-hero-reveal">
            <Link href="/login">Enter Portal</Link>
            <a href="#architecture">Explore Architecture</a>
          </div>
        </div>
      </section>

      <section id="architecture" className="ddx-architecture">
        <div className="ddx-scan-line" />

        <div className="ddx-section-head ddx-reveal">
          <p>Platform Architecture</p>

          <h2>
            A real-time operating system
            <span>for pilgrimage crowd intelligence.</span>
          </h2>
        </div>

        <div className="ddx-command-grid">
          <div className="ddx-command-card ddx-reveal">
            <p className="ddx-mini">Command Flow</p>

            <h3>
              Every booking, movement and alert becomes visible before pressure
              becomes danger.
            </h3>

            <p>
              Digii-Darshan connects pilgrim booking, kiosk counters, scanner
              gates, admin control rooms, SOS response and SeniorSathi support
              into one live intelligence layer.
            </p>
          </div>

          <div className="ddx-flow-card ddx-reveal">
            {flow.map((item, index) => (
              <div className="ddx-flow-row" key={item}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{item}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="ddx-module-grid">
          {modules.map((module, index) => (
            <article className="ddx-module ddx-reveal" key={module.title}>
              <small>{module.tag}</small>
              <h3>{module.title}</h3>
              <p>{module.desc}</p>
              <b>{String(index + 1).padStart(2, "0")}</b>
            </article>
          ))}
        </div>
      </section>

      <section className="ddx-intelligence">
        <div className="ddx-intel-inner ddx-reveal">
          <div>
            <p className="ddx-mini">Intelligence Layer</p>

            <h2>Live crowd status, AI predictions, heatmaps and SOS alerts.</h2>
          </div>

          <div className="ddx-stats">
            <div>
              <strong>04</strong>
              <span>Temple Panels</span>
            </div>

            <div>
              <strong>06</strong>
              <span>Core Modules</span>
            </div>

            <div>
              <strong>24/7</strong>
              <span>Command View</span>
            </div>
          </div>
        </div>
      </section>

      <section className="ddx-footer">
        <video
          className="ddx-footer-video"
          src="/videos/digidarshan-hero.mp4"
          autoPlay
          muted
          loop
          playsInline
        />

        <div className="ddx-footer-overlay" />

        <div className="ddx-footer-content ddx-reveal">
          <p>Live Prototype</p>

          <h2>Built for crowd intelligence, not just ticket booking.</h2>

          <Link href="/login">Launch Digii-Darshan</Link>
        </div>
      </section>
    </main>
  );
}
