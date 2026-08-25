import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/App";
import type { Me } from "../src/types";

const staffUser: Me = {
  id: "staff-user",
  email: "staff.a@clinic-a.test",
  display_name: "Staff A",
  memberships: [
    { clinic_id: "clinic-a", clinic_name: "Clinic A", role: "staff" },
  ],
  patient_ids: [],
};

const patientUser: Me = {
  id: "patient-user",
  email: "sarah.patient@clinic-a.test",
  display_name: "Sarah Patient",
  memberships: [],
  patient_ids: ["patient-a"],
};

const patient = {
  id: "patient-a",
  clinic_id: "clinic-a",
  synthetic_display_name: "Sarah Tan",
  created_at: "2026-08-25T00:00:00Z",
};

const timeline = [
  {
    id: "entry-staff",
    clinic_id: "clinic-a",
    patient_id: "patient-a",
    entry_type: "staff_note",
    author_role: "staff",
    created_by_user_id: "staff-user",
    current_version: 2,
    content: "Pending renal panel requires coordination.",
    occurred_at: "2026-08-25T08:00:00Z",
    source_kind: "manual",
    source_reference: "self-manual",
    created_at: "2026-08-25T08:00:00Z",
    updated_at: "2026-08-25T08:00:00Z",
  },
  {
    id: "entry-ai",
    clinic_id: "clinic-a",
    patient_id: "patient-a",
    entry_type: "ai_nurse_consult_summary",
    author_role: "system",
    created_by_user_id: null,
    current_version: 1,
    content: "Unresolved cardiology referral noted in the nurse consult.",
    occurred_at: "2026-08-24T10:00:00Z",
    source_kind: "nurse_consult",
    source_reference: "synthetic-nurse-consult",
    created_at: "2026-08-24T10:00:00Z",
    updated_at: "2026-08-24T10:00:00Z",
  },
];

const glance = Array.from({ length: 6 }, (_, index) => ({
  id: `highlight-${index}`,
  content_summary:
    index === 0 ? "Pending renal panel" : `Synthetic item ${index + 1}`,
  item_kind: index === 0 ? "action" : "information",
  status: index === 1 ? "suggested" : "accepted",
  display_priority: 100 - index,
  risk_level: index === 1 ? "high" : null,
  risk_reason: "Synthetic review reason",
  action_label: "Review item",
  action_state: "open",
  source_entry_id: index === 0 ? "entry-staff" : "entry-ai",
  source_version_id: "version-1",
  source_label: index === 1 ? "AI-scribed · Nurse consult" : "Manual note",
  entry_type: index === 1 ? "ai_nurse_consult_summary" : "staff_note",
  occurred_at: "2026-08-25T08:00:00Z",
  quote: index === 0 ? "Pending renal panel" : `Synthetic item ${index + 1}`,
}));

function response(payload: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => JSON.stringify(payload),
  };
}

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}

function mockAuthenticatedApi(user = staffUser) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) return response(user);
      if (url.endsWith("/patients")) return response([patient]);
      if (url.endsWith("/timeline")) return response(timeline);
      if (url.endsWith("/glance")) return response(glance);
      if (url.includes("/highlights/") && url.endsWith("/source")) {
        return response({
          highlight: {
            id: "highlight-0",
            clinic_id: "clinic-a",
            patient_id: "patient-a",
            source_entry_id: "entry-staff",
            source_version_id: "version-1",
            start_offset: 0,
            end_offset: 18,
            quote: "Pending renal panel",
            quote_sha256: "hash",
            offset_unit: "unicode_codepoint",
            item_kind: "action",
            status: "accepted",
            display_priority: 100,
            risk_level: null,
            risk_reason: "Synthetic review reason",
            action_label: "Review item",
            action_state: "open",
            created_by_role: "staff",
            created_by_user_id: "staff-user",
            reviewed_by_user_id: null,
            reviewed_at: null,
            created_at: "2026-08-25T08:00:00Z",
            updated_at: "2026-08-25T08:00:00Z",
          },
          source_entry_id: "entry-staff",
          source_version_id: "version-1",
          entry_type: "staff_note",
          source_kind: "manual",
          source_reference: "self-manual",
          occurred_at: "2026-08-25T08:00:00Z",
          version_content: "Pending renal panel requires coordination.",
          quote: "Pending renal panel",
          start_offset: 0,
          end_offset: 18,
        });
      }
      if (url.includes("/comments")) return response([]);
      if (url.includes("/versions")) return response([]);
      if (url.endsWith("/auth/logout")) return response(undefined, 204);
      if (init?.method === "POST" || init?.method === "PATCH")
        return response({});
      return response({});
    }),
  );
}

describe("Gate B shared care note", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows loading then a real login error", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          response({ detail: "Invalid email or password" }, 401),
        ),
    );
    renderApp();
    expect(screen.getByText("Checking secure session…")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { name: "Shared Care Note" }),
    ).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "wrong" },
    });
    fireEvent.submit(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Invalid email or password",
    );
  });

  it("loads Glance with six items, AI labels, and role-aware controls", async () => {
    mockAuthenticatedApi();
    renderApp();
    expect(
      await screen.findByText(/6 active source-linked items · max 6/),
    ).toBeInTheDocument();
    expect(
      screen.getAllByText("AI-scribed · Nurse consult").length,
    ).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: "Open source" })).toHaveLength(
      6,
    );
    expect(screen.getAllByRole("button", { name: "Comments" }).length).toBe(2);
  });

  it("opens an immutable source and the internal comments flow", async () => {
    mockAuthenticatedApi();
    renderApp();
    const sourceButtons = await screen.findAllByRole("button", {
      name: "Open source",
    });
    fireEvent.click(sourceButtons[0]);
    expect(await screen.findByText("Immutable source")).toBeInTheDocument();
    expect(screen.getByText(/Exact span/)).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: "Comments" })[0]);
    expect(
      await screen.findByRole("region", { name: "Comments" }),
    ).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Comment body"), {
      target: { value: "Follow up" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add comment" }));
    await waitFor(() =>
      expect(screen.getByLabelText("Comment body")).toHaveValue(""),
    );
  });

  it("does not expose internal Glance or comments to a patient session", async () => {
    mockAuthenticatedApi(patientUser);
    renderApp();
    expect(
      await screen.findByText("Internal Glance View is hidden"),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Top Card · Glance View"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Comments" }),
    ).not.toBeInTheDocument();
  });
});
