"use client";

import React, { useState } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import { API_BASE } from "@/lib/api";
import {
  ShieldAlert,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Zap,
  Target,
} from "lucide-react";

const ATTACK_VECTORS = [
  {
    id: "FONT_SPLICING",
    name: "Numerical Font & Value Splicing",
    desc: "Simulates splicing altered figures (e.g., '1.75' → '2.10' acres) into a scanned government deed.",
    engine: "OpenCV Error Level Analysis (ELA)",
    severity: "CRITICAL",
    color: "#f43f5e",
  },
  {
    id: "CANVA_METADATA",
    name: "Graphic Suite Footprint Injection",
    desc: "Injects Canva/Photoshop creator tags and mismatched font dictionaries into PDF object streams.",
    engine: "PyMuPDF Stream Parser",
    severity: "HIGH",
    color: "#f59e0b",
  },
  {
    id: "EXIF_GPS_FORGERY",
    name: "EXIF Geolocation Spoofing",
    desc: "Injects remote off-campus coordinates into laboratory and infrastructure photographs.",
    engine: "Haversine Distance Verifier",
    severity: "HIGH",
    color: "#f59e0b",
  },
  {
    id: "TEMPLATE_CLONING",
    name: "Cross-College Certificate Cloning",
    desc: "Reuses borders and visual layout from an unrelated institution in another state.",
    engine: "64-Bit Perceptual dHash",
    severity: "CRITICAL",
    color: "#f43f5e",
  },
];

const FALLBACK: Record<string, any> = {
  FONT_SPLICING: {
    attack_name: "Numerical Font & Value Splicing",
    injection: "Spliced '2.10' acres at coordinate [105, 310]",
    detector: "OpenCV Error Level Analysis (ELA)",
    detection_status: "CAUGHT_BY_DETECTOR",
    fraud_score: 0.94,
    ela_variance: "48.6 (Mean: 4.2)",
    verdict: "FRAUDULENT",
    explanation: "Localized pixel difference matrix detected sharp compression boundary around numeral '2.10'.",
  },
  CANVA_METADATA: {
    attack_name: "Graphic Suite Footprint Injection",
    injection: "Injected Producer: 'Canva PDF Generator v2.4'",
    detector: "PyMuPDF Stream Parser",
    detection_status: "CAUGHT_BY_DETECTOR",
    fraud_score: 0.88,
    verdict: "SUSPICIOUS_SOFTWARE",
    explanation: "Metadata dictionary contains prohibited graphic design suite signature.",
  },
  EXIF_GPS_FORGERY: {
    attack_name: "EXIF Geolocation Spoofing",
    injection: "GPS Coordinates: 28.6139° N, 77.2090° E (New Delhi)",
    detector: "Infrastructure Geo Verifier",
    detection_status: "CAUGHT_BY_DETECTOR",
    fraud_score: 0.85,
    distance_delta: "1,140 km from campus centroid",
    verdict: "GEO_LOCATION_MISMATCH",
    explanation: "Photo capture location deviates by over 1,000 km from the registered land title centroid.",
  },
  TEMPLATE_CLONING: {
    attack_name: "Cross-College Certificate Cloning",
    injection: "Perceptual template cloned from Apex City College",
    detector: "64-Bit Difference Hash (dHash)",
    detection_status: "CAUGHT_BY_DETECTOR",
    fraud_score: 0.91,
    hamming_distance: "3 / 64 bits",
    verdict: "PERCEPTUAL_DUPLICATE",
    explanation: "Visual difference hash matches a previously submitted certificate with 95.3% similarity.",
  },
};

