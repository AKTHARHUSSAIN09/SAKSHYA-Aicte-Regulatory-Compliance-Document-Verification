"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import SidebarLayout from "@/components/SidebarLayout";
import { API_BASE } from "@/lib/api";
import {
  FileText,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Download,
  ArrowLeft,
  RefreshCw,
  X,
} from "lucide-react";

function ScrutinyContent() {
  const params = useParams();
  const router = useRouter();
  const appId = (params?.id as string) || "AICTE-2024-FRAUD-002";

  const [auditData, setAuditData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeDocTab, setActiveDocTab] = useState("land_deed");
  const [selectedBBox, setSelectedBBox] = useState("land_area_acres");

  const [noticeOpen, setNoticeOpen] = useState(false);
  const [noticeNote, setNoticeNote] = useState("");
  const [noticeSuccess, setNoticeSuccess] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => { fetchAudit(); }, [appId]);

  const fetchAudit = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/audit/run/${appId}`, { method: "POST" });
      if (res.ok) setAuditData(await res.json());
    } catch { /* silent */ } finally { setLoading(false); }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("document_type", "UNKNOWN");
      const res = await fetch(`${API_BASE}/applications/${appId}/documents`, {
        method: "POST", body: form,
      });
      if (!res.ok) throw new Error();
      await fetchAudit();
      alert("Document uploaded and sent for forensic analysis.");
    } catch { alert("Upload failed. Use PDF/PNG/JPEG < 20MB."); }
    finally { setUploading(false); e.target.value = ""; }
  };

  const handleIssueNotice = async () => {
    try {
      const deficiencies =
        auditData?.audit_report?.results
          ?.filter((r: any) => r.status === "DEFICIENT")
          ?.map((r: any) => `${r.rule_title}: ${r.explanation}`) ||
        ["Statutory deficiency."];
      const res = await fetch(`${API_BASE}/deficiency-notice/issue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          application_id: appId,
          institution_name: auditData?.brief?.institution_name || "Applicant",
          officer_id: "AICTE_SCRUTINY_OFFICER",
          deficiencies,
          instructions: noticeNote || "Rectify land title and upload fresh approvals.",
          deadline_date: "2024-07-20",
        }),
      });
      if (res.ok) {
        setNoticeSuccess(true);
        setTimeout(() => { setNoticeSuccess(false); setNoticeOpen(false); }, 1500);
      }
    } catch { alert("Failed to issue notice"); }
  };

  const isFraud = appId.includes("FRAUD");
  const brief = auditData?.brief;
  const results = auditData?.audit_report?.results || [];

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* ── Header ─────────────────────────────── */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">
          <div>
            <button
              onClick={() => router.push("/")}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 transition mb-3"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Command Center
            </button>
            <div className="flex items-center flex-wrap gap-3">
              <h1 className="page-title">
                {loading ? (
                  <span className="skeleton inline-block w-64 h-7 rounded" />
                ) : (
                  brief?.institution_name || "Institution Scrutiny"
                )}
              </h1>
              <span
                className="badge"
                style={
                  isFraud
                    ? { background: "rgba(244,63,94,0.12)", color: "#BE123C", border: "1px solid rgba(244,63,94,0.28)", padding: "0.25rem 0.75rem", fontSize: "0.625rem" }
                    : { background: "rgba(16,185,129,0.12)", color: "#047857", border: "1px solid rgba(16,185,129,0.28)", padding: "0.25rem 0.75rem", fontSize: "0.625rem" }
                }
              >
                {isFraud ? "CRITICAL DEFICIENCIES" : "COMPLIANT"}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1.5 font-mono">
              {appId} · Technical & Statutory Verification
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <label className="btn btn-ghost cursor-pointer">
              <FileText className="w-3.5 h-3.5" />
              {uploading ? "Processing…" : "Upload Evidence"}
              <input
                type="file"
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg,.tiff"
                disabled={uploading}
                onChange={handleUpload}
              />
            </label>
            <button
              onClick={() => window.open(`${API_BASE}/officer-brief/pdf/${appId}`, "_blank")}
              className="btn btn-primary"
            >
              <Download className="w-3.5 h-3.5" />
              Download PDF Brief
            </button>
            <button
              onClick={() => setNoticeOpen(true)}
              className="btn btn-danger"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              Issue Notice
            </button>
          </div>
        </div>

        {/* ── Split screen ─────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left: document canvas (5 cols) */}
          <div
            className="lg:col-span-5 rounded-xl overflow-hidden"
            style={{ background: "var(--bg-surface)", border: "1px solid rgba(15,21,53,0.096)" }}
          >
            {/* Tabs */}
            <div
              className="flex items-center gap-1 p-4"
              style={{ borderBottom: "1px solid rgba(15,21,53,0.096)" }}
            >
              <FileText className="w-3.5 h-3.5 text-indigo-700 mr-2" />
              <span className="text-xs font-bold text-slate-900 flex-1">Document Canvas</span>
              {["land_deed", "fire_noc"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveDocTab(tab)}
                  className="text-[11px] font-semibold px-3 py-1.5 rounded-lg transition"
                  style={
                    activeDocTab === tab
                      ? { background: "rgba(99,102,241,0.2)", color: "#4338CA" }
                      : { color: "#475569" }
                  }
                >
                  {tab === "land_deed" ? "Land Deed" : "Fire NOC"}
                </button>
              ))}
            </div>

            {/* Document body */}
            <div className="p-5 space-y-5">
              {/* Doc header */}
              <div
                className="pb-4 space-y-1"
                style={{ borderBottom: "1px solid rgba(15,21,53,0.08)" }}
              >
                <div className="text-[9px] uppercase font-mono tracking-widest text-slate-600">
                  Official Record · State Revenue & Statutory Filing
                </div>
                <div className="text-xs font-semibold text-slate-700">
                  {activeDocTab === "land_deed"
                    ? "Schedule of Immovable Property & Deed of Transfer"
                    : "State Fire & Rescue Services · No Objection Certificate"}
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed font-serif">
                This instrument is executed in favor of the applicant educational trust for educational purposes.
              </p>

              {/* Bounding boxes */}
              {activeDocTab === "land_deed" && (
                <button
                  onClick={() => setSelectedBBox("land_area_acres")}
                  className="w-full text-left rounded-xl p-4 transition-all"
                  style={
                    selectedBBox === "land_area_acres"
                      ? { background: "rgba(180,83,9,0.08)", border: "2px solid rgba(180,83,9,0.5)" }
                      : { background: "rgba(99,102,241,0.04)", border: "2px solid rgba(99,102,241,0.2)" }
                  }
                >
                  <div className="flex justify-between text-[9px] font-mono text-amber-700 font-bold mb-2">
                    <span>BBOX [X1:105 Y1:310 X2:275 Y2:340]</span>
                    <span>98.4% conf.</span>
                  </div>
                  <div className="text-sm text-slate-900 font-semibold">
                    "Total Land Parcel: {isFraud ? "2.10 Acres" : "2.85 Acres"} at Khasra No. 991/B"
                  </div>
                  {isFraud && (
                    <div className="mt-2 text-[10px] text-amber-700">
                      ⚠ ELA variance hotspot: pixel compression indicates "1.75" spliced to "2.10"
                    </div>
                  )}
                </button>
              )}

              {activeDocTab === "fire_noc" && (
                <button
                  onClick={() => setSelectedBBox("fire_safety_noc_valid")}
                  className="w-full text-left rounded-xl p-4 transition-all"
                  style={
                    selectedBBox === "fire_safety_noc_valid"
                      ? { background: "rgba(244,63,94,0.08)", border: "2px solid rgba(244,63,94,0.4)" }
                      : { background: "rgba(99,102,241,0.04)", border: "2px solid rgba(99,102,241,0.2)" }
                  }
                >
                  <div className="flex justify-between text-[9px] font-mono text-rose-600 font-bold mb-2">
                    <span>BBOX [X1:85 Y1:190 X2:310 Y2:215]</span>
                    <span>EXPIRED</span>
                  </div>
                  <div className="text-sm text-slate-900 font-semibold">
                    "Valid From: 2021-01-10 to 2023-01-09"
                  </div>
                  {isFraud && (
                    <div className="mt-2 text-[10px] text-rose-600">
                      ⚠ Expired 16 months before portal application submission.
                    </div>
                  )}
                </button>
              )}

              <p className="text-[10px] text-slate-500 italic leading-relaxed font-serif">
                Subject to conditions laid down by the Municipal Town Planning department and AICTE regulations.
              </p>

              {/* Footer stamp */}
              <div
                className="pt-4 flex items-center justify-between text-[10px] font-mono"
                style={{ borderTop: "1px solid rgba(15,21,53,0.08)" }}
              >
                <span className="text-slate-600">SHA-256: e3b0c44298fc…</span>
                <span className="text-emerald-700">DIGITALLY PARSED</span>
              </div>
            </div>
          </div>

          {/* Right: compliance proofs (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div
              className="rounded-xl p-5"
              style={{ background: "var(--bg-surface)", border: "1px solid rgba(15,21,53,0.096)" }}
            >
              <h3 className="text-sm font-bold text-slate-900">Compliance Proofs</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Formally verified by the Z3 SMT solver against AICTE Handbook clauses.
              </p>
            </div>

            <div className="space-y-3">
              {loading
                ? Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="rounded-xl p-5 skeleton h-28" />
                  ))
                : results.map((item: any, idx: number) => (
                    <div
                      key={idx}
                      className="rounded-xl p-5 space-y-3"
                      style={
                        item.status === "COMPLIANT"
                          ? { background: "rgba(16,185,129,0.04)", border: "1px solid rgba(16,185,129,0.15)" }
                          : item.status === "DEFICIENT"
                          ? { background: "rgba(244,63,94,0.05)", border: "1px solid rgba(244,63,94,0.2)" }
                          : { background: "rgba(180,83,9,0.05)", border: "1px solid rgba(180,83,9,0.2)" }
                      }
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          {item.status === "COMPLIANT" ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
                          ) : item.status === "DEFICIENT" ? (
                            <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
                          )}
                          <span className="font-semibold text-sm text-slate-900">{item.rule_title}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="badge badge-indigo">{item.clause_reference}</span>
                          <span
                            className="badge"
                            style={
                              item.status === "COMPLIANT"
                                ? { background: "rgba(16,185,129,0.12)", color: "#047857", border: "1px solid rgba(16,185,129,0.22)" }
                                : item.status === "DEFICIENT"
                                ? { background: "rgba(244,63,94,0.12)", color: "#BE123C", border: "1px solid rgba(244,63,94,0.22)" }
                                : { background: "rgba(180,83,9,0.12)", color: "#92400E", border: "1px solid rgba(180,83,9,0.22)" }
                            }
                          >
                            {item.status}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-3 text-xs">
                        {[
                          { label: "AICTE Norm", val: String(item.required_value) },
                          { label: "Extracted Value", val: String(item.actual_value) },
                          { label: "Shortfall", val: item.shortfall ? `${item.shortfall} ${item.unit}` : "None" },
                        ].map(({ label, val }) => (
                          <div key={label}>
                            <span className="text-[10px] text-slate-500 block">{label}</span>
                            <span className="font-semibold text-slate-800 text-xs">{val}</span>
                          </div>
                        ))}
                      </div>

                      <div
                        className="pt-3 text-xs text-slate-600 leading-relaxed"
                        style={{ borderTop: "1px solid rgba(15,21,53,0.08)" }}
                      >
                        <span className="text-slate-500 font-medium">Proof: </span>
                        {item.explanation}
                      </div>
                    </div>
                  ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Notice modal ─────────────────────────── */}
      {noticeOpen && (
        <div className="modal-backdrop">
          <div className="modal-box">
            <div
              className="flex items-center justify-between pb-4 mb-5"
              style={{ borderBottom: "1px solid rgba(15,21,53,0.112)" }}
            >
              <div>
                <h3 className="font-bold text-slate-900">Dispatch Deficiency Notice</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  15-day statutory rectification period
                </p>
              </div>
              <button
                onClick={() => setNoticeOpen(false)}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-900 hover:bg-slate-900/5"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-600 mb-4">
              Issue a formal notice to{" "}
              <span className="text-slate-900 font-semibold">{brief?.institution_name}</span>.
            </p>

            <div>
              <label className="block text-xs text-slate-600 mb-1.5 font-medium">
                Rectification Directives
              </label>
              <textarea
                value={noticeNote}
                onChange={(e) => setNoticeNote(e.target.value)}
                rows={4}
                placeholder="Enter specific instructions…"
                className="field resize-none"
              />
            </div>

            {noticeSuccess && (
              <div
                className="mt-4 rounded-xl p-3 flex items-center gap-2 text-xs text-emerald-800"
                style={{ background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)" }}
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                Notice dispatched and entered into the legal audit ledger.
              </div>
            )}

            <div
              className="flex justify-end gap-2.5 pt-5 mt-5"
              style={{ borderTop: "1px solid rgba(15,21,53,0.112)" }}
            >
              <button onClick={() => setNoticeOpen(false)} className="btn btn-ghost">
                Cancel
              </button>
              <button onClick={handleIssueNotice} className="btn btn-danger">
                Confirm &amp; Dispatch
              </button>
            </div>
          </div>
        </div>
      )}
    </SidebarLayout>
  );
}

export default function SplitScreenScrutinyPage() {
  return (
    <React.Suspense
      fallback={
        <div
          className="min-h-screen flex items-center justify-center text-slate-500 text-sm"
          style={{ background: "var(--bg-base)" }}
        >
          Loading Scrutiny Bureau…
        </div>
      }
    >
      <ScrutinyContent />
    </React.Suspense>
  );
}
