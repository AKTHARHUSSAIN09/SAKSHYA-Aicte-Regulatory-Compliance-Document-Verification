"use client";

import { useEffect, useMemo, useState } from "react";
import SidebarLayout from "@/components/SidebarLayout";
import ApplicationPicker from "@/components/ApplicationPicker";
import { API_BASE } from "@/lib/api";
import { AlertTriangle, Building2, FileText, MapPin, Scale, Share2, UserCheck } from "lucide-react";

type GraphNode = { id: string; label: string; type: string; flagged?: boolean };
type GraphEdge = { from: string; to: string; relation: string; anomaly?: boolean };
type GraphPayload = { nodes: GraphNode[]; edges: GraphEdge[] };
type Position = { x: number; y: number };

const TYPE_CONFIG: Record<string, { color: string; soft: string; Icon: typeof Building2 }> = {
  APPLICATION: { color: "#4F46E5", soft: "rgba(129,140,248,0.13)", Icon: Building2 },
  DOCUMENT: { color: "#0891B2", soft: "rgba(34,211,238,0.12)", Icon: FileText },
  EXTRACTED_FIELD: { color: "#3347B0", soft: "rgba(251,191,36,0.12)", Icon: MapPin },
  REGULATION: { color: "#059669", soft: "rgba(52,211,153,0.12)", Icon: Scale },
  FACULTY: { color: "#9333EA", soft: "rgba(192,132,252,0.12)", Icon: UserCheck },
};

function distribute(ids: string[], y: number, positions: Record<string, Position>) {
  ids.forEach((id, index) => {
    positions[id] = { x: ((index + 1) * 1000) / (ids.length + 1), y };
  });
}

function makeLayout(nodes: GraphNode[]) {
  const positions: Record<string, Position> = {};
  const apps = nodes.filter((node) => node.type === "APPLICATION").map((node) => node.id);
  const documents = nodes.filter((node) => node.type === "DOCUMENT").map((node) => node.id);
  const fields = nodes.filter((node) => node.type === "EXTRACTED_FIELD").map((node) => node.id);
  const regulations = nodes.filter((node) => node.type === "REGULATION").map((node) => node.id);
  const other = nodes.filter((node) => !["APPLICATION", "DOCUMENT", "EXTRACTED_FIELD", "REGULATION"].includes(node.type)).map((node) => node.id);
  distribute(apps, 64, positions);
  distribute(documents, 215, positions);
  distribute(fields, 380, positions);
  distribute(regulations, 550, positions);
  distribute(other, 470, positions);
  return positions;
}