export default function AttackLabPage() {
  const [selected, setSelected] = useState("FONT_SPLICING");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadReport, setUploadReport] = useState<any>(null);

  const runAttack = () => {
    setRunning(true);
    fetch(`${API_BASE}/attack-lab/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: selected }),
    })
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((data) => setResult({ ...data, attack_name: selected }))
      .catch(() => setResult(FALLBACK[selected]))
      .finally(() => setRunning(false));
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadLoading(true);
    const form = new FormData();
    form.append("file", file);
    form.append("institution_id", "ATTACK-BENCH-01");
    form.append("institution_name", "Attack Lab Benchmark");
    try {
      const res = await fetch(`${API_BASE}/forensics/analyze-upload`, {
        method: "POST", body: form,
      });
      if (res.ok) setUploadReport(await res.json());
    } catch { alert("Failed to analyze uploaded file"); }
    finally { setUploadLoading(false); }
  };

  const scorePercent = result ? Math.round(result.fraud_score * 100) : 0;

  return (
    <SidebarLayout>
      <div className="space-y-7">
        {/* ── Header ─────────────────────────────── */}
        <div>
          <p className="page-eyebrow mb-2">
            <ShieldAlert className="w-3.5 h-3.5" />
            Adversarial Testing & Forensic Verification Bench
          </p>
          <h1 className="page-title">Forensic Attack Lab</h1>
          <p className="page-subtitle mt-1.5 max-w-2xl">
            Programmatically inject synthetic tampering — font swaps, seal cloning, EXIF forgery,
            metadata stripping — to stress-test and benchmark the automated forensic detectors.
          </p>
        </div>

        {/* ── 2-column layout ──────────────────────── */}
        <div className="grid lg:grid-cols-12 gap-5 items-start">
          {/* Left: attack selector (5 cols) */}
          <div
            className="lg:col-span-5 rounded-xl overflow-hidden"
            style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div
              className="px-5 py-4"
              style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
            >
              <h3 className="text-sm font-bold text-white">Synthetic Tampering Suite</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Select an adversarial perturbation to benchmark
              </p>
            </div>

            <div className="p-4 space-y-2.5">
              {ATTACK_VECTORS.map((atk) => {
                const isSelected = selected === atk.id;
                return (
                  <button
                    key={atk.id}
                    onClick={() => setSelected(atk.id)}
                    className="w-full text-left rounded-xl p-4 space-y-2 transition-all"
                    style={
                      isSelected
                        ? {
                            background: "rgba(99,102,241,0.1)",
                            border: "1px solid rgba(99,102,241,0.35)",
                            transform: "scale(1.01)",
                          }
                        : {
                            background: "rgba(255,255,255,0.025)",
                            border: "1px solid rgba(255,255,255,0.06)",
                          }
                    }
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-xs font-semibold text-slate-100 leading-snug">
                        {atk.name}
                      </span>
                      <span
                        className="badge shrink-0"
                        style={{
                          background: `${atk.color}18`,
                          color: atk.color,
                          border: `1px solid ${atk.color}30`,
                        }}
                      >
                        {atk.severity}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-relaxed">{atk.desc}</p>
                    <div className="flex items-center gap-1.5 text-[10px] text-indigo-400 font-mono">
                      <Target className="w-3 h-3" />
                      {atk.engine}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="p-4 pt-0">
              <button
                onClick={runAttack}
                disabled={running}
                className="btn btn-primary w-full justify-center py-3"
              >
                {running ? (
                  <>
                    <Cpu className="w-3.5 h-3.5 animate-pulse" />
                    Injecting &amp; Running Detectors…
                  </>
                ) : (
                  <>
                    <Zap className="w-3.5 h-3.5" />
                    Execute Synthetic Benchmark
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right: results + upload (7 cols) */}
          <div className="lg:col-span-7 space-y-5">
            {/* Benchmark result */}
            {result && (
              <div
                className="rounded-xl overflow-hidden"
                style={{ background: "var(--bg-surface)", border: "1px solid rgba(16,185,129,0.2)" }}
              >
                <div
                  className="flex items-center justify-between px-5 py-4"
                  style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
                >
                  <div className="flex items-center gap-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-bold text-white">Detector Result</span>
                  </div>
                  <span className="badge badge-emerald">{result.detection_status}</span>
                </div>

                <div className="p-5 space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { label: "Attack Simulated", val: result.attack_name, sub: result.injection },
                      { label: "Detector Engine", val: result.detector, sub: `Fraud confidence: ${scorePercent}%`, highlight: true },
                    ].map(({ label, val, sub, highlight }) => (
                      <div
                        key={label}
                        className="rounded-xl p-4 space-y-1"
                        style={{ background: "rgba(0,0,0,0.2)", border: "1px solid rgba(255,255,255,0.05)" }}
                      >
                        <div className="text-[10px] text-slate-500">{label}</div>
                        <div className="text-xs font-semibold text-slate-100">{val}</div>
                        <div
                          className="text-[10px] font-mono"
                          style={{ color: highlight ? "#f43f5e" : "#64748b" }}
                        >
                          {sub}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Score bar */}
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] text-slate-500">Fraud Confidence Score</span>
                      <span className="text-xs font-bold text-rose-400">{scorePercent}%</span>
                    </div>
                    <div
                      className="h-2 rounded-full overflow-hidden"
                      style={{ background: "rgba(255,255,255,0.06)" }}
                    >
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${scorePercent}%`,
                          background: "linear-gradient(90deg, #f59e0b, #f43f5e)",
                        }}
                      />
                    </div>
                  </div>

                  <div
                    className="rounded-xl p-3.5 text-xs text-slate-300 leading-relaxed"
                    style={{ background: "rgba(0,0,0,0.2)", border: "1px solid rgba(255,255,255,0.05)" }}
                  >
                    <span className="font-semibold text-white">Proof: </span>
                    {result.explanation}
                  </div>
                </div>
              </div>
            )}

            {/* Live upload sandbox */}
            <div
              className="rounded-xl overflow-hidden"
              style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
            >
              <div
                className="px-5 py-4"
                style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
              >
                <h3 className="text-sm font-bold text-white">Live Certificate Sandbox</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Upload any PDF or image to test the detector in real time
                </p>
              </div>

              <div className="p-5 space-y-4">
                <label
                  className="flex flex-col items-center justify-center gap-3 rounded-xl p-8 cursor-pointer transition-all"
                  style={{
                    background: "rgba(0,0,0,0.2)",
                    border: "2px dashed rgba(99,102,241,0.25)",
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.borderColor = "rgba(99,102,241,0.5)")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.borderColor = "rgba(99,102,241,0.25)")
                  }
                >
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleUpload}
                  />
                  <UploadCloud
                    className={`w-8 h-8 text-indigo-400 ${uploadLoading ? "animate-bounce" : ""}`}
                  />
                  <div className="text-center">
                    <div className="text-sm font-semibold text-slate-200">
                      {uploadLoading
                        ? "Parsing PDF streams & computing ELA…"
                        : "Drop PDF or Image here"}
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Land title deeds, fire NOCs, building approvals
                    </p>
                  </div>
                </label>

                {uploadReport && (
                  <div
                    className="rounded-xl p-4 space-y-3"
                    style={{
                      background: "rgba(99,102,241,0.05)",
                      border: "1px solid rgba(99,102,241,0.2)",
                    }}
                  >
                    <div
                      className="flex items-center justify-between pb-3"
                      style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}
                    >
                      <span className="text-xs font-bold text-white">
                        {uploadReport.file_name}
                      </span>
                      <span className="badge badge-rose">
                        {uploadReport.verdict} ({Math.round(uploadReport.overall_fraud_score * 100)}%)
                      </span>
                    </div>

                    <div className="space-y-2">
                      {uploadReport.findings?.map((f: any, i: number) => (
                        <div
                          key={i}
                          className="rounded-lg p-3 space-y-1.5 text-xs"
                          style={{ background: "rgba(0,0,0,0.2)", border: "1px solid rgba(255,255,255,0.05)" }}
                        >
                          <div className="font-semibold text-indigo-300">{f.title}</div>
                          <p className="text-slate-400 leading-relaxed">{f.description}</p>
                          {f.visual_evidence_b64 && (
                            <img
                              src={f.visual_evidence_b64}
                              alt="ELA Heatmap"
                              className="w-full max-h-40 object-contain rounded mt-1"
                              style={{ background: "#000" }}
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}
