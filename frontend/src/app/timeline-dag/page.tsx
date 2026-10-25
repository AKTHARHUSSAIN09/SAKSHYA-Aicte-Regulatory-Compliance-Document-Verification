"use client";

import { useEffect, useState } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import ApplicationPicker from "@/components/ApplicationPicker";
import { API_BASE } from "@/lib/api";
import { AlertTriangle, Calendar, CheckCircle2, GitBranch } from "lucide-react";

type Event = { event_id: string; entity_name: string; category: string; start_date: string; end_date?: string | null; document_ref: string };
type Timeline = { events: Event[]; report: { is_chronologically_valid: boolean; anomalies_count: number; anomalies: Array<{ event_a_id?: string; event_b_id?: string; explanation?: string }> } };

export default function TimelineDAGPage() {
  const [applicationId, setApplicationId] = useState("AICTE-2024-FRAUD-002");
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [error, setError] = useState("");

  useEffect(() => setApplicationId(localStorage.getItem("sakshya_active_application") ?? "AICTE-2024-FRAUD-002"), []);
  useEffect(() => {
    setTimeline(null); setError("");
    fetch(`${API_BASE}/timelines/${applicationId}`)
      .then((response) => response.ok ? response.json() : Promise.reject(new Error(`Request failed (${response.status})`)))
      .then(setTimeline)
      .catch(() => setError("Timeline analysis could not be loaded for this application."));
  }, [applicationId]);

  const anomaliesFor = (eventId: string) => timeline?.report.anomalies.filter((anomaly) => anomaly.event_a_id === eventId || anomaly.event_b_id === eventId) ?? [];
  const valid = timeline?.report.is_chronologically_valid ?? true;

  return <SidebarLayout><div className="space-y-7">
    <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
      <div><p className="page-eyebrow mb-2"><GitBranch className="h-3.5 w-3.5" />Allen&apos;s Temporal Interval Algebra</p><h1 className="page-title">Timeline Impossibility Engine</h1><p className="page-subtitle mt-1.5 max-w-2xl">Live chronological analysis for the selected institution, using its submitted milestones and evidence records.</p></div>
      <ApplicationPicker value={applicationId} onChange={setApplicationId} />
    </div>
    <div className="rounded-xl p-4 flex items-start gap-4" style={{ background: valid ? "rgba(16,185,129,0.06)" : "rgba(244,63,94,0.06)", border: `1px solid ${valid ? "rgba(16,185,129,0.2)" : "rgba(244,63,94,0.2)"}` }}>
      {valid ? <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-700" /> : <AlertTriangle className="h-5 w-5 shrink-0 text-rose-600" />}
      <div><h2 className="text-sm font-bold" style={{ color: valid ? "#047857" : "#BE123C" }}>{valid ? "Chronologically Valid Timeline" : `${timeline?.report.anomalies_count ?? 0} chronological anomalies detected`}</h2><p className="mt-1 text-xs text-slate-600">{timeline ? `Live analysis for ${applicationId}.` : "Loading live timeline analysis…"}</p></div>
    </div>
    {error && <div role="alert" className="rounded-xl p-4 text-xs text-rose-800" style={{ background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.22)" }}>{error}</div>}
    <div className="rounded-xl p-6" style={{ background: "var(--bg-surface)", border: "1px solid rgba(15,21,53,0.096)" }}><div className="mb-6 flex items-center justify-between border-b border-slate-900/10 pb-4"><span className="text-sm font-bold text-slate-900">Chronological Directed Acyclic Graph</span><span className="font-mono text-[10px] text-slate-500">{timeline?.events.length ?? 0} milestones evaluated</span></div>
      <div className="relative space-y-4 pl-10 timeline-line">{timeline?.events.map((event) => { const anomalies = anomaliesFor(event.event_id); const flagged = anomalies.length > 0; return <div key={event.event_id} className="relative flex items-start gap-5"><div className="absolute -left-10 z-10 flex h-7 w-7 items-center justify-center rounded-full border-2 text-[10px] font-black" style={{ background: flagged ? "rgba(244,63,94,0.15)" : "rgba(16,185,129,0.12)", borderColor: flagged ? "rgba(244,63,94,0.6)" : "rgba(16,185,129,0.5)", color: flagged ? "#BE123C" : "#047857" }}>{flagged ? "!" : "✓"}</div><div className="flex-1 rounded-xl p-4" style={{ background: flagged ? "rgba(244,63,94,0.05)" : "rgba(15,21,53,0.04)", border: `1px solid ${flagged ? "rgba(244,63,94,0.18)" : "rgba(15,21,53,0.08)"}` }}><div className="flex flex-wrap items-center justify-between gap-2"><div><div className="text-sm font-semibold text-slate-900">{event.entity_name}</div><div className="mt-1 flex items-center gap-2 text-[10px] font-mono text-slate-500"><Calendar className="h-3 w-3" />{event.start_date}{event.end_date ? ` → ${event.end_date}` : ""} · {event.document_ref}</div></div><span className={`badge ${flagged ? "badge-rose" : "badge-emerald"}`}>{flagged ? "FLAGGED" : "VALID"}</span></div>{anomalies.map((anomaly, index) => <p key={index} className="mt-3 rounded-lg border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-slate-700">{anomaly.explanation ?? "Chronological inconsistency detected."}</p>)}</div></div>; })}</div>
    </div>
  </div></SidebarLayout>;
}
