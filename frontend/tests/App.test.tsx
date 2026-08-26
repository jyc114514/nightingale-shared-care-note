import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App, exactCodepointSpan, scrollToElement } from "../src/App";
import { en, zhCN } from "../src/i18n";
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
    owner_role: "staff",
    author_role: "staff",
    author_id: "staff-user",
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
    owner_role: "system",
    author_role: "system",
    author_id: null,
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
  feature_signature: `v1|feature-${index}`,
  item_kind: index === 0 ? "action" : "information",
  status: index === 1 ? "suggested" : "accepted",
  base_priority: 90 - index,
  recency_contribution: 8,
  explicit_risk_contribution: index === 1 ? 12 : 0,
  unresolved_action_contribution: 15,
  clinician_confirmation_contribution: index === 1 ? 0 : 8,
  adaptive_feedback_adjustment: index === 0 ? 2 : 0,
  ranking_explanation: {
    base: 90 - index,
    recency: 8,
    explicit_risk: index === 1 ? 12 : 0,
    unresolved_action: 15,
    clinician_confirmation: index === 1 ? 0 : 8,
    adaptive_feedback: index === 0 ? 2 : 0,
    final: 100 - index,
  },
  display_priority: 100 - index,
  risk_level: index === 1 ? "high" : null,
  risk_reason: "Synthetic review reason",
  action_label: "Review item",
  action_state: "open",
  source_entry_id: index === 0 ? "entry-staff" : "entry-ai",
  source_version_id: "version-1",
  version_number: 1,
  current_entry_version: index === 0 ? 2 : 1,
  source_label: index === 1 ? "AI-scribed · Nurse consult" : "Manual note",
  entry_type: index === 1 ? "ai_nurse_consult_summary" : "staff_note",
  occurred_at: "2026-08-25T08:00:00Z",
  quote: index === 0 ? "Pending renal panel" : `Synthetic item ${index + 1}`,
}));

const context = {
  patient_id: "patient-a",
  policy_version: "gate-d-v1",
  hot_entries: [],
  warm_entries: [],
  archival_summaries: [
    {
      id: "archival-2025-04",
      period_start: "2025-04-01T00:00:00Z",
      period_end: "2025-05-01T00:00:00Z",
      summary_text:
        "Derived historical context for 2025-04: 1 source entry remains canonical.",
      source_count: 1,
      source_manifest_hash: "manifest",
      generated_by: "deterministic-local-archive",
      created_at: "2026-08-26T00:00:00Z",
      refreshed_at: "2026-08-26T00:00:00Z",
      policy_version: "gate-d-v1",
      sources: [
        {
          source_entry_id: "entry-staff",
          source_version_id: "version-1",
          entry_type: "staff_note",
          version_number: 1,
          occurred_at: "2025-04-15T09:00:00Z",
          source_order: 0,
        },
      ],
      derived: true,
    },
  ],
};

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

