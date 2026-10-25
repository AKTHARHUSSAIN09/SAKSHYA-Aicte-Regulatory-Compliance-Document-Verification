import Link from "next/link";
import { ArrowRight, Binary, FileCheck2, Network, Scale, ShieldCheck, Sparkles, CheckCircle } from "lucide-react";

const CAPABILITIES = [
  {
    Icon: Scale,
    title: "Deterministic Rules",
    body: "Z3-backed regulatory evaluation with clause-level evidence and formal mathematical proofs.",
    color: "#1E2A78",
  },
  {
    Icon: Network,
    title: "Evidence Intelligence",
    body: "Cross-document links, provenance tracing, anomaly detection and full chain-of-custody.",
    color: "#2563EB",
  },
  {
    Icon: ShieldCheck,
    title: "Human Authority",
    body: "Officer review, statutory notices and an immutable cryptographic decision audit trail.",
    color: "#059669",
  },
];

const STATS = [
  { value: "9", label: "Scrutiny Modules" },
  { value: "6", label: "Analysis Engines" },
  { value: "100%", label: "Traceable Evidence" },
];

const CHECKS = [
  "Land title evidence linked to registry record",
  "Fire NOC validity interval verified",
  "APH 2024 §4.1 evidence threshold evaluated",
];

export default function LandingPage() {
  return (
    <main
      className="min-h-screen overflow-x-hidden text-slate-800"
      style={{ background: "#F4F5FA" }}
    >
      {/* ── Background gradients ──────────────────── */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 70% 55% at 15% 0%, rgba(99,102,241,0.22) 0%, transparent 60%)," +
            "radial-gradient(ellipse 55% 45% at 85% 75%, rgba(34,211,238,0.12) 0%, transparent 55%)",
        }}
      />

      {/* ── Nav ──────────────────────────────────── */}
      <nav
        className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10"
      >
        <Link href="/landing" className="flex items-center gap-3">
          <span
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #4f46e5, #0891B2)",
              boxShadow: "0 4px 14px rgba(99,102,241,0.35)",
            }}
          >
            <Scale className="w-4.5 h-4.5 text-white" />
          </span>
          <span>
            <b className="text-slate-900 tracking-[0.14em] text-sm">SAKSHYA</b>
            <em
              className="block text-[9px] not-italic tracking-widest uppercase"
              style={{ color: "#475569" }}
            >
              Regulatory Intelligence
            </em>
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="hidden sm:block text-sm text-slate-600 hover:text-slate-900 transition px-3 py-1.5 rounded-lg hover:bg-slate-900/5"
          >
            Command Center
          </Link>
          <Link
            href="/login"
            className="btn btn-primary text-sm"
            style={{ padding: "0.5rem 1.1rem" }}
          >
            Secure sign in
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────── */}
      <section className="relative z-10 mx-auto grid max-w-7xl gap-14 px-6 pb-20 pt-8 lg:grid-cols-[1.1fr_.9fr] lg:px-10 lg:pt-14">
        {/* Left */}
        <div className="flex flex-col justify-center">
          <div
            className="inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-semibold mb-8 w-fit"
            style={{
              background: "rgba(30,42,120,0.07)",
              border: "1px solid rgba(30,42,120,0.18)",
              color: "#3347B0",
            }}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Evidence-first decision support
          </div>

          <h1
            className="text-5xl sm:text-6xl xl:text-7xl font-black leading-[0.95] tracking-tight"
            style={{ color: "#0F1535" }}
          >
            Make every approval
            <br />
            decision{" "}
            <span
              style={{
                background: "linear-gradient(90deg, #1E2A78, #3347B0, #F28C28)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              defensible.
            </span>
          </h1>

          <p className="mt-7 max-w-lg text-base leading-relaxed" style={{ color: "#64748b" }}>
            Sakshya brings formal regulatory logic, document forensics, and traceable evidence into one calm
            scrutiny workspace — built for decisions people can explain and courts can accept.
          </p>

          {/* CTA row */}
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              href="/login"
              className="btn btn-primary text-sm px-5 py-3"
              style={{ fontSize: "0.875rem", padding: "0.75rem 1.4rem" }}
            >
              Enter secure workspace
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/rules-matrix"
              className="btn btn-ghost text-sm"
              style={{ padding: "0.75rem 1.4rem", fontSize: "0.875rem" }}
            >
              Explore rule engine
            </Link>
          </div>

          {/* Stats row */}
          <div
            className="mt-12 flex gap-8 pt-7"
            style={{ borderTop: "1px solid rgba(30,42,120,0.1)" }}
          >
            {STATS.map(({ value, label }) => (
              <div key={label}>
                <div className="text-2xl font-black text-slate-900">{value}</div>
                <div className="text-xs text-slate-500 mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: UI preview card */}
        <div className="relative self-center">
          <div
            className="absolute -inset-8 rounded-[2rem] blur-3xl"
            style={{ background: "rgba(99,102,241,0.12)" }}
          />
          <div
            className="relative rounded-2xl p-5 space-y-4"
            style={{
              background: "rgba(11,17,32,0.9)",
              border: "1px solid rgba(15,21,53,0.128)",
              boxShadow: "0 24px 60px rgba(0,0,0,0.5)",
              backdropFilter: "blur(16px)",
            }}
          >
            {/* Card header */}
            <div
              className="flex items-center justify-between pb-4"
              style={{ borderBottom: "1px solid rgba(15,21,53,0.096)" }}
            >
              <div className="flex items-center gap-2.5">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ background: "#059669", boxShadow: "0 0 6px #059669" }}
                />
                <span className="text-xs font-bold" style={{ color: "#0F1535" }}>
                  Evidence Integrity Console
                </span>
              </div>
              <Binary className="w-4 h-4" style={{ color: "#1E2A78" }} />
            </div>

            {/* Check rows */}
            <div className="space-y-2.5">
              {CHECKS.map((text, i) => (
                <div
                  key={text}
                  className="flex items-center gap-3 rounded-xl p-3.5"
                  style={{
                    background: "rgba(0,0,0,0.25)",
                    border: "1px solid rgba(15,21,53,0.08)",
                  }}
                >
                  <span
                    className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                    style={
                      i === 1
                        ? { background: "rgba(180,83,9,0.12)" }
                        : { background: "rgba(16,185,129,0.1)" }
                    }
                  >
                    <FileCheck2
                      className="w-4 h-4"
                      style={{ color: i === 1 ? "#B45309" : "#059669" }}
                    />
                  </span>
                  <div>
                    <p className="text-xs font-semibold text-slate-800">{text}</p>
                    <p className="text-[10px] text-slate-500 mt-0.5">
                      Source anchored · Officer review ready
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Decision posture banner */}
            <div
              className="rounded-xl p-4"
              style={{
                background: "linear-gradient(90deg, rgba(30,42,120,0.18), rgba(30,42,120,0.08))",
                border: "1px solid rgba(30,42,120,0.22)",
              }}
            >
              <p
                className="text-[9px] font-bold uppercase tracking-widest"
                style={{ color: "#1E2A78" }}
              >
                Decision Posture
              </p>
              <p className="text-base font-bold mt-1" style={{ color: "#0F1535" }}>
                Human authority preserved
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Capabilities ─────────────────────────── */}
      <section className="relative z-10 mx-auto max-w-7xl grid gap-4 px-6 pb-24 lg:grid-cols-3 lg:px-10">
        {CAPABILITIES.map(({ Icon, title, body, color }) => (
          <article
            key={title}
            className="rounded-xl p-6 space-y-4"
            style={{
              background: "rgba(11,17,32,0.7)",
              border: "1px solid rgba(15,21,53,0.096)",
            }}
          >
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: `${color}18`, border: `1px solid ${color}30` }}
            >
              <Icon className="w-5 h-5" style={{ color }} />
            </div>
            <h2 className="font-bold text-slate-900">{title}</h2>
            <p className="text-sm leading-relaxed text-slate-600">{body}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
