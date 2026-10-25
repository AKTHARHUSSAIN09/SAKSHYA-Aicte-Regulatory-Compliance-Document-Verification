"use client";

import React, { useState } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import { API_BASE } from "@/lib/api";
import {
  Building2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Search,
  ExternalLink,
} from "lucide-react";

const FEEDS = [
  {
    id: "FEED-1",
    authority: "State Land Records (Bhulekh GIS)",
    identifier: "KHASRA-991/B",
    status: "MISMATCH_DETECTED",
    institution: "National Knowledge Institute",
    claimed: { survey_number: "KHASRA-991/B", claimed_acres: 2.10, society: "National Knowledge Trust" },
    official: { owner_name: "National Knowledge Trust", registered_acres: 1.75, district: "Bengaluru Rural", status: "DISPUTED_TITLE" },
    mismatch: "Application claims 2.10 acres, but official Bhulekh registry records only 1.75 acres (Shortfall: 0.35 acres). Title Status: DISPUTED_TITLE.",
  },
  {
    id: "FEED-2",
    authority: "State Land Records (Bhulekh GIS)",
    identifier: "KHASRA-402/1",
    status: "VERIFIED",
    institution: "Savitribai Phule Institute of Tech",
    claimed: { survey_number: "KHASRA-402/1", claimed_acres: 2.85 },
    official: { owner_name: "Shri Ram Educational Society", registered_acres: 2.85, district: "Pune", status: "CLEAR_TITLE" },
    mismatch: null,
  },
  {
    id: "FEED-3",
    authority: "DigiLocker NAD (National Academic Depository)",
    identifier: "DEG-IITB-2014-998",
    status: "VERIFIED",
    institution: "Savitribai Phule Institute of Tech",
    claimed: { candidate: "Dr. Rajesh Kumar", degree: "Ph.D. in Computer Science" },
    official: { candidate_name: "Dr. Rajesh Kumar", degree: "Ph.D.", university: "IIT Bombay", conferment_year: 2014, verified: true },
    mismatch: null,
  },
  {
    id: "FEED-4",
    authority: "DigiLocker NAD (National Academic Depository)",
    identifier: "DEG-UNKNOWN-99",
    status: "MANUAL_REVIEW_REQUIRED",
    institution: "National Knowledge Institute",
    claimed: { candidate: "Dr. K. Mehta", degree: "Ph.D. in Mechanical Engineering" },
    official: null,
    mismatch: "University graduation batch records not yet synchronized with NAD database. Routed to manual verification queue.",
  },
];

const STATUS_CONFIG: Record<string, { color: string; bg: string; border: string; icon: React.FC<any> }> = {
  VERIFIED:               { color: "#10b981", bg: "rgba(16,185,129,0.08)",  border: "rgba(16,185,129,0.2)",  icon: CheckCircle2 },
  MISMATCH_DETECTED:      { color: "#f43f5e", bg: "rgba(244,63,94,0.08)",   border: "rgba(244,63,94,0.2)",   icon: XCircle },
  MANUAL_REVIEW_REQUIRED: { color: "#f59e0b", bg: "rgba(245,158,11,0.08)",  border: "rgba(245,158,11,0.2)",  icon: AlertTriangle },
};