function mockAuthenticatedApi(
  user = staffUser,
  sourceOptions: {
    startOffset?: number;
    endOffset?: number;
    commentsDelayMs?: number;
    commentsStatus?: number;
  } = {},
) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) return response(user);
      if (url.endsWith("/patients")) return response([patient]);
      if (url.endsWith("/context")) return response(context);
      if (url.endsWith("/timeline")) return response(timeline);
      if (url.endsWith("/glance")) return response(glance);
      if (url.endsWith("/mentionable-users"))
        return response([
          { user_id: "staff-user", display_name: "Staff A", role: "staff" },
          {
            user_id: "clinician-user",
            display_name: "Clinician A",
            role: "clinician",
          },
        ]);
      if (url.endsWith("/tasks")) return response([]);
      if (url.includes("/highlights/") && url.endsWith("/source")) {
        return response({
          highlight: {
            id: "highlight-0",
            clinic_id: "clinic-a",
            patient_id: "patient-a",
            source_entry_id: "entry-staff",
            source_version_id: "version-1",
            start_offset: sourceOptions.startOffset ?? 0,
            end_offset: sourceOptions.endOffset ?? 18,
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
          version_number: 1,
          current_entry_version: 2,
          entry_type: "staff_note",
          source_kind: "manual",
          source_reference: "self-manual",
          occurred_at: "2026-08-25T08:00:00Z",
          version_content: "Pending renal panel requires coordination.",
          quote: "Pending renal panel",
          start_offset: sourceOptions.startOffset ?? 0,
          end_offset: sourceOptions.endOffset ?? 18,
        });
      }
      if (url.includes("/comments")) {
        if (sourceOptions.commentsDelayMs) {
          await new Promise((resolve) =>
            window.setTimeout(resolve, sourceOptions.commentsDelayMs),
          );
        }
        if (sourceOptions.commentsStatus)
          return response(
            { detail: "Comments request failed" },
            sourceOptions.commentsStatus,
          );
        return response([]);
      }
      if (url.includes("/versions")) return response([]);
      if (url.includes("/conflicts")) return response([]);
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
    window.localStorage.clear();
    document.documentElement.lang = "en-SG";
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("renders exact non-BMP codepoint occurrences and rejects approximate spans", () => {
    const text = "A😀 repeat 😀 repeat";
    const quote = "😀 repeat";
    const start = Array.from("A😀 repeat ").length;
    const valid = exactCodepointSpan(
      text,
      quote,
      start,
      start + Array.from(quote).length,
    );
    expect(valid).toEqual({
      valid: true,
      before: "A😀 repeat ",
      quote,
      after: "",
    });
    const invalid = exactCodepointSpan(text, "repeat", 0, 6);
    expect(invalid).toMatchObject({ valid: false });
  });

  it("keeps bilingual dictionaries in parity and localizes chrome only", async () => {
    expect(Object.keys(zhCN).sort()).toEqual(Object.keys(en).sort());
    mockAuthenticatedApi(staffUser, { endOffset: 19 });
    renderApp();
    expect(await screen.findByText("Shared Care Note")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "简体中文" }));
    expect(screen.getByText("共享照护记录")).toBeInTheDocument();
    const localizedSourceButtons = await screen.findAllByRole("button", {
      name: "打开来源",
    });
    fireEvent.click(localizedSourceButtons[0]);
    expect(
      await screen.findByRole("region", { name: "不可变来源" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "关闭来源" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Pending renal panel requires coordination."),
    ).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("zh-CN");
    expect(window.localStorage.getItem("nightingale-language")).toBe("zh-CN");
    fireEvent.click(screen.getByRole("button", { name: "使用指南" }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "关闭指南" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("opens fixed desktop/mobile preview frames without recursive controls", async () => {
    window.history.replaceState(
      {},
      "",
      "/?patient=patient-a&highlight=highlight-0&lang=en",
    );
    mockAuthenticatedApi(staffUser, { endOffset: 19 });
    renderApp();
    await screen.findByText("Shared Care Note");
    const preview = screen.getByTestId("demo-preview-select");
    fireEvent.change(preview, { target: { value: "mobile" } });
    expect(screen.getByTestId("preview-dimensions")).toHaveTextContent(
      "390×844",
    );
    const mobileFrame = screen.getByTestId("demo-preview-iframe");
    expect(mobileFrame).toHaveAttribute("width", "390");
    expect(mobileFrame).toHaveAttribute("height", "844");
    expect(mobileFrame.getAttribute("src")).toContain("patient=patient-a");
    expect(mobileFrame.getAttribute("src")).toContain("highlight=highlight-0");
    expect(mobileFrame.getAttribute("src")).toContain("embedded=1");
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByTestId("demo-preview")).not.toBeInTheDocument();

    fireEvent.change(preview, { target: { value: "desktop" } });
    expect(screen.getByTestId("preview-dimensions")).toHaveTextContent(
      "1440×900",
    );
    expect(screen.getByTestId("demo-preview-iframe")).toHaveAttribute(
      "width",
      "1440",
    );
  });

  it("restores saved locale while URL locale takes precedence", async () => {
    mockAuthenticatedApi();
    const first = renderApp();
    await screen.findByText("Shared Care Note");
    fireEvent.click(screen.getByRole("button", { name: "简体中文" }));
    first.unmount();

    window.history.replaceState({}, "", "/");
    const restored = renderApp();
    expect(await screen.findByText("共享照护记录")).toBeInTheDocument();
    restored.unmount();

    window.history.replaceState({}, "", "/?lang=en");
    const overridden = renderApp();
    expect(await screen.findByText("Shared Care Note")).toBeInTheDocument();
    overridden.unmount();
  });

  it("supports guide keyboard return focus and reduced-motion scrolling", async () => {
    mockAuthenticatedApi();
    renderApp();
    await screen.findByText("Shared Care Note");
    const guideButton = screen.getByRole("button", { name: "Guide" });
    guideButton.focus();
    fireEvent.click(guideButton);
    const closeGuide = screen.getByRole("button", { name: "Close guide" });
    await waitFor(() => expect(document.activeElement).toBe(closeGuide));
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(document.activeElement).toBe(guideButton);

    const target = document.createElement("div");
    const scrollIntoView = vi.fn();
    target.scrollIntoView = scrollIntoView;
    document.body.appendChild(target);
    vi.stubGlobal("matchMedia", () => ({ matches: true }));
    scrollToElement(target);
    expect(scrollIntoView).toHaveBeenCalledWith({
      behavior: "auto",
      block: "center",
    });
    target.remove();
  });

  it("honors a deep-linked locale and preserves provenance source data", async () => {
    window.history.replaceState(
      {},
      "",
      "/?patient=patient-a&highlight=highlight-0&lang=zh-CN",
    );
    mockAuthenticatedApi(staffUser, { endOffset: 19 });
    renderApp();
    expect(
      await screen.findByRole("region", { name: "不可变来源" }),
    ).toBeInTheDocument();
    expect(screen.getByText("不可变来源范围")).toBeInTheDocument();
    expect(
      within(screen.getByTestId("immutable-timeline-source")).getByTestId(
        "source-quote",
      ),
    ).toHaveTextContent("Pending renal panel");
    expect(new URL(window.location.href).searchParams.get("lang")).toBe(
      "zh-CN",
    );
    expect(document.documentElement.lang).toBe("zh-CN");
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

  it("shows bounded ranking contributions and sends pin feedback", async () => {
    mockAuthenticatedApi();
    renderApp();
    const details = (await screen.findAllByTestId("ranking-details"))[0];
    fireEvent.click(details);
    expect(
      (
        await screen.findAllByText(
          "Ranking priority, not a medical risk score.",
        )
      ).length,
    ).toBeGreaterThan(0);
    const pin = screen.getAllByRole("button", { name: "Pin" })[0];
    fireEvent.click(pin);
    await waitFor(() =>
      expect(
        screen.getAllByRole("button", { name: "Unpin" })[0],
      ).toBeInTheDocument(),
    );
  });

  it("supports keyboard mention autocomplete with stable collaborator choices", async () => {
    mockAuthenticatedApi();
    renderApp();
    fireEvent.click(
      (await screen.findAllByRole("button", { name: "Comments" }))[0],
    );
    const body = await screen.findByLabelText("Comment body");
    fireEvent.change(body, { target: { value: "@Clinician" } });
    expect(
      within(screen.getByRole("listbox")).getByRole("option"),
    ).toHaveTextContent("@Clinician A");
    fireEvent.keyDown(body, { key: "Enter" });
    expect(body).toHaveValue("@Clinician A ");
  });

  it("opens Comments immediately, exposes loading/error state, and returns focus", async () => {
    mockAuthenticatedApi(staffUser, { commentsDelayMs: 40 });
    renderApp();
    const commentsButton = (
      await screen.findAllByRole("button", {
        name: "Comments",
      })
    )[0];
    commentsButton.focus();
    fireEvent.click(commentsButton);
    expect(screen.getByTestId("comments-drawer")).toBeVisible();
    expect(screen.getByTestId("comments-loading")).toBeVisible();
    await waitFor(() =>
      expect(screen.getByText("No comments yet.")).toBeVisible(),
    );
    fireEvent.keyDown(document, { key: "Escape" });
    await waitFor(() => expect(document.activeElement).toBe(commentsButton));

    mockAuthenticatedApi(staffUser, { commentsStatus: 500 });
    fireEvent.click(commentsButton);
    expect(await screen.findByTestId("comments-error")).toHaveTextContent(
      "Comments request failed",
    );
  });

  it("opens the task composer in a drawer and returns focus on close", async () => {
    mockAuthenticatedApi();
    renderApp();
    const assignButton = (
      await screen.findAllByRole("button", {
        name: "Assign task",
      })
    )[0];
    assignButton.focus();
    fireEvent.click(assignButton);
    expect(screen.getByTestId("task-drawer")).toBeVisible();
    const title = await screen.findByLabelText("Task title");
    expect(title).toHaveFocus();
    fireEvent.click(screen.getByRole("button", { name: "Close tasks" }));
    await waitFor(() => expect(document.activeElement).toBe(assignButton));
  });

  it("shows derived historical context and distinguishable original source metadata", async () => {
    mockAuthenticatedApi();
    renderApp();
    const historical = await screen.findByTestId("historical-context");
    expect(historical).toContainElement(
      within(historical).getByTestId("derived-summary-label"),
    );
    expect(historical).toHaveTextContent(
      "Derived summary · not the original record",
    );
    expect(historical).toHaveTextContent("Staff note");
    expect(historical).toHaveTextContent("v1");
    fireEvent.click(
      within(historical).getByRole("button", { name: "View original record" }),
    );
    await waitFor(() =>
      expect(screen.getByTestId("timeline-entry-entry-staff")).toHaveClass(
        "border-amber-400",
      ),
    );
  });

  it("keeps the selected source visible after focus fades and closes it cleanly", async () => {
    mockAuthenticatedApi(staffUser, { endOffset: 19 });
    renderApp();
    const sourceButtons = await screen.findAllByRole("button", {
      name: "Open source",
    });
    vi.useFakeTimers();
    await act(async () => {
      fireEvent.click(sourceButtons[0]);
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(
      screen.getByRole("region", { name: "Immutable source" }),
    ).toBeInTheDocument();
    const renderedSource = screen.getByTestId("source-rendered-text");
    expect(renderedSource.textContent).toBe(
      "Pending renal panel requires coordination.",
    );
    expect(
      within(screen.getByTestId("immutable-timeline-source")).getByTestId(
        "source-quote",
      ).className,
    ).not.toContain("px-1");
    await act(async () => {
      vi.advanceTimersByTime(3001);
    });
    expect(screen.getByTestId("immutable-timeline-source")).toBeInTheDocument();
    expect(
      within(screen.getByTestId("immutable-timeline-source")).getByTestId(
        "source-quote",
      ),
    ).toHaveTextContent("Pending renal panel");
    fireEvent.click(screen.getByRole("button", { name: "Close source" }));
    expect(
      screen.queryByRole("region", { name: "Immutable source" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("immutable-timeline-source"),
    ).not.toBeInTheDocument();
    expect(new URL(window.location.href).searchParams.get("patient")).toBe(
      "patient-a",
    );
    expect(new URL(window.location.href).searchParams.has("highlight")).toBe(
      false,
    );
    vi.useRealTimers();
  });

  it("keeps the selected source flow available to comments", async () => {
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

  it("shows an integrity warning instead of approximating an invalid span", async () => {
    mockAuthenticatedApi(staffUser, { startOffset: 99, endOffset: 100 });
    renderApp();
    const sourceButtons = await screen.findAllByRole("button", {
      name: "Open source",
    });
    fireEvent.click(sourceButtons[0]);
    expect(
      await screen.findAllByTestId("provenance-integrity-warning"),
    ).not.toHaveLength(0);
    expect(screen.queryAllByTestId("source-quote")).toHaveLength(0);
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