export default function EvidenceGraphPage() {
  const [applicationId, setApplicationId] = useState("AICTE-2024-FRAUD-002");
  const [graph, setGraph] = useState<GraphPayload>({ nodes: [], edges: [] });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState("ALL");
  const [status, setStatus] = useState<"loading" | "live" | "error">("loading");

  useEffect(() => setApplicationId(localStorage.getItem("sakshya_active_application") ?? "AICTE-2024-FRAUD-002"), []);
  useEffect(() => {
    setStatus("loading"); setSelectedId(null);
    fetch(`${API_BASE}/evidence-graph/${applicationId}`)
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((data: GraphPayload) => { setGraph({ nodes: data.nodes ?? [], edges: data.edges ?? [] }); setStatus("live"); })
      .catch(() => { setGraph({ nodes: [], edges: [] }); setStatus("error"); });
  }, [applicationId]);

  const positions = useMemo(() => makeLayout(graph.nodes), [graph.nodes]);
  const selectedNode = graph.nodes.find((node) => node.id === selectedId) ?? null;
  const selectedEdges = selectedId ? graph.edges.filter((edge) => edge.from === selectedId || edge.to === selectedId) : [];
  const relatedIds = new Set(selectedEdges.flatMap((edge) => [edge.from, edge.to]));
  const visible = (node: GraphNode) => filterType === "ALL" || node.type === filterType;

  return <SidebarLayout><div className="space-y-7">
    <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
      <div><p className="page-eyebrow mb-2"><Share2 className="h-3.5 w-3.5" />Multi-Hop Entity Linkage & Regulatory Graph</p><h1 className="page-title">Evidence Knowledge Graph</h1><p className="page-subtitle mt-1.5 max-w-2xl">An interactive evidence network. Follow each application through submitted documents, extracted evidence, and the regulations used for assessment.</p><p className="mt-2 font-mono text-[10px]" style={{ color: "var(--text-muted)" }}>{status === "live" ? `LIVE GRAPH · ${graph.nodes.length} NODES · ${graph.edges.length} EDGES` : status === "loading" ? "LOADING LIVE GRAPH…" : "GRAPH SERVICE UNAVAILABLE"}</p></div>
      <div className="flex flex-col gap-2 sm:flex-row"><ApplicationPicker value={applicationId} onChange={setApplicationId} /><select value={filterType} onChange={(event) => setFilterType(event.target.value)} className="field py-2 text-xs" aria-label="Highlight node type"><option value="ALL">All node types</option><option value="APPLICATION">Application</option><option value="DOCUMENT">Documents</option><option value="EXTRACTED_FIELD">Extracted fields</option><option value="REGULATION">Regulations</option></select></div>
    </div>

    <div className="rounded-xl p-4 flex items-start gap-4" style={{ background: "rgba(37,99,235,0.06)", border: "1px solid rgba(37,99,235,0.18)" }}><Share2 className="h-5 w-5 shrink-0 text-blue-600" /><div><h2 className="text-sm font-bold text-blue-800">Interactive evidence chain for {applicationId}</h2><p className="mt-1 text-xs text-slate-600">Click a node to trace its connected evidence. Red edges identify an anomalous relationship; gold nodes contain extracted document fields.</p></div></div>

    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className="overflow-hidden rounded-xl" style={{ background: "var(--bg-surface)", border: "1px solid rgba(15,21,53,0.096)" }}>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-900/10 px-5 py-4"><div><h2 className="text-sm font-bold text-slate-900">Evidence Graph Canvas</h2><p className="mt-0.5 text-[10px] text-slate-500">Application → documents → extracted facts → regulatory rules</p></div><div className="flex flex-wrap gap-3 text-[10px] text-slate-500"><span className="flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-cyan-400" />Document</span><span className="flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-amber-400" />Extracted fact</span><span className="flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-emerald-400" />Regulation</span></div></div>
        <div className="overflow-x-auto"><div className="relative min-w-[1000px]" style={{ height: "650px", background: "radial-gradient(circle at 50% 0%, rgba(37,99,235,0.08), transparent 42%), linear-gradient(rgba(15,21,53,0.029) 1px, transparent 1px), linear-gradient(90deg, rgba(15,21,53,0.029) 1px, transparent 1px)", backgroundSize: "auto, 32px 32px, 32px 32px" }}>
          <svg viewBox="0 0 1000 650" className="absolute inset-0 h-full w-full" aria-label="Evidence graph connections"><defs><marker id="graph-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" /></marker><marker id="graph-alert-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#E11D48" /></marker></defs>{graph.edges.map((edge, index) => { const from = positions[edge.from]; const to = positions[edge.to]; if (!from || !to) return null; const active = !selectedId || edge.from === selectedId || edge.to === selectedId; const filtered = filterType === "ALL" || graph.nodes.find((node) => node.id === edge.from)?.type === filterType || graph.nodes.find((node) => node.id === edge.to)?.type === filterType; return <g key={`${edge.from}-${edge.to}-${index}`} opacity={active && filtered ? 1 : 0.12}><line x1={from.x} y1={from.y + 32} x2={to.x} y2={to.y - 32} stroke={edge.anomaly ? "#E11D48" : "#64748b"} strokeWidth={edge.anomaly ? "2.5" : "1.5"} strokeDasharray={edge.anomaly ? "7 5" : undefined} markerEnd={`url(#${edge.anomaly ? "graph-alert-arrow" : "graph-arrow"})`} /><text x={(from.x + to.x) / 2} y={(from.y + to.y) / 2 - 6} fill={edge.anomaly ? "#BE123C" : "#64748B"} textAnchor="middle" fontSize="9" fontFamily="monospace">{edge.relation}</text></g>; })}</svg>
          {graph.nodes.map((node) => { const position = positions[node.id]; if (!position) return null; const config = TYPE_CONFIG[node.type] ?? TYPE_CONFIG.DOCUMENT; const Icon = config.Icon; const selected = node.id === selectedId; const related = relatedIds.has(node.id); const dimmed = selectedId !== null && !related; return <button key={node.id} onClick={() => setSelectedId(selected ? null : node.id)} className="absolute w-[170px] -translate-x-1/2 -translate-y-1/2 rounded-xl p-3 text-left transition duration-150" style={{ left: `${position.x / 10}%`, top: `${position.y / 6.5}%`, background: selected ? config.soft : node.flagged ? "rgba(244,63,94,0.10)" : "rgba(7,13,26,0.96)", border: `1px solid ${selected ? config.color : node.flagged ? "rgba(244,63,94,0.55)" : "rgba(15,21,53,0.16)"}`, boxShadow: selected ? `0 0 0 3px ${config.soft}, 0 10px 25px rgba(0,0,0,0.35)` : "0 7px 18px rgba(0,0,0,0.25)", opacity: visible(node) && !dimmed ? 1 : 0.25, zIndex: selected ? 20 : 10 }}><div className="flex items-start justify-between gap-2"><span className="flex h-7 w-7 items-center justify-center rounded-lg" style={{ background: config.soft }}><Icon className="h-3.5 w-3.5" style={{ color: config.color }} /></span>{node.flagged && <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />}</div><p className="mt-2 line-clamp-2 text-[11px] font-bold leading-snug text-slate-900">{node.label}</p><span className="mt-2 inline-flex rounded px-1.5 py-0.5 font-mono text-[8px] font-bold" style={{ color: config.color, background: config.soft }}>{node.type.replaceAll("_", " ")}</span></button>; })}
          {status === "error" && <p className="absolute inset-0 flex items-center justify-center text-sm text-rose-700">Unable to load this application&apos;s evidence graph.</p>}
        </div></div>
      </section>
      <aside className="rounded-xl overflow-hidden" style={{ background: "var(--bg-surface)", border: "1px solid rgba(15,21,53,0.096)" }}><div className="border-b border-slate-900/10 px-5 py-4"><h2 className="text-sm font-bold text-slate-900">Evidence Inspector</h2><p className="mt-0.5 text-[10px] text-slate-500">Inspect a node and its direct relationships</p></div><div className="p-5">{selectedNode ? <div className="space-y-5">{(() => { const config = TYPE_CONFIG[selectedNode.type] ?? TYPE_CONFIG.DOCUMENT; const Icon = config.Icon; return <><div className="rounded-xl border border-slate-900/10 bg-slate-900/5 p-4"><span className="flex h-9 w-9 items-center justify-center rounded-lg" style={{ background: config.soft }}><Icon className="h-4 w-4" style={{ color: config.color }} /></span><p className="mt-3 text-sm font-bold text-slate-900">{selectedNode.label}</p><p className="mt-1 font-mono text-[10px]" style={{ color: config.color }}>{selectedNode.id}</p>{selectedNode.flagged && <span className="badge badge-rose mt-3">Flagged evidence</span>}</div><div><p className="mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">Connected relationships ({selectedEdges.length})</p><div className="space-y-2">{selectedEdges.map((edge, index) => <div key={`${edge.relation}-${index}`} className="rounded-lg p-3" style={{ background: edge.anomaly ? "rgba(244,63,94,0.07)" : "rgba(15,21,53,0.048)", border: `1px solid ${edge.anomaly ? "rgba(244,63,94,0.20)" : "rgba(15,21,53,0.096)"}` }}><p className="font-mono text-[10px] font-bold" style={{ color: edge.anomaly ? "#BE123C" : "#4338CA" }}>{edge.relation}</p><p className="mt-1 break-all font-mono text-[9px] text-slate-500">{edge.from === selectedId ? `→ ${edge.to}` : `← ${edge.from}`}</p></div>)}</div></div></>; })()}</div> : <div className="py-16 text-center"><Share2 className="mx-auto h-8 w-8 text-slate-700" /><p className="mt-3 text-xs text-slate-500">Click a graph node to trace its evidence connections.</p></div>}</div></aside>
    </div>
  </div></SidebarLayout>;
}
