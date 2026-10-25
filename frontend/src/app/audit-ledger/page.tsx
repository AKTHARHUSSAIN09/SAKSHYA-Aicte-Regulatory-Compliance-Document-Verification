"use client";

import React, { useEffect, useState } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import ApplicationPicker from "@/components/ApplicationPicker";
import { API_BASE } from "@/lib/api";
import { Clock, ShieldCheck, UserCheck, Scale, AlertTriangle, CheckCircle2 } from "lucide-react";

const LOGS = [
  {
    id: "LOG-00001",
    timestamp: "2024-06-01 · 10:15 UTC",
    actor: "AICTE-SYSTEM",
    role: "SYSTEM",
    action: "FULL_APPLICATION_AUDIT_EXECUTED",
    target: "APPLICATION:AICTE-2024-FRAUD-002",
    details: "Dual-Engine pipeline executed with Z3 theorem solver and OpenCV ELA. Verdict: REJECT_WITH_LEGAL_SHOW_CAUSE.",
    type: "system",
  },
  {
    id: "LOG-00002",
    timestamp: "2024-06-01 · 10:22 UTC",
    actor: "Officer R. K. Saxena",
    role: "REGIONAL_DIRECTOR",
    action: "RULE_OVERRIDE_RECORDED",
    target: "CONFLICT:AMBIG-APH-2024-LAND-URBAN",
    details: "Precedence granted to Circular 2024-C1 for dense urban greenfield campuses.",
    type: "officer",
  },
  {
    id: "LOG-00003",
    timestamp: "2024-06-01 · 10:30 UTC",
    actor: "AICTE Scrutiny Officer",
    role: "SCRUTINY_OFFICER",
    action: "DEFICIENCY_NOTICE_ISSUED",
    target: "APPLICATION:AICTE-2024-FRAUD-002",
    details: "Notice DEF-NOTICE-AICTE-2024-FRAUD-002 dispatched with 15-day statutory rectification window.",
    type: "notice",
  },
];

const NOTICES = [
  {
    id: "DEF-NOTICE-AICTE-2024-FRAUD-002",
    institution: "National Knowledge Institute of Tech & Research",
    deadline: "2024-07-15",
    status: "PENDING_RECTIFICATION",
    deficiencies: [
      "Land holding deficit of 0.40 acres against Urban norm of 2.50 acres.",
      "Expired Fire Safety NOC (expired on 2023-01-09).",
      "Chronological inversion in architect site inspection certificate.",
    ],
  },
];

const LOG_ICON: Record<string, React.ReactNode> = {
  system: <Scale className="w-3.5 h-3.5 text-indigo-400" />,
  officer: <UserCheck className="w-3.5 h-3.5 text-cyan-400" />,
  notice: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
};

const LOG_COLOR: Record<string, string> = {
  system: "rgba(99,102,241,0.12)",
  officer: "rgba(34,211,238,0.12)",
  notice: "rgba(245,158,11,0.12)",
};

