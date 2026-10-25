"use client";

import { useEffect, useState } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import { API_BASE } from "@/lib/api";
import { Clock, ArrowRight, RefreshCw, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";

export default function RegulatoryTimeMachinePage() {
  const [appId, setAppId] = useState("AICTE-2024-FRAUD-002");
  const [land, setLand] = useState("2.8");
  const [fireValid, setFireValid] = useState(true);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const selected = localStorage.getItem("sakshya_active_application");
    if (selected) setAppId(selected);
  }, []);

  const runScenario = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/applications/${appId}/time-machine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          label: "Officer correction scenario",
          corrections: { land_area_acres: Number(land), fire_safety_noc_valid: fireValid },
        }),
      });
      if (!res.ok) throw new Error();
      setResult(await res.json());
    } catch {
      alert("Could not run the comparison. Confirm the API service is running.");
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (s: string) =>
    s?.includes("COMPLIANT") || s?.includes("APPROVE")
      ? "#10b981"
      : s?.includes("REJECT") || s?.includes("DEFICIENT")
      ? "#f43f5e"
      : "#f59e0b";

  return (
    <SidebarLayout>
      <div className="space-y-7">
        {/* ── Header ─────────────────────────────── */}
        <div>
          <p className="page-eyebrow mb-2">
            <Clock className="w-3.5 h-3.5" />
            Historical Assessment Reconstruction
          </p>
          <h1 className="page-title">Regulatory Time Machine</h1>
          <p className="page-subtitle mt-1.5 max-w-2xl">
            Run a non-persistent correction scenario and compare its rule-by-rule outcome
            with recorded application facts. Final decisions remain with authorized officers.
          </p>
        </div>

        {/* ── Scenario builder ─────────────────────── */}
        <div
          className="rounded-xl p-6 space-y-5"
          style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="pb-4"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
          >
            <h2 className="text-sm font-bold text-white">Correction Scenario Builder</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Adjust parameters below and run a hypothetical re-assessment
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1.5 font-medium">
                Application ID
              </label>
              <input
                value={appId}
                onChange={(e) => setAppId(e.target.value)}
                className="field font-mono"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1.5 font-medium">
                Corrected Land Area (acres)
              </label>
              <input
                type="number"
                step="0.05"
                value={land}
                onChange={(e) => setLand(e.target.value)}
                className="field"
              />
            </div>
            <div className="flex flex-col justify-end">
              <label
                className="flex items-center gap-3 p-3.5 rounded-xl cursor-pointer"
                style={{ border: "1px solid rgba(255,255,255,0.07)", background: "rgba(255,255,255,0.03)" }}
              >
                <input
                  type="checkbox"
                  checked={fireValid}
                  onChange={(e) => setFireValid(e.target.checked)}
                  className="w-4 h-4 accent-indigo-500"
                />
                <span className="text-xs text-slate-300 font-medium">
                  Fire NOC is valid
                </span>
              </label>
            </div>
          </div>

          <button
            onClick={runScenario}
            disabled={loading}
            className="btn btn-primary w-full justify-center py-3"
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Reconstructing assessment…
              </>
            ) : (
              <>
                Run Scenario Comparison
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {/* ── Results ─────────────────────────────── */}
        {result && (
          <div className="space-y-5">
            {/* Outcome comparison */}
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { label: "Recorded Outcome", status: result.baseline_status, deficiencies: result.baseline_deficiencies, note: "Original application facts" },
                { label: "Corrected Scenario", status: result.projected_status, deficiencies: result.projected_deficiencies, note: "With your applied corrections" },
              ].map(({ label, status, deficiencies, note }) => (
                <div
                  key={label}
                  className="rounded-xl p-5 space-y-3"
                  style={{
                    background: "var(--bg-surface)",
                    border: `1px solid ${statusColor(status)}30`,
                  }}
                >
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider">{note}</div>
                    <div className="text-sm font-bold text-white mt-0.5">{label}</div>
                  </div>
                  <div
                    className="text-xl font-black"
                    style={{ color: statusColor(status) }}
                  >
                    {status}
                  </div>
                  <div className="text-xs text-slate-400">
                    {deficiencies} deficienc{deficiencies === 1 ? "y" : "ies"}
                  </div>
                </div>
              ))}
            </div>

            {/* Rule changes */}
            <div
              className="rounded-xl overflow-hidden"
              style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
            >
              <div
                className="px-6 py-4"
                style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
              >
                <h3 className="text-sm font-bold text-white">Rule Outcome Changes</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Rules whose status flipped between the two scenarios
                </p>
              </div>

              <div className="p-6">
                {result.rule_changes?.length ? (
                  <div className="space-y-2.5">
                    {result.rule_changes.map((change: any) => (
                      <div
                        key={change.rule_id}
                        className="flex items-center gap-4 rounded-xl p-4"
                        style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}
                      >
                        <span className="font-mono text-xs text-indigo-400 font-bold w-40 shrink-0">
                          {change.rule_id}
                        </span>
                        <div className="flex items-center gap-3 text-xs">
                          <span
                            className="badge"
                            style={{
                              background: `${statusColor(change.before)}18`,
                              color: statusColor(change.before),
                              border: `1px solid ${statusColor(change.before)}30`,
                            }}
                          >
                            {change.before}
                          </span>
                          <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                          <span
                            className="badge"
                            style={{
                              background: `${statusColor(change.after)}18`,
                              color: statusColor(change.after),
                              border: `1px solid ${statusColor(change.after)}30`,
                            }}
                          >
                            {change.after}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle2 className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                    <p className="text-sm text-slate-500">
                      No rule outcomes changed for this scenario.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </SidebarLayout>
  );
}
