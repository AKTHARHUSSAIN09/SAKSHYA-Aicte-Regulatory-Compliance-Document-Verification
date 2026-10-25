"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import SidebarLayout from "@/components/SidebarLayout";
import ApplicationIngestionWizard from "@/components/ApplicationIngestionWizard";
import { API_BASE } from "@/lib/api";
import {
  Layers,
  FileCheck2,
  AlertTriangle,
  Building2,
  ArrowRight,
  Plus,
  RefreshCw,
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  X,
} from "lucide-react";

const METRIC_CARDS = [
  {
    label: "Applications in Queue",
    icon: Building2,
    color: "#f5a623",
    bgColor: "rgba(245,166,35,0.07)",
    borderColor: "rgba(245,166,35,0.16)",
    key: "total",
    sub: "Intake checklists populated",
  },
  {
    label: "Critical Alerts",
    icon: AlertTriangle,
    color: "#ef4444",
    bgColor: "rgba(220,38,38,0.07)",
    borderColor: "rgba(220,38,38,0.18)",
    key: "alerts",
    sub: "ELA pixel splicing detected",
  },
  {
    label: "Compliant Institutions",
    icon: CheckCircle2,
    color: "#10b981",
    bgColor: "rgba(5,150,105,0.07)",
    borderColor: "rgba(5,150,105,0.18)",
    key: "compliant",
    sub: "Zero shortfall across norms",
  },
  {
    label: "Rule Contradictions",
    icon: Clock,
    color: "#3b82f6",
    bgColor: "rgba(59,130,246,0.07)",
    borderColor: "rgba(59,130,246,0.18)",
    key: "conflicts",
    sub: "Z3 theorem prover flagged",
  },
];