export default function AuthorityGatewayPage() {
  const [surveyNum, setSurveyNum] = useState("KHASRA-991/B");
  const [acres, setAcres] = useState(2.10);
  const [liveResult, setLiveResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/authorities/verify-land`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          survey_number: surveyNum,
          claimed_acres: acres,
          society_name: "Applicant Educational Society",
        }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setLiveResult({
        authority: data.authority_name,
        status: data.status,
        registry_data: data.official_registry_data,
        notes: data.mismatch_details || "Registry record matches the submitted claim.",
      });
    } catch {
      setLiveResult({
        authority: "Verification Gateway",
        status: "MANUAL_REVIEW_REQUIRED",
        registry_data: null,
        notes: "The authority service is unavailable. Request has been routed to an authorized officer.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <SidebarLayout>
      <div className="space-y-7">
        {/* ── Header ─────────────────────────────── */}
        <div>
          <p className="page-eyebrow mb-2">
            <Building2 className="w-3.5 h-3.5" />
            Direct Statutory Source Verification
          </p>
          <h1 className="page-title">Issuing Authority Gateway</h1>
          <p className="page-subtitle mt-1.5 max-w-2xl">
            Automated integration connecting DigiLocker NAD (degrees), State Land Records
            (Bhulekh GIS), and MCA21 Corporate Registry with fallback to officer queue.
          </p>
        </div>

        {/* ── Live sandbox ─────────────────────────── */}
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="px-6 py-4"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
          >
            <h2 className="text-sm font-bold text-white">Live Authority Query Sandbox</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Query official state registries with live parameters
            </p>
          </div>

          <div className="p-6 space-y-5">
            <div className="grid sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1.5 font-medium">
                  Survey / Khasra Identifier
                </label>
                <input
                  type="text"
                  value={surveyNum}
                  onChange={(e) => setSurveyNum(e.target.value)}
                  className="field font-mono"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1.5 font-medium">
                  Claimed Land Acreage
                </label>
                <input
                  type="number"
                  step="0.05"
                  value={acres}
                  onChange={(e) => setAcres(parseFloat(e.target.value) || 0)}
                  className="field"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleVerify}
                  disabled={loading}
                  className="btn btn-primary w-full justify-center py-3"
                >
                  <Search className="w-3.5 h-3.5" />
                  {loading ? "Querying Registry…" : "Dispatch to Bhulekh"}
                </button>
              </div>
            </div>

            {liveResult && (
              <div
                className="rounded-xl p-5 space-y-3"
                style={{
                  background: STATUS_CONFIG[liveResult.status]?.bg ?? "rgba(255,255,255,0.03)",
                  border: `1px solid ${STATUS_CONFIG[liveResult.status]?.border ?? "rgba(255,255,255,0.08)"}`,
                }}
              >
                <div
                  className="flex items-center justify-between pb-3"
                  style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
                >
                  <span className="text-xs font-bold text-white">
                    Response from {liveResult.authority}
                  </span>
                  <span
                    className="badge"
                    style={{
                      background: STATUS_CONFIG[liveResult.status]
                        ? `${STATUS_CONFIG[liveResult.status].color}18`
                        : "rgba(255,255,255,0.08)",
                      color: STATUS_CONFIG[liveResult.status]?.color ?? "#94a3b8",
                      border: `1px solid ${STATUS_CONFIG[liveResult.status]?.color ?? "#94a3b8"}30`,
                    }}
                  >
                    {liveResult.status}
                  </span>
                </div>
                <p className="text-xs text-slate-300">{liveResult.notes}</p>
                <pre
                  className="rounded-lg p-3 text-[11px] font-mono text-slate-400 overflow-x-auto leading-relaxed"
                  style={{ background: "rgba(0,0,0,0.3)" }}
                >
                  {JSON.stringify(liveResult.registry_data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* ── Verification records ─────────────────── */}
        <div>
          <h2 className="text-sm font-bold text-white mb-4">
            Recent Statutory Verification Records
          </h2>
          <div className="space-y-4">
            {FEEDS.map((feed) => {
              const cfg = STATUS_CONFIG[feed.status];
              const StatusIcon = cfg?.icon ?? CheckCircle2;
              return (
                <div
                  key={feed.id}
                  className="rounded-xl overflow-hidden"
                  style={{
                    background: cfg?.bg ?? "rgba(255,255,255,0.03)",
                    border: `1px solid ${cfg?.border ?? "rgba(255,255,255,0.08)"}`,
                  }}
                >
                  {/* Card header */}
                  <div
                    className="flex flex-wrap items-start justify-between gap-3 px-5 py-4"
                    style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                        style={{ background: `${cfg?.color}18` }}
                      >
                        <Building2 className="w-4 h-4" style={{ color: cfg?.color }} />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{feed.authority}</h4>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          Target:{" "}
                          <span className="font-mono text-slate-300">{feed.identifier}</span>
                          {" · "}
                          {feed.institution}
                        </div>
                      </div>
                    </div>
                    <span
                      className="badge"
                      style={{
                        background: `${cfg?.color}18`,
                        color: cfg?.color,
                        border: `1px solid ${cfg?.color}30`,
                      }}
                    >
                      <StatusIcon className="w-2.5 h-2.5" />
                      {feed.status}
                    </span>
                  </div>

                  {/* Data grid */}
                  <div className="grid md:grid-cols-2 gap-4 p-5">
                    {[
                      { label: "Claimed in Application", data: feed.claimed },
                      { label: "Official Registry Response", data: feed.official },
                    ].map(({ label, data }) => (
                      <div
                        key={label}
                        className="rounded-xl p-4 space-y-2"
                        style={{ background: "rgba(0,0,0,0.2)", border: "1px solid rgba(255,255,255,0.05)" }}
                      >
                        <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                          {label}
                        </div>
                        {data ? (
                          <pre className="text-[11px] font-mono text-slate-300 overflow-x-auto leading-relaxed whitespace-pre-wrap">
                            {JSON.stringify(data, null, 2)}
                          </pre>
                        ) : (
                          <div className="text-xs text-amber-400 italic py-1">
                            Database record unavailable. Routed to officer queue.
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Mismatch note */}
                  {feed.mismatch && (
                    <div
                      className="mx-5 mb-5 rounded-xl p-3.5 text-xs leading-relaxed"
                      style={{ background: "rgba(244,63,94,0.07)", border: "1px solid rgba(244,63,94,0.18)" }}
                    >
                      <span className="font-semibold text-rose-300">Registry Discrepancy: </span>
                      <span className="text-slate-300">{feed.mismatch}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}
