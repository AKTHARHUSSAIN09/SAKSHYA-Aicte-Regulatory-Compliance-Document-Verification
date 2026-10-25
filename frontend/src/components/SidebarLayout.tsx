"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Scale,
  Layers,
  FileSearch,
  Share2,
  GitBranch,
  ShieldAlert,
  Cpu,
  Building2,
  Clock,
  ExternalLink,
  ChevronRight,
  Menu,
  X,
  Activity,
} from "lucide-react";

interface SidebarLayoutProps {
  children: React.ReactNode;
}

export const NAV_ITEMS = [
  { href: "/",                                  label: "Command Center",         icon: Layers,     tag: "Mod 1", group: "core",     desc: "Applications & Scrutiny Queue" },
  { href: "/scrutiny/AICTE-2024-FRAUD-002",     label: "Split-Screen Scrutiny",  icon: FileSearch, tag: "Mod 2", group: "core",     desc: "Spatial Bounding Boxes & Clause Diff" },
  { href: "/evidence-graph",                    label: "Evidence Graph",          icon: Share2,     tag: "Mod 3", group: "core",     desc: "Multi-Hop Entity Links" },
  { href: "/timeline-dag",                      label: "Timeline Impossibility",  icon: GitBranch,  tag: "Mod 3", group: "core",     desc: "Allen's Interval Algebra" },
  { href: "/rules-matrix",                      label: "Z3 Rule Conflicts",       icon: Cpu,        tag: "Mod 6", group: "analysis", desc: "SMT Formal Logic" },
  { href: "/attack-lab",                        label: "Forensic Attack Lab",     icon: ShieldAlert,tag: "Mod 4", group: "analysis", desc: "Tampering & ELA Detectors" },
  { href: "/authority-gateway",                 label: "Authority Gateway",       icon: Building2,  tag: "Mod 5", group: "analysis", desc: "DigiLocker, Bhulekh, MCA21" },
  { href: "/regulatory-time-machine",           label: "Time Machine",            icon: Clock,      tag: "WIF",   group: "tools",    desc: "What-if Correction Scenarios" },
  { href: "/audit-ledger",                      label: "Audit Ledger",            icon: Clock,      tag: "Mod 9", group: "tools",    desc: "Event Sourcing & Notices" },
];

const NAV_GROUPS: Record<string, string> = {
  core:     "Core Scrutiny",
  analysis: "Analysis Engines",
  tools:    "Officer Tools",
};

const ENGINE_STATUS = [
  { label: "Z3 SMT Solver",  status: "SAT",    color: "#059669" },
  { label: "OpenCV ELA",     status: "READY",  color: "#1E2A78" },
  { label: "Timeline DAG",   status: "ACTIVE", color: "#2563EB" },
];