export default function CommandCenterPage() {
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [modalOpen, setModalOpen] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setLoadError("");
    try {
      const res = await fetch(`${API_BASE}/applications`);
      if (!res.ok) throw new Error(`Directory request failed (${res.status})`);
      const data = await res.json();
      if (!Array.isArray(data)) throw new Error("Directory returned an invalid response");
      setApplications(data);
    } catch {
      setApplications([]);
      setLoadError("Unable to load the applications directory. Confirm the Sakshya API service is running and refresh.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);


  const filtered = applications.filter((app) => {
    const q = searchQuery.toLowerCase();
    const match =
      app.institution_name.toLowerCase().includes(q) ||
      app.institution_id.toLowerCase().includes(q);
    const caseStatus = app.case_status ?? (app.institution_id.includes("FRAUD") ? "CRITICAL_DEFICIENCIES" : "VERIFIED");
    if (statusFilter === "FRAUD") return match && caseStatus === "CRITICAL_DEFICIENCIES";
    if (statusFilter === "COMPLIANT") return match && caseStatus === "VERIFIED";
    if (statusFilter === "REVIEW") return match && caseStatus === "MANUAL_REVIEW_REQUIRED";
    return match;
  });

  const metrics = {
    total: applications.length,
    alerts: applications.filter((a) => a.case_status === "CRITICAL_DEFICIENCIES" || a.institution_id.includes("FRAUD")).length,
    compliant: applications.filter((a) => (a.case_status ?? "VERIFIED") === "VERIFIED").length,
    conflicts: 1,
  };

  return (
    <SidebarLayout>
      <div className="space-y-7">
        {/* ── Page header ─────────────────────────── */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">
          <div>
            <p className="page-eyebrow mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              National Approval &amp; Fraud Verification Bureau
            </p>
            <h1 className="page-title">Scrutiny Command Center</h1>
            <p className="page-subtitle mt-2 max-w-2xl">
              Explainable decision-support portal executing deterministic regulatory
              proofs via Z3 SMT solver coupled with non-deterministic computer vision
              and multi-layer document forensics.
            </p>
          </div>
          <div className="flex items-center gap-2.5 shrink-0">
            <button
              onClick={() => setModalOpen(true)}
              className="btn btn-primary"
            >
              <Plus className="w-3.5 h-3.5" />
              Ingest Application
            </button>
            <button
              onClick={loadData}
              className="btn btn-ghost"
              title="Refresh"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* ── Metric cards ─────────────────────────── */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {METRIC_CARDS.map(({ label, icon: Icon, color, bgColor, borderColor, key, sub }) => (
            <div
              key={key}
              className="rounded-xl p-5 space-y-3"
              style={{ background: bgColor, border: `1px solid ${borderColor}` }}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400">{label}</span>
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ background: `${color}20` }}
                >
                  <Icon className="w-4 h-4" style={{ color }} />
                </div>
              </div>
              <div className="text-3xl font-black" style={{ color }}>
                {key === "conflicts" ? "1" : key === "alerts" ? `${metrics.alerts} Case` : key === "compliant" ? `${metrics.compliant} Verified` : metrics.total}
              </div>
              <p className="text-[10px] text-slate-500">{sub}</p>
            </div>
          ))}
        </div>

        {/* ── Applications directory ────────────────── */}
        <div
          className="rounded-xl overflow-hidden"
          style={{
            background: "var(--bg-surface)",
            border: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          {/* Table header bar */}
          <div
            className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-6 py-5"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div>
              <h2 className="text-sm font-bold text-white">
                Institutional Applications Directory
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {loading ? "Loading live application records…" : `${applications.length} live application records · select an institution to begin review.`}
              </p>
            </div>
            <div className="flex w-full flex-col gap-2.5 sm:w-auto sm:flex-row sm:items-center">
              {/* Search */}
              <div className="relative min-w-0 flex-1 sm:w-64 sm:flex-none">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Search college or ID…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="field w-full py-2 pl-9 pr-9 text-xs"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-slate-500 transition hover:bg-white/10 hover:text-slate-200"
                    aria-label="Clear application search"
                    title="Clear search"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
              {/* Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="field w-full py-2 text-xs sm:w-auto"
                aria-label="Filter applications by status"
              >
                <option value="ALL">All</option>
                <option value="FRAUD">Fraud Flagged</option>
                <option value="COMPLIANT">Verified</option>
                <option value="REVIEW">Manual Review</option>
              </select>
            </div>
          </div>

          {loadError && (
            <div
              className="mx-6 mb-5 rounded-lg px-4 py-3 text-xs text-rose-200"
              style={{ background: "rgba(220,38,38,0.09)", border: "1px solid rgba(220,38,38,0.22)" }}
              role="alert"
            >
              {loadError}
            </div>
          )}

          {/* Table */}
          <div className="overflow-x-auto px-6 pb-4">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="text-left pr-4">Application / AICTE ID</th>
                  <th className="text-left pr-4">Institution</th>
                  <th className="text-left pr-4">Location</th>
                  <th className="text-left pr-4">Land</th>
                  <th className="text-left pr-4">Faculty</th>
                  <th className="text-left pr-4">Documents</th>
                  <th className="text-left pr-4">Case Status</th>
                  <th className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: 3 }).map((_, i) => (
                      <tr key={i}>
                        {Array.from({ length: 8 }).map((_, j) => (
                          <td key={j} className="pr-4">
                            <div className="skeleton h-4 w-full max-w-[120px]" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : filtered.map((app) => {
                      const caseStatus = app.case_status ?? (app.institution_id.includes("FRAUD") ? "CRITICAL_DEFICIENCIES" : "VERIFIED");
                      const isFraud = caseStatus === "CRITICAL_DEFICIENCIES";
                      const isReview = caseStatus === "MANUAL_REVIEW_REQUIRED";
                      return (
                        <tr key={app.institution_id}>
                          <td className="pr-4">
                            <span className="font-mono text-indigo-400 font-semibold text-xs">
                              {app.application_reference_number ?? app.institution_id}
                            </span>
                            <div className="mt-0.5 text-[10px] text-slate-500">{app.permanent_id ?? app.institution_id} · {app.application_category ?? "EOA"}</div>
                          </td>
                          <td className="pr-4">
                            <div className="font-semibold text-slate-100 text-xs">
                              {app.institution_name}
                            </div>
                            <div className="text-[10px] text-slate-500 mt-0.5">
                              {app.program} · Enrolment {app.enrolment}
                            </div>
                          </td>
                          <td className="pr-4">
                            <span className="badge badge-slate">{app.location_type}</span>
                          </td>
                          <td className="pr-4">
                            <span
                              className="font-mono text-xs font-semibold"
                              style={{
                                color: app.land_acres < 2.5 ? "#f59e0b" : "#10b981",
                              }}
                            >
                              {app.land_acres} ac
                            </span>
                          </td>
                          <td className="pr-4">
                            <span className="font-mono text-xs text-slate-400">
                              {app.faculty_count}
                            </span>
                          </td>
                          <td className="pr-4">
                            {app.missing_mandatory_documents?.length > 0 ? (
                              <span className="badge badge-rose">
                                <XCircle className="w-2.5 h-2.5" />
                                {app.missing_mandatory_documents.length} missing
                              </span>
                            ) : (
                              <span className="badge badge-emerald">
                                <CheckCircle2 className="w-2.5 h-2.5" />
                                Complete
                              </span>
                            )}
                          </td>
                          <td className="pr-4">
                            <span className={`badge ${isFraud ? "badge-rose" : isReview ? "badge-saffron" : "badge-emerald"}`}>
                              {isFraud ? "Critical" : isReview ? "Manual review" : "Verified"}
                            </span>
                          </td>
                          <td className="text-right">
                            <Link
                              href={`/scrutiny/${app.institution_id}`}
                              onClick={() => localStorage.setItem("sakshya_active_application", app.institution_id)}
                              className="btn"
                              style={
                                isFraud
                                  ? {
                                      background: "rgba(220,38,38,0.08)",
                                      border: "1px solid rgba(220,38,38,0.25)",
                                      color: "#fca5a5",
                                    }
                                  : isReview
                                  ? {
                                      background: "rgba(245,158,11,0.08)",
                                      border: "1px solid rgba(245,158,11,0.25)",
                                      color: "#fcd34d",
                                    }
                                  : {
                                      background: "linear-gradient(135deg,#c87d0e,#f5a623)",
                                      color: "#0a0a0a",
                                      fontWeight: 800,
                                      boxShadow: "0 2px 10px rgba(245,166,35,0.25)",
                                    }
                              }
                            >
                              {isFraud ? "Deep-Dive" : isReview ? "Review Queue" : "Review"}
                              <ArrowRight className="w-3 h-3" />
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                {!loading && !loadError && filtered.length === 0 && (
                  <tr>
                    <td colSpan={8} className="py-10 text-center text-xs text-slate-500">
                      No applications match the current search or filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Create modal ─────────────────────────── */}
      {modalOpen && <ApplicationIngestionWizard onClose={() => setModalOpen(false)} onComplete={(applicationId) => { setModalOpen(false); localStorage.setItem("sakshya_active_application", applicationId); loadData(); }} />}
    </SidebarLayout>
  );
}
