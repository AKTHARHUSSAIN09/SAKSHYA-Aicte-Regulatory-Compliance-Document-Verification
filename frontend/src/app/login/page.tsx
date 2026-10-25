"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight, LockKeyhole, Scale, ShieldCheck, Eye, EyeOff } from "lucide-react";
import { API_BASE } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("officer@sakshya.gov.in");
  const [password, setPassword] = useState("Sakshya@2026");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error();
      const session = await res.json();
      sessionStorage.setItem("sakshya_session", JSON.stringify(session));
      router.push("/");
    } catch {
      setError("We could not verify those credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      className="min-h-screen flex items-center justify-center p-5"
      style={{ background: "#F4F5FA" }}
    >
      {/* Background radials */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 20% 20%, rgba(99,102,241,0.18) 0%, transparent 55%)," +
            "radial-gradient(ellipse 50% 45% at 80% 80%, rgba(34,211,238,0.10) 0%, transparent 50%)",
        }}
      />

      <div
        className="relative z-10 w-full max-w-5xl rounded-2xl overflow-hidden grid lg:grid-cols-[1fr_1fr]"
        style={{
          background: "rgba(9,14,26,0.95)",
          border: "1px solid rgba(15,21,53,0.128)",
          boxShadow: "0 32px 80px rgba(0,0,0,0.6)",
        }}
      >
        {/* Left panel */}
        <div
          className="hidden lg:flex flex-col justify-between p-10 relative overflow-hidden"
          style={{
            background: "linear-gradient(160deg, rgba(30,42,120,0.08) 0%, rgba(37,99,235,0.05) 100%)",
            borderRight: "1px solid rgba(30,42,120,0.08)",
          }}
        >
          {/* Noise texture */}
          <div className="absolute inset-0 opacity-[0.03]" />

          {/* Brand */}
          <Link href="/landing" className="flex items-center gap-3">
            <span
              className="w-9 h-9 rounded-full flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, #151F5C, #1E2A78)",
                boxShadow: "0 4px 14px rgba(30,42,120,0.3)",
              }}
            >
              <Scale className="w-4 h-4" style={{ color: "#ffffff" }} />
            </span>
            <b
              className="tracking-[0.2em] text-sm font-black"
              style={{
                background: "linear-gradient(90deg, #1E2A78, #3347B0)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              SAKSHYA
            </b>
          </Link>

          {/* Hero text */}
          <div className="space-y-5">
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center"
              style={{
                background: "rgba(30,42,120,0.1)",
                border: "1px solid rgba(30,42,120,0.2)",
              }}
            >
              <ShieldCheck className="w-5 h-5" style={{ color: "#1E2A78" }} />
            </div>
            <h1 className="text-4xl font-black leading-tight" style={{ color: "#0F1535" }}>
              Scrutiny, with a<br />chain of proof.
            </h1>
            <p className="text-sm leading-relaxed text-slate-600 max-w-sm">
              A governed workspace for evidence, rules, human review,
              and final regulatory decisions.
            </p>

            {/* Feature list */}
            <div className="space-y-2.5 pt-2">
              {[
                "Deterministic Z3 compliance proofs",
                "Multi-layer document forensics",
                "Immutable audit trail",
              ].map((f) => (
                <div key={f} className="flex items-center gap-3 text-sm" style={{ color: "#4A5170" }}>
                  <div
                    className="w-5 h-5 rounded-full flex items-center justify-center shrink-0"
                    style={{ background: "rgba(30,42,120,0.15)" }}
                  >
                    <div className="w-1.5 h-1.5 rounded-full" style={{ background: "#1E2A78" }} />
                  </div>
                  {f}
                </div>
              ))}
            </div>
          </div>

          <p className="text-[10px] text-slate-600">
            Restricted workspace · Authorized users only
          </p>
        </div>

        {/* ─── Right: Login form ─────────────────── */}
        <div className="flex items-center justify-center p-8 sm:p-12">
          <form onSubmit={submit} className="w-full max-w-sm space-y-6">
            {/* Mobile logo */}
            <Link href="/landing" className="flex items-center gap-2 mb-8 lg:hidden">
              <Scale className="w-5 h-5 text-indigo-400" />
              <b className="tracking-[0.14em] text-slate-900 text-sm">SAKSHYA</b>
            </Link>

            <div>
              <p className="page-eyebrow mb-3">Secure Access</p>
              <h2 className="text-2xl font-black" style={{ color: "#0F1535" }}>Welcome back.</h2>
              <p className="text-sm mt-1.5" style={{ color: "var(--text-secondary)" }}>
                Sign in to continue to the regulatory workspace.
              </p>
            </div>

            {/* Fields */}
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                  Official Email
                </label>
                <input
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  type="email"
                  autoComplete="email"
                  className="field"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <input
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    type={showPass ? "text" : "password"}
                    autoComplete="current-password"
                    className="field pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700"
                  >
                    {showPass ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div
                className="rounded-xl p-3 text-xs text-rose-700"
                style={{
                  background: "rgba(244,63,94,0.08)",
                  border: "1px solid rgba(244,63,94,0.25)",
                }}
              >
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full justify-center py-3 text-sm"
              style={{ fontSize: "0.875rem" }}
            >
              {loading ? "Verifying access…" : "Enter workspace"}
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>

            {/* Demo note */}
            <div
              className="rounded-xl p-3.5 flex items-start gap-2.5 text-xs"
              style={{
                background: "rgba(15,21,53,0.048)",
                border: "1px solid rgba(15,21,53,0.112)",
              }}
            >
              <LockKeyhole className="w-3.5 h-3.5 text-indigo-700 mt-0.5 shrink-0" />
              <span className="text-slate-500">
                Demo officer credentials are pre-filled. Production use requires
                approved SSO authentication.
              </span>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}