export default function AuditLedgerPage() {
  const [logs, setLogs] = useState(LOGS);
  const [source, setSource] = useState<"live" | "demo">("demo");
  const [applicationId, setApplicationId] = useState("AICTE-2024-FRAUD-002");

  useEffect(() => setApplicationId(localStorage.getItem("sakshya_active_application") ?? "AICTE-2024-FRAUD-002"), []);
  useEffect(() => {
    setLogs([]);
    setSource("live");
    fetch(`${API_BASE}/audit/logs/${applicationId}`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((entries: Array<Record<string, unknown>>) => {
        if (!Array.isArray(entries)) throw new Error("Invalid audit response");
        setLogs(entries.map((entry) => ({
          id: String(entry.log_id),
          timestamp: new Date(String(entry.timestamp)).toLocaleString(),
          actor: String(entry.actor_name ?? entry.actor_id),
          role: String(entry.role),
          action: String(entry.action),
          target: String(entry.target_entity),
          details: Object.entries((entry.details as Record<string, unknown>) ?? {})
            .map(([key, value]) => `${key.replaceAll("_", " ")}: ${String(value)}`)
            .join(" · ") || "No supplementary details recorded.",
          type: String(entry.action).includes("NOTICE") ? "notice" : String(entry.action).includes("OVERRIDE") ? "officer" : "system",
        })));
        setSource("live");
      })
      .catch(() => setSource("demo"));
  }, [applicationId]);

  return (
    <SidebarLayout>
      <div className="space-y-7">
        {/* ── Header ─────────────────────────────── */}
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
          <p className="page-eyebrow mb-2">
            <Clock className="w-3.5 h-3.5" />
            Event-Sourced Regulatory Audit Trail
          </p>
          <h1 className="page-title">Legal Audit Ledger</h1>
          <p className="page-subtitle mt-1.5 max-w-2xl">
            Court-admissible, append-only event log recording every automated verification,
            officer override, and issued legal notice with cryptographic timestamps.
          </p>
          </div>
          <ApplicationPicker value={applicationId} onChange={setApplicationId} />
        </div>

        {/* ── Notices ─────────────────────────────── */}
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="flex items-center justify-between px-6 py-4"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div>
              <h2 className="text-sm font-bold text-white">Issued Deficiency Notices</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Formal legal notices requiring applicant rectification
              </p>
            </div>
            <span className="badge badge-amber">{applicationId === "AICTE-2024-FRAUD-002" ? "1 Pending" : "No seeded notice"}</span>
          </div>

          <div className="p-6 space-y-4">
            {applicationId === "AICTE-2024-FRAUD-002" ? NOTICES.map((n) => (
              <div
                key={n.id}
                className="rounded-xl p-5 space-y-4"
                style={{
                  background: "rgba(245,158,11,0.04)",
                  border: "1px solid rgba(245,158,11,0.18)",
                }}
              >
                <div
                  className="flex flex-wrap items-start justify-between gap-3 pb-3"
                  style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}
                >
                  <div>
                    <span className="font-mono text-indigo-400 font-bold text-xs">
                      {n.id}
                    </span>
                    <h4 className="font-semibold text-sm text-white mt-0.5">
                      {n.institution}
                    </h4>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-slate-500">Rectification Deadline</div>
                    <div className="font-mono font-bold text-rose-400 text-xs mt-0.5">
                      {n.deadline}
                    </div>
                  </div>
                </div>

                <div>
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    Cited Deficiencies
                  </p>
                  <ul className="space-y-1.5">
                    {n.deficiencies.map((d, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs text-slate-300">
                        <span
                          className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                          style={{ background: "#f59e0b" }}
                        />
                        {d}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )) : <p className="py-6 text-center text-xs text-slate-500">No deficiency notice has been issued for {applicationId}.</p>}
          </div>
        </div>

        {/* ── Audit log ─────────────────────────────── */}
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: "var(--bg-surface)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="px-6 py-4"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
          >
            <h2 className="text-sm font-bold text-white">Immutable Event Log</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              {source === "live" ? "Live append-only trail for the selected application" : "Demo trail shown until the API records an event"}
            </p>
          </div>

          <div className="p-6 space-y-3">
            {logs.map((log, index) => (
              <div
                key={`${log.id}-${log.timestamp}-${index}`}
                className="flex items-start gap-4 rounded-xl p-4 transition"
                style={{ border: "1px solid rgba(255,255,255,0.05)" }}
              >
                {/* Icon dot */}
                <div
                  className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: LOG_COLOR[log.type] }}
                >
                  {LOG_ICON[log.type]}
                </div>

                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-[10px] font-bold text-indigo-400">
                      {log.id}
                    </span>
                    <span className="badge badge-slate">{log.role}</span>
                    <span className="text-[10px] text-slate-600">{log.timestamp}</span>
                  </div>
                  <div className="text-xs font-semibold text-white">{log.action}</div>
                  <p className="text-xs text-slate-400 leading-relaxed">{log.details}</p>
                </div>

                <div
                  className="shrink-0 text-[10px] font-mono font-bold px-2.5 py-1.5 rounded-lg"
                  style={{
                    background: "rgba(99,102,241,0.1)",
                    border: "1px solid rgba(99,102,241,0.18)",
                    color: "#a5b4fc",
                  }}
                >
                  {log.target.split(":")[1] ?? log.target}
                </div>
              </div>
            ))}
            {source === "live" && logs.length === 0 && (
              <p className="py-8 text-center text-xs text-slate-500">No ledger events have been recorded for {applicationId} yet.</p>
            )}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}