export default function SidebarLayout({ children }: SidebarLayoutProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div
      className="min-h-screen flex"
      style={{ background: "var(--bg-base)", color: "var(--text-primary)" }}
    >
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 lg:hidden"
          style={{ background: "rgba(0,0,0,0.65)", backdropFilter: "blur(4px)" }}
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* ── Sidebar ───────────────────────────────── */}
      <aside
        className={`
          fixed lg:sticky top-0 h-screen z-40
          flex flex-col shrink-0 w-60 xl:w-64
          transition-transform duration-300 ease-in-out
          ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
        style={{
          background: "linear-gradient(180deg, #ffffff 0%, #F8F9FD 100%)",
          borderRight: "1px solid rgba(30,42,120,0.08)",
        }}
      >
        {/* Brand mark */}
        <div
          className="flex items-center gap-3 px-5 py-5"
          style={{ borderBottom: "1px solid rgba(30,42,120,0.08)" }}
        >
          {/* Seal-style logo */}
          <div
            className="relative w-9 h-9 rounded-full flex items-center justify-center shrink-0"
            style={{
              background: "linear-gradient(135deg, #151F5C, #1E2A78, #2B3A9E)",
              boxShadow: "0 0 0 2px rgba(30,42,120,0.18), 0 4px 14px rgba(30,42,120,0.25)",
            }}
          >
            <Scale className="w-4 h-4" style={{ color: "#ffffff" }} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span
                className="font-black text-base tracking-[0.22em] leading-none"
                style={{
                  background: "linear-gradient(90deg, #1E2A78, #3347B0, #F28C28)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  filter: "drop-shadow(0 0 8px rgba(30,42,120,0.28))",
                }}
              >
                SAKSHYA
              </span>
              <span className="badge badge-gold" style={{ fontSize: "0.5rem" }}>AICTE</span>
            </div>
            <p
              className="text-[9px] mt-0.5 tracking-widest uppercase"
              style={{ color: "var(--text-muted)" }}
            >
              Regulatory Intelligence
            </p>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="ml-auto lg:hidden"
            style={{ color: "var(--text-muted)" }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
          {["core", "analysis", "tools"].map((groupKey) => (
            <div key={groupKey}>
              {/* Group label */}
              <div
                className="px-3 mb-1.5 text-[8px] font-black tracking-[0.2em] uppercase"
                style={{ color: "var(--text-faint)", letterSpacing: "0.2em" }}
              >
                {NAV_GROUPS[groupKey]}
              </div>

              <div className="space-y-0.5">
                {NAV_ITEMS.filter((i) => i.group === groupKey).map((item) => {
                  const Icon = item.icon;
                  const isActive =
                    item.href === "/"
                      ? pathname === "/"
                      : pathname.startsWith(item.href) ||
                        (item.href.startsWith("/scrutiny") && pathname.startsWith("/scrutiny"));

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className="group flex items-center gap-3 px-3 py-2.5 rounded-lg relative transition-all duration-150"
                      style={
                        isActive
                          ? {
                              background: "linear-gradient(90deg, rgba(30,42,120,0.12), rgba(30,42,120,0.04))",
                              border: "1px solid rgba(30,42,120,0.18)",
                            }
                          : {
                              border: "1px solid transparent",
                              color: "var(--text-muted)",
                            }
                      }
                    >
                      {/* Active left bar */}
                      {isActive && (
                        <span
                          className="absolute left-0 top-[20%] bottom-[20%] w-[2px] rounded-r-full"
                          style={{ background: "var(--accent)" }}
                        />
                      )}

                      <Icon
                        className="w-3.5 h-3.5 shrink-0 transition-colors"
                        style={{ color: isActive ? "var(--amber)" : "var(--text-faint)" }}
                      />

                      <span
                        className="flex-1 truncate text-xs font-semibold"
                        style={{ color: isActive ? "var(--text-primary)" : "var(--text-muted)" }}
                      >
                        {item.label}
                      </span>

                      <span
                        className="text-[8px] font-mono font-black px-1.5 py-0.5 rounded shrink-0 tracking-wider"
                        style={
                          isActive
                            ? {
                                background: "rgba(30,42,120,0.15)",
                                color: "var(--amber)",
                                border: "1px solid rgba(30,42,120,0.25)",
                              }
                            : {
                                background: "rgba(15,21,53,0.048)",
                                color: "var(--text-faint)",
                                border: "1px solid rgba(15,21,53,0.096)",
                              }
                        }
                      >
                        {item.tag}
                      </span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Engine telemetry */}
        <div
          className="mx-3 mb-3 rounded-xl p-3.5 space-y-2.5"
          style={{
            background: "rgba(30,42,120,0.03)",
            border: "1px solid rgba(30,42,120,0.08)",
          }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-3 h-3" style={{ color: "var(--amber)" }} />
            <span
              className="text-[8px] font-black tracking-[0.18em] uppercase"
              style={{ color: "var(--text-muted)" }}
            >
              System Telemetry
            </span>
          </div>
          {ENGINE_STATUS.map((e) => (
            <div key={e.label} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{
                    background: e.color,
                    boxShadow: `0 0 5px ${e.color}`,
                  }}
                />
                <span
                  className="text-[10px]"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {e.label}
                </span>
              </div>
              <span
                className="text-[9px] font-mono font-black"
                style={{ color: e.color }}
              >
                {e.status}
              </span>
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main area ─────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header
          className="sticky top-0 z-30 h-13 flex items-center px-5 xl:px-8 gap-4"
          style={{
            background: "rgba(3,7,15,0.88)",
            borderBottom: "1px solid rgba(30,42,120,0.07)",
            backdropFilter: "blur(18px)",
            height: "3.25rem",
          }}
        >
          {/* Mobile burger */}
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden"
            style={{ color: "var(--text-muted)" }}
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Breadcrumb */}
          <div
            className="flex items-center gap-2 text-[11px] min-w-0"
            style={{ color: "var(--text-muted)" }}
          >
            <span className="hidden sm:block">Ministry of Education</span>
            <ChevronRight className="hidden sm:block w-3 h-3 shrink-0" />
            <span className="hidden md:block">AICTE Approval Bureau</span>
            <ChevronRight className="hidden md:block w-3 h-3 shrink-0" />
            <span
              className="font-semibold truncate"
              style={{ color: "var(--text-primary)" }}
            >
              {NAV_ITEMS.find((n) =>
                n.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(n.href)
              )?.label ?? "Scrutiny"}
            </span>
          </div>

          <div className="ml-auto flex items-center gap-3">
            {/* Session pill */}
            <div
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px]"
              style={{
                background: "rgba(4,120,87,0.08)",
                border: "1px solid rgba(4,120,87,0.18)",
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  background: "var(--emerald-bright)",
                  boxShadow: "0 0 6px #059669",
                }}
              />
              <span
                className="font-semibold"
                style={{ color: "#047857" }}
              >
                Sr. Scrutiny Officer
              </span>
            </div>

            {/* API Docs */}
            <Link
              href={`${API_BASE.replace("/api/v1", "")}/docs`}
              target="_blank"
              className="flex items-center gap-1.5 text-[11px] px-2.5 py-1.5 rounded-lg transition"
              style={{ color: "var(--text-muted)" }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.color = "var(--amber)";
                (e.currentTarget as HTMLElement).style.background = "rgba(30,42,120,0.06)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.color = "var(--text-muted)";
                (e.currentTarget as HTMLElement).style.background = "transparent";
              }}
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:block">API Docs</span>
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-5 xl:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
