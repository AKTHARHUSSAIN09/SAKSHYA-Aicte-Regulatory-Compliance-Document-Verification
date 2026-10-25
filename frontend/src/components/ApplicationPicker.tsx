"use client";

import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

type Application = { institution_id: string; institution_name: string };

export default function ApplicationPicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (applicationId: string) => void;
}) {
  const [applications, setApplications] = useState<Application[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/applications`)
      .then((response) => (response.ok ? response.json() : []))
      .then((data) => setApplications(Array.isArray(data) ? data : []))
      .catch(() => setApplications([]));
  }, []);

  return (
    <label className="block shrink-0">
      <span className="sr-only">Select an application</span>
      <select
        value={value}
        onChange={(event) => {
          localStorage.setItem("sakshya_active_application", event.target.value);
          onChange(event.target.value);
        }}
        className="field min-w-[250px] py-2 text-xs"
        aria-label="Select an application"
      >
        {applications.length === 0 && <option value={value}>{value}</option>}
        {applications.map((application) => (
          <option key={application.institution_id} value={application.institution_id}>
            {application.institution_name} · {application.institution_id}
          </option>
        ))}
      </select>
    </label>
  );
}
