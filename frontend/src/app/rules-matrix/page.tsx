"use client";

import React, { useState, useEffect } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import ApplicationPicker from "@/components/ApplicationPicker";
import { API_BASE } from "@/lib/api";
import { Cpu, AlertTriangle, CheckCircle2, Sparkles, X } from "lucide-react";

export default function RulesMatrixPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [modalOpen, setModalOpen] = useState(false);
  const [activeConflict, setActiveConflict] = useState<any>(null);
  const [winner, setWinner] = useState("");
  const [justification, setJustification] = useState("");
  const [applicationId, setApplicationId] = useState("AICTE-2024-FRAUD-002");
  const [assessment, setAssessment] = useState<any>(null);

  useEffect(() => { load(); }, []);
  useEffect(() => setApplicationId(localStorage.getItem("sakshya_active_application") ?? "AICTE-2024-FRAUD-002"), []);
  useEffect(() => {
    setAssessment(null);
    fetch(`${API_BASE}/audit/run/${applicationId}`, { method: "POST" })
      .then((response) => response.ok ? response.json() : null)
      .then(setAssessment)
      .catch(() => setAssessment(null));
  }, [applicationId]);

  const load = async () => {
    setLoading(true);
    try {
      const [rRes, cRes] = await Promise.all([
        fetch(`${API_BASE}/rules`),
        fetch(`${API_BASE}/rules/conflicts`),
      ]);
      if (rRes.ok) setRules(await rRes.json());
      if (cRes.ok) setConflicts(await cRes.json());
    } catch { /* silent */ }
    finally { setLoading(false); }
  };

  const handleOverride = async () => {
    if (!activeConflict || !winner) return;
    try {
      const res = await fetch(`${API_BASE}/rules/override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conflict_id: activeConflict.conflict_id,
          winning_rule_id: winner,
          admin_officer_id: "AICTE_REGIONAL_DIRECTOR",
          justification_note: justification || "Authorized regulatory circular precedence override.",
        }),
      });
      if (res.ok) { setModalOpen(false); load(); }
    } catch { alert("Override failed"); }
  };

  const CATEGORY_COLORS: Record<string, string> = {
    LAND: "#f59e0b",
    FACULTY: "#a855f7",
    DOCUMENTS: "#22d3ee",
    INFRASTRUCTURE: "#6366f1",
    FINANCE: "#10b981",
  };

  return (
    <SidebarLayout>
      <div className="space-y-7">
        {/* ── Header ─────────────────────────────── */}
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
          <p className="page-eyebrow mb-2">
            <Cpu className="w-3.5 h-3.5" />
            Microsoft Research Z3 SMT Theorem Prover
          </p>
          <h1 className="page-title">Rule Conflict Matrix</h1>
          <p className="page-subtitle mt-1.5 max-w-2xl">
            Formally converts AICTE Approval Process Handbook clauses and supplementary circulars
            into SMT assertions to mathematically detect contradictory or overlapping constraints.
          </p>
          </div>
          <ApplicationPicker value={applicationId} onChange={setApplicationId} />
        </div>

        <div className="rounded-xl p-5" style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-sm font-bold text-white">Selected Institution: Z3 Assessment</h2><p className="mt-1 text-xs text-slate-500">Live rule evaluation for {applicationId}</p></div><span className={`badge ${assessment?.audit_report?.overall_status === "COMPLIANT" ? "badge-emerald" : "badge-rose"}`}>{assessment?.audit_report?.overall_status ?? "RUNNING"}</span></div>
          {assessment?.audit_report?.results && <div className="mt-4 grid gap-2 md:grid-cols-2">{assessment.audit_report.results.map((result: any) => <div key={result.rule_id} className="rounded-lg border border-white/5 bg-black/20 p-3"><div className="flex justify-between gap-2"><span className="text-xs font-semibold text-slate-200">{result.rule_title}</span><span className={`badge ${result.status === "COMPLIANT" ? "badge-emerald" : "badge-rose"}`}>{result.status}</span></div><p className="mt-1 text-[11px] text-slate-500">{result.explanation}</p></div>)}</div>}
        </div>

        {/* ── Conflict banners ─────────────────────── */}
        {conflicts.map((conf) => (
          <div
            key={conf.conflict_id}
            className="rounded-xl p-5 space-y-4"
            style={{ background: "rgba(245,158,11,0.05)", border: "1px solid rgba(245,158,11,0.2)" }}
          >
            {/* Conflict header */}
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div
                  className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: "rgba(245,158,11,0.12)" }}
                >
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-amber-200">
                    Regulatory Ambiguity · {conf.conflict_id}
                  </h3>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="badge badge-slate">{conf.category}</span>
                    <span className="badge badge-amber">{conf.conflict_type}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2.5">
                <span
                  className="badge"
                  style={
                    conf.override_active
                      ? { background: "rgba(16,185,129,0.1)", color: "#6ee7b7", border: "1px solid rgba(16,185,129,0.25)" }
                      : { background: "rgba(245,158,11,0.1)", color: "#fcd34d", border: "1px solid rgba(245,158,11,0.25)" }
                  }
                >
                  {conf.override_active ? "OVERRIDE RECORDED" : "AWAITING OVERRIDE"}
                </span>
                <button
                  onClick={() => {
                    setActiveConflict(conf);
                    setWinner(conf.rule_b_id);
                    setModalOpen(true);
                  }}
                  className="btn btn-primary"
                >
                  Configure Override
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">{conf.explanation}</p>

            {/* Rule comparison */}
            <div className="grid md:grid-cols-2 gap-3">
              {[
                { label: "Handbook Clause A", id: conf.rule_a_id, clause: conf.rule_a_clause },
                { label: "Supplementary Circular B", id: conf.rule_b_id, clause: conf.rule_b_clause },
              ].map(({ label, id, clause }) => (
                <div
                  key={id}
                  className="rounded-xl p-4 space-y-1.5"
                  style={{ background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)" }}
                >
                  <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">
                    {label}
                  </div>
                  <div className="font-mono text-xs text-slate-200 font-semibold">{id}</div>
                  <div className="text-[11px] text-slate-400 leading-relaxed">{clause}</div>
                </div>
              ))}
            </div>

            {/* Z3 counterexample */}
            {conf.counterexample_model && (
              <div
                className="rounded-xl p-4 flex items-start gap-3"
                style={{ background: "rgba(245,158,11,0.07)", border: "1px solid rgba(245,158,11,0.18)" }}
              >
                <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <p className="text-xs text-amber-200 leading-relaxed">
                  <span className="font-bold">Z3 Counterexample: </span>
                  At parameter value{" "}
                  <span className="font-mono font-bold text-white">
                    {conf.counterexample_model.counterexample_value} Acres
                  </span>
                  , an application satisfies Circular B but violates Handbook Rule A. The system
                  halts automated rejection until an officer records an explicit administrative override.
                </p>
              </div>
            )}
          </div>
        ))}

        {/* ── Rules table ─────────────────────────── */}
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="px-6 py-4"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
          >
            <h2 className="text-sm font-bold text-white">Active Regulatory Rule Matrix</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Formal logic representations evaluated across all applicant institutions
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="data-table px-6">
              <thead>
                <tr>
                  <th className="pl-6 text-left pr-4">Rule ID</th>
                  <th className="text-left pr-4">Category</th>
                  <th className="text-left pr-4">SMT Predicate</th>
                  <th className="text-left pr-4">Citation</th>
                  <th className="text-right pr-6">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i}>
                        {Array.from({ length: 5 }).map((_, j) => (
                          <td key={j} className={j === 0 ? "pl-6 pr-4" : j === 4 ? "pr-6" : "pr-4"}>
                            <div className="skeleton h-4 w-full max-w-[100px]" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : rules.map((r) => {
                      const catColor = CATEGORY_COLORS[r.category] || "#6366f1";
                      return (
                        <tr key={r.rule_id}>
                          <td className="pl-6 pr-4">
                            <span className="font-mono text-xs font-bold text-indigo-400">
                              {r.rule_id}
                            </span>
                          </td>
                          <td className="pr-4">
                            <span
                              className="badge text-[9px]"
                              style={{
                                background: `${catColor}15`,
                                color: catColor,
                                border: `1px solid ${catColor}28`,
                              }}
                            >
                              {r.category}
                            </span>
                          </td>
                          <td className="pr-4">
                            <span className="font-mono text-xs text-slate-300">
                              {r.variable_name} {r.operator} {JSON.stringify(r.target_value)}
                            </span>
                          </td>
                          <td className="pr-4">
                            <span className="text-xs text-slate-500">
                              {r.source?.document_name}{" "}
                              <span className="font-mono text-slate-600">
                                [{r.source?.clause_reference}]
                              </span>
                            </span>
                          </td>
                          <td className="pr-6 text-right">
                            <span className="badge badge-emerald">SAT</span>
                          </td>
                        </tr>
                      );
                    })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Override modal ─────────────────────────── */}
      {modalOpen && activeConflict && (
        <div className="modal-backdrop">
          <div className="modal-box">
            <div
              className="flex items-center justify-between pb-4 mb-5"
              style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}
            >
              <div>
                <h3 className="font-bold text-white">Record Precedence Override</h3>
                <p className="text-xs text-slate-500 mt-0.5 font-mono">
                  {activeConflict.conflict_id}
                </p>
              </div>
              <button
                onClick={() => setModalOpen(false)}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-500 hover:text-white hover:bg-white/10"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 mb-5">
              <p className="text-xs text-slate-400">
                Select which rule takes statutory precedence:
              </p>
              {[
                {
                  id: activeConflict.rule_b_id,
                  label: "Supplementary Circular (1.80 Acres relaxed)",
                },
                {
                  id: activeConflict.rule_a_id,
                  label: "Approval Process Handbook (2.50 Acres standard)",
                },
              ].map(({ id, label }) => (
                <label
                  key={id}
                  className="flex items-start gap-3 rounded-xl p-4 cursor-pointer transition"
                  style={{
                    background: winner === id ? "rgba(99,102,241,0.1)" : "rgba(255,255,255,0.03)",
                    border: winner === id
                      ? "1px solid rgba(99,102,241,0.35)"
                      : "1px solid rgba(255,255,255,0.07)",
                  }}
                >
                  <input
                    type="radio"
                    name="winner"
                    value={id}
                    checked={winner === id}
                    onChange={() => setWinner(id)}
                    className="mt-0.5 accent-indigo-500"
                  />
                  <div>
                    <div className="text-xs font-semibold text-white">{label}</div>
                    <div className="text-[10px] font-mono text-slate-500 mt-0.5">{id}</div>
                  </div>
                </label>
              ))}
            </div>

            <div className="mb-5">
              <label className="block text-xs text-slate-400 mb-1.5 font-medium">
                Administrative Justification
              </label>
              <input
                type="text"
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
                placeholder="e.g., Circular precedence approved pursuant to AICTE Notification…"
                className="field"
              />
            </div>

            <div
              className="flex justify-end gap-2.5 pt-4"
              style={{ borderTop: "1px solid rgba(255,255,255,0.07)" }}
            >
              <button onClick={() => setModalOpen(false)} className="btn btn-ghost">
                Cancel
              </button>
              <button onClick={handleOverride} className="btn btn-primary">
                Record Precedence
              </button>
            </div>
          </div>
        </div>
      )}
    </SidebarLayout>
  );
}
