import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  App,
  exactCodepointSpan,
  productizeProvenanceSource,
  productizeSuggestionText,
  scrollToElement,
} from "../src/App";
import { en, zhCN } from "../src/i18n";
import type {
  ClinicalAssertion,
  ClinicalAssertionSource,
  ClinicalConflict,
  Me,
  Patient,
  ProvenanceSource,
  Version,
} from "../src/types";

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

const clinicianUser: Me = {
  id: "clinician-user",
  email: "clinician.a@clinic-a.test",
  display_name: "Clinician A",
  memberships: [
    { clinic_id: "clinic-a", clinic_name: "Clinic A", role: "clinician" },
  ],
  patient_ids: [],
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

const positiveAssertion: ClinicalAssertion = {
  id: "assertion-positive",
  clinic_id: "clinic-a",
  patient_id: "patient-a",
  domain: "allergy",
  concept_key: "penicillin",
  polarity: "present",
  verification_status: "unconfirmed",
  criticality: "unable_to_assess",
  source_entry_id: "entry-staff",
  source_version_id: "version-1",
  start_offset: 0,
  end_offset: 19,
  quote: "Pending renal panel",
  quote_sha256: "hash-positive",
  offset_unit: "unicode_codepoint",
  asserted_by_role: "staff",
  asserted_by_user_id: "staff-user",
  status: "active",
  superseded_at: null,
  created_at: "2026-08-25T08:00:00Z",
  updated_at: "2026-08-25T08:00:00Z",
};

const negativeAssertion: ClinicalAssertion = {
  id: "assertion-negative",
  clinic_id: "clinic-a",
  patient_id: "patient-a",
  domain: "allergy",
  concept_key: "all_drug_allergies",
  polarity: "absent",
  verification_status: "unconfirmed",
  criticality: "unable_to_assess",
  source_entry_id: "entry-ai",
  source_version_id: "version-ai",
  start_offset: 0,
  end_offset: 18,
  quote: "no known allergies",
  quote_sha256: "hash-negative",
  offset_unit: "unicode_codepoint",
  asserted_by_role: "system",
  asserted_by_user_id: null,
  status: "active",
  superseded_at: null,
  created_at: "2026-08-24T10:00:00Z",
  updated_at: "2026-08-24T10:00:00Z",
};

const clinicalConflict: ClinicalConflict = {
  id: "clinical-conflict-1",
  clinic_id: "clinic-a",
  patient_id: "patient-a",
  conflict_type: "allergy_assertion_conflict",
  status: "open",
  positive_assertion_id: positiveAssertion.id,
  negative_assertion_id: negativeAssertion.id,
  version: 1,
  resolution: null,
  adjudicated_by_user_id: null,
  adjudicated_at: null,
  created_at: "2026-08-25T10:00:00Z",
  updated_at: "2026-08-25T10:00:00Z",
  positive_assertion: positiveAssertion,
  negative_assertion: negativeAssertion,
};

function assertionSource(
  assertion: ClinicalAssertion,
  versionContent: string,
  entryType: string,
  authorRole: "staff" | "system",
): ClinicalAssertionSource {
  return {
    assertion,
    source_entry_id: assertion.source_entry_id,
    source_version_id: assertion.source_version_id,
    version_number: 1,
    current_entry_version: assertion.source_version_id === "version-1" ? 2 : 1,
    version_content: versionContent,
    entry_type: entryType,
    source_kind: authorRole === "staff" ? "manual" : "patient_ai_session",
    source_reference: "synthetic-source",
    author_role: authorRole,
    author_id: authorRole === "staff" ? "staff-user" : null,
    occurred_at: assertion.created_at,
    quote: assertion.quote,
    start_offset: assertion.start_offset,
    end_offset: assertion.end_offset,
    quote_sha256: assertion.quote_sha256,
    offset_unit: "unicode_codepoint",
    source_is_current_version: assertion.source_version_id !== "version-1",
  };
}

const protectedGlance = {
  ...glance[0],
  id: "conflict-highlight",
  content_summary: "Pending renal panel",
  item_kind: "flag",
  status: "conflict_review",
  ranking_explanation: {
    ...glance[0].ranking_explanation,
    pre_floor: 50,
    safety_floor: 95,
    floor_applied: 1,
    final: 95,
  },
  display_priority: 95,
  risk_level: null,
  action_label: "Review allergy conflict",
  action_state: "open",
  clinical_conflict_id: clinicalConflict.id,
  safety_class: "allergy_conflict",
  safety_floor: 95,
  source_entry_id: positiveAssertion.source_entry_id,
  source_version_id: positiveAssertion.source_version_id,
  version_number: 1,
  current_entry_version: 2,
  quote: positiveAssertion.quote,
};

const protectedGlanceResponse = [protectedGlance, ...glance.slice(1)];
const needsMoreConflict: ClinicalConflict = {
  ...clinicalConflict,
  version: 2,
  resolution: "needs_more_information",
  updated_at: "2026-08-25T10:01:00Z",
};

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

function audioResponse(status = 200, contentType = "audio/wav") {
  const blob = new Blob(["RIFF synthetic audio"], { type: contentType });
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": contentType }),
    blob: async () => blob,
    text: async () => "",
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

function getProtectedCard(): HTMLElement {
  const card = screen
    .getAllByTestId("glance-item")
    .find((element) => element.dataset.protectedConflict === "true");
  if (!card) throw new Error("protected conflict card not found");
  return card;
}

function mockAuthenticatedApi(
  user = staffUser,
  sourceOptions: {
    startOffset?: number;
    endOffset?: number;
    patients?: Patient[];
    timelineAfterRefresh?: typeof timeline;
    commentsDelayMs?: number;
    commentsStatus?: number;
    aiProviderResponse?: unknown;
    aiJobResponse?: unknown;
    voiceProviderResponse?: unknown;
    voiceSamplesResponse?: unknown;
    voiceSessionResponse?: unknown;
    voiceAudioStatus?: number;
    voiceAudioContentType?: string;
    voiceAudioDelayMs?: number;
    versionsResponse?: Version[];
    glanceResponse?: unknown;
    clinicalConflictResponse?: ClinicalConflict;
    latestClinicalConflictResponse?: ClinicalConflict;
    assertionSources?: Record<string, ClinicalAssertionSource>;
    adjudicationResponse?: ClinicalConflict;
    adjudicationStatus?: number;
    impressionStatus?: number;
    feedbackResponse?: unknown;
  } = {},
) {
  let timelineCallCount = 0;
  let clinicalConflictCallCount = 0;
  const fetchMock = vi.fn(
    async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) return response(user);
      if (url.endsWith("/patients"))
        return response(sourceOptions.patients ?? [patient]);
      if (url.endsWith("/context")) return response(context);
      if (url.endsWith("/timeline")) {
        timelineCallCount += 1;
        return response(
          sourceOptions.timelineAfterRefresh && timelineCallCount > 1
            ? sourceOptions.timelineAfterRefresh
            : timeline,
        );
      }
      if (url.endsWith("/glance"))
        return response(sourceOptions.glanceResponse ?? glance);
      if (url.includes("/clinical-assertions/") && url.endsWith("/source")) {
        const assertionId =
          url.split("/clinical-assertions/")[1]?.split("/source")[0] ?? "";
        return response(sourceOptions.assertionSources?.[assertionId] ?? {});
      }
      if (url.includes("/clinical-conflicts/") && url.endsWith("/adjudicate")) {
        if (sourceOptions.adjudicationStatus) {
          return response(
            {
              detail: {
                message: "Clinical conflict version is stale",
                actual_version: 2,
              },
            },
            sourceOptions.adjudicationStatus,
          );
        }
        return response(
          sourceOptions.adjudicationResponse ??
            sourceOptions.clinicalConflictResponse ??
            {},
        );
      }
      if (url.includes("/clinical-conflicts/"))
        return response(
          ++clinicalConflictCallCount > 1
            ? (sourceOptions.latestClinicalConflictResponse ??
                sourceOptions.clinicalConflictResponse ??
                {})
            : (sourceOptions.clinicalConflictResponse ??
                sourceOptions.latestClinicalConflictResponse ??
                {}),
        );
      if (url.endsWith("/glance-impressions") && init?.method === "POST") {
        return response({}, sourceOptions.impressionStatus ?? 200);
      }
      if (url.includes("/highlights/") && url.endsWith("/feedback")) {
        return response(
          sourceOptions.feedbackResponse ?? {
            applied_to_profile: true,
            suppression_reason: null,
          },
        );
      }
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
      if (url.endsWith("/voice/provider"))
        return response(sourceOptions.voiceProviderResponse ?? {});
      if (url.endsWith("/voice/samples"))
        return response(sourceOptions.voiceSamplesResponse ?? []);
      if (url.includes("/voice/samples/") && url.endsWith("/audio")) {
        if (sourceOptions.voiceAudioDelayMs) {
          await new Promise((resolve) =>
            window.setTimeout(resolve, sourceOptions.voiceAudioDelayMs),
          );
        }
        return audioResponse(
          sourceOptions.voiceAudioStatus ?? 200,
          sourceOptions.voiceAudioContentType ?? "audio/wav",
        );
      }
      if (url.endsWith("/voice/sessions") && init?.method === "POST")
        return response(sourceOptions.voiceSessionResponse ?? {});
      if (url.endsWith("/ai-processing/provider"))
        return response(
          sourceOptions.aiProviderResponse ?? {
            provider_name: "fixture-redacted-v1",
            model: "deterministic-local",
            configured: true,
            mode: "fixture",
          },
        );
      if (url.endsWith("/ai-processing") && init?.method === "POST") {
        return response(
          sourceOptions.aiJobResponse ?? {
            id: "job-fixture",
            clinic_id: "clinic-a",
            patient_id: "patient-a",
            interaction_type: "ai_doctor_consult_summary",
            provider_name: "fixture-redacted-v1",
            status: "completed",
            idempotency_key: "job-fixture-key",
            input_hash: "hash",
            source_reference: "synthetic-source",
            error_code: null,
            entry_id: "entry-ai-new",
            highlight_id: null,
            created_at: "2026-08-26T00:00:00Z",
            updated_at: "2026-08-26T00:00:00Z",
            completed_at: "2026-08-26T00:00:00Z",
          },
        );
      }
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
      if (url.includes("/versions"))
        return response(sourceOptions.versionsResponse ?? []);
      if (url.includes("/conflicts")) return response([]);
      if (url.endsWith("/auth/logout")) return response(undefined, 204);
      if (init?.method === "POST" || init?.method === "PATCH")
        return response({});
      return response({});
    },
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function installFakeEventSource() {
  let constructorCount = 0;
  let latestStream: {
    emit: (resourceType: string) => void;
  } | null = null;

  class FakeEventSource {
    onopen: (() => void) | null = null;
    onerror: (() => void) | null = null;
    private collaborationListener:
      ((event: MessageEvent<string>) => void) | null = null;

    constructor() {
      constructorCount += 1;
      latestStream = {
        emit: (resourceType: string) => this.emit(resourceType),
      };
      queueMicrotask(() => this.onopen?.());
    }

    addEventListener(
      type: string,
      listener: (event: MessageEvent<string>) => void,
    ) {
      if (type === "collaboration") this.collaborationListener = listener;
    }

    close() {}

    emit(resourceType: string) {
      this.collaborationListener?.({
        data: JSON.stringify({ resource_type: resourceType }),
      } as MessageEvent<string>);
    }
  }

  vi.stubGlobal("EventSource", FakeEventSource);
  return {
    count: () => constructorCount,
    emit: (resourceType: string) => latestStream?.emit(resourceType),
  };
}

describe("Gate B shared care note", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/");
    window.localStorage.clear();
    document.documentElement.lang = "en-SG";
    if (typeof URL.createObjectURL !== "function") {
      Object.defineProperty(URL, "createObjectURL", {
        configurable: true,
        writable: true,
        value: () => "",
      });
    }
    if (typeof URL.revokeObjectURL !== "function") {
      Object.defineProperty(URL, "revokeObjectURL", {
        configurable: true,
        writable: true,
        value: () => undefined,
      });
    }
    let objectUrlCounter = 0;
    vi.spyOn(URL, "createObjectURL").mockImplementation(
      () => `blob:nightingale-test-${++objectUrlCounter}`,
    );
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
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

  it("productizes legacy suggestion prefixes without breaking source offsets", () => {
    const rawText = "Fixture suggestion: Pending renal panel";
    const quote = "Pending renal panel";
    const storedStart = Array.from("Fixture suggestion: ").length;
    const source = {
      version_content: rawText,
      quote,
      start_offset: storedStart,
      end_offset: storedStart + Array.from(quote).length,
    } as ProvenanceSource;
    const displayed = productizeProvenanceSource(source);
    expect(productizeSuggestionText(rawText)).toBe(
      "Care note suggestion: Pending renal panel",
    );
    expect(displayed.start_offset).toBe(storedStart + 2);
    expect(
      Array.from(displayed.version_content)
        .slice(displayed.start_offset, displayed.end_offset)
        .join(""),
    ).toBe(quote);
  });

  it("keeps bilingual dictionaries in parity and localizes chrome only", async () => {
    expect(Object.keys(zhCN).sort()).toEqual(Object.keys(en).sort());
    mockAuthenticatedApi(staffUser, { endOffset: 19 });
    renderApp();
    expect(await screen.findByText("Shared Care Note")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "简体中文" }));
    expect(screen.getByText("共享照护记录")).toBeInTheDocument();
    expect(await screen.findByTestId("ai-scribe-panel")).toHaveTextContent(
      "AI 辅助记录",
    );
    const localizedSourceButtons = await screen.findAllByRole("button", {
      name: "打开来源",
    });
    fireEvent.click(localizedSourceButtons[0]);
    expect(
      await screen.findByRole("region", { name: "原始来源" }),
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

  it("shows the internal AI-assisted panel and a safe completed job", async () => {
    mockAuthenticatedApi(staffUser, {
      aiProviderResponse: {
        provider_name: "deepseek-v4-flash",
        model: "deepseek-v4-flash",
        configured: true,
        mode: "deepseek",
      },
      aiJobResponse: {
        id: "job-deepseek",
        clinic_id: "clinic-a",
        patient_id: "patient-a",
        interaction_type: "ai_doctor_consult_summary",
        provider_name: "deepseek-v4-flash",
        status: "completed",
        idempotency_key: "job-deepseek-key",
        input_hash: "hash",
        source_reference: "synthetic-source",
        error_code: null,
        entry_id: "entry-ai-new",
        highlight_id: null,
        created_at: "2026-08-26T00:00:00Z",
        updated_at: "2026-08-26T00:00:00Z",
        completed_at: "2026-08-26T00:00:00Z",
      },
    });
    renderApp();
    const panel = await screen.findByTestId("ai-scribe-panel");
    expect(panel).toHaveTextContent("AI-assisted note");
    expect(panel).not.toHaveTextContent("DeepSeek V4 Flash");
    expect(panel).toHaveTextContent(
      "Demo text only. Do not enter real patient information.",
    );
    expect(screen.getByTestId("ai-technical-details")).not.toHaveAttribute(
      "open",
    );
    fireEvent.click(
      within(panel).getByRole("button", { name: "Create suggestion" }),
    );
    const result = await screen.findByTestId("ai-job-result");
    expect(result).toHaveTextContent("Ready for review");
    expect(result).not.toHaveTextContent("deepseek-v4-flash");
    expect(result).not.toHaveTextContent("DeepSeek");
    expect(result).not.toHaveTextContent("api-key");
    expect(result).not.toHaveTextContent(".txt");
  });

  it("shows processing and failed provider states without exposing configuration", async () => {
    mockAuthenticatedApi(staffUser, {
      aiJobResponse: {
        id: "job-processing",
        clinic_id: "clinic-a",
        patient_id: "patient-a",
        interaction_type: "ai_doctor_consult_summary",
        provider_name: "fixture-redacted-v1",
        status: "processing",
        idempotency_key: "job-processing-key",
        input_hash: "hash",
        source_reference: "synthetic-source",
        error_code: null,
        entry_id: null,
        highlight_id: null,
        created_at: "2026-08-26T00:00:00Z",
        updated_at: "2026-08-26T00:00:00Z",
        completed_at: null,
      },
    });
    renderApp();
    const panel = await screen.findByTestId("ai-scribe-panel");
    fireEvent.click(
      within(panel).getByRole("button", { name: "Create suggestion" }),
    );
    expect(await screen.findByTestId("ai-job-result")).toHaveTextContent(
      "In progress",
    );

    cleanup();
    mockAuthenticatedApi(staffUser, {
      aiJobResponse: {
        id: "job-failed",
        clinic_id: "clinic-a",
        patient_id: "patient-a",
        interaction_type: "ai_doctor_consult_summary",
        provider_name: "deepseek-v4-flash",
        status: "failed_provider",
        idempotency_key: "job-failed-key",
        input_hash: "hash",
        source_reference: "synthetic-source",
        error_code: "provider_auth_failed",
        entry_id: null,
        highlight_id: null,
        created_at: "2026-08-26T00:00:00Z",
        updated_at: "2026-08-26T00:00:00Z",
        completed_at: "2026-08-26T00:00:00Z",
      },
    });
    renderApp();
    const failedPanel = await screen.findByTestId("ai-scribe-panel");
    fireEvent.click(
      within(failedPanel).getByRole("button", { name: "Create suggestion" }),
    );
    const failedResult = await screen.findByTestId("ai-job-result");
    expect(failedResult).toHaveTextContent(
      "The suggestion could not be created. Your existing record was not changed.",
    );
    expect(failedResult).not.toHaveTextContent("provider_auth_failed");
    expect(failedResult).not.toHaveTextContent(".nightingale-local.json");
    expect(failedResult).not.toHaveTextContent("api.txt");
  });

  it("shows a Voice note with segments and source navigation", async () => {
    const fetchMock = mockAuthenticatedApi(staffUser, {
      voiceProviderResponse: {
        provider_name: "mock-transcript-fixture",
        model: "precomputed-v1",
        mode: "fixture",
        enabled: true,
        disclosure:
          "Mock transcript fixture - local ASR unavailable in this environment.",
      },
      voiceSamplesResponse: [
        {
          sample_id: "nurse-follow-up",
          label: "Synthetic nurse follow-up",
          scope: "clinical",
          interaction_type: "ai_nurse_consult_summary",
          duration_ms: 24000,
          audio_url: "/patients/patient-a/voice/samples/nurse-follow-up/audio",
          provider_disclosure:
            "Mock transcript fixture - local ASR unavailable in this environment.",
        },
      ],
      voiceSessionResponse: {
        id: "voice-session-1",
        clinic_id: "clinic-a",
        patient_id: "patient-a",
        actor_role: "staff",
        interaction_type: "ai_nurse_consult_summary",
        sample_id: "nurse-follow-up",
        audio_sha256: "a".repeat(64),
        audio_duration_ms: 24000,
        asr_provider: "mock-transcript-fixture",
        asr_model: "precomputed-v1",
        language: "en",
        language_probability: null,
        status: "completed",
        error_code: null,
        entry_id: "entry-voice",
        highlight_id: "highlight-0",
        source_segment_id: "voice-segment-0",
        created_at: "2026-08-27T00:00:00Z",
        completed_at: "2026-08-27T00:00:00Z",
        patient_safe: false,
        segments: [
          {
            id: "voice-segment-0",
            segment_index: 0,
            start_ms: 0,
            end_ms: 8000,
            text: "This is a synthetic nurse follow-up.",
            confidence: null,
          },
          {
            id: "voice-segment-1",
            segment_index: 1,
            start_ms: 8000,
            end_ms: 16000,
            text: "The scheduled laboratory review remains pending.",
            confidence: null,
          },
        ],
      },
    });
    renderApp();
    const panel = await screen.findByTestId("voice-panel");
    expect(panel).toHaveTextContent("Voice note");
    expect(panel).toHaveTextContent("Review a pre-recorded care conversation");
    expect(panel).not.toHaveTextContent("mock-transcript-fixture");
    expect(panel).not.toHaveTextContent("Level-C");
    expect(panel).not.toHaveTextContent("precomputed-v1");
    expect(panel).not.toHaveTextContent("provider");
    expect(panel).not.toHaveTextContent("ASR confidence");
    const voiceAbout = screen.getByTestId("voice-about-details");
    expect(voiceAbout).not.toHaveAttribute("open");
    fireEvent.click(within(voiceAbout).getByText("About this example"));
    expect(voiceAbout).toHaveTextContent(
      "pre-recorded synthetic care conversation and a prepared timestamped transcript",
    );
    const audio = within(panel).getByTestId("voice-audio");
    const audioCall = await waitFor(() => {
      const call = fetchMock.mock.calls.find(([input]) =>
        String(input).endsWith(
          "/patients/patient-a/voice/samples/nurse-follow-up/audio",
        ),
      );
      expect(call).toBeDefined();
      return call;
    });
    expect(audioCall?.[1]).toMatchObject({ credentials: "include" });
    expect(audio).toHaveAttribute("data-audio-state", "loading");
    fireEvent.loadedMetadata(audio);
    expect(audio).toHaveAttribute("data-audio-state", "ready");
    let currentTime = 0;
    Object.defineProperty(audio, "currentTime", {
      configurable: true,
      get: () => currentTime,
      set: (value: number) => {
        currentTime = value;
      },
    });
    fireEvent.click(
      within(panel).getByRole("button", {
        name: "Create care-note suggestion",
      }),
    );
    const result = await screen.findByTestId("voice-session-result");
    expect(result).toHaveTextContent("Suggestion status: Ready for review");
    expect(result).toHaveTextContent("This is a synthetic nurse follow-up.");
    expect(result).not.toHaveTextContent("ASR confidence");
    fireEvent.click(within(result).getByTestId("voice-segment-1"));
    expect(currentTime).toBe(8);
    fireEvent.click(
      within(result).getByRole("button", { name: "View source" }),
    );
    expect(
      await screen.findByTestId("immutable-timeline-source"),
    ).toBeInTheDocument();
  });

  it("keeps patient Voice UI limited to the patient fixture and no internal source", async () => {
    mockAuthenticatedApi(patientUser, {
      voiceProviderResponse: {
        provider_name: "mock-transcript-fixture",
        model: "precomputed-v1",
        mode: "fixture",
        enabled: true,
        disclosure:
          "Mock transcript fixture - local ASR unavailable in this environment.",
      },
      voiceSamplesResponse: [
        {
          sample_id: "patient-follow-up",
          label: "Synthetic patient follow-up",
          scope: "patient",
          interaction_type: "ai_patient_session_summary",
          duration_ms: 24000,
          audio_url:
            "/patients/patient-a/voice/samples/patient-follow-up/audio",
          provider_disclosure:
            "Mock transcript fixture - local ASR unavailable in this environment.",
        },
      ],
      voiceSessionResponse: {
        id: "voice-session-patient",
        clinic_id: "clinic-a",
        patient_id: "patient-a",
        actor_role: "patient",
        interaction_type: "ai_patient_session_summary",
        sample_id: "patient-follow-up",
        audio_sha256: "b".repeat(64),
        audio_duration_ms: 24000,
        asr_provider: "mock-transcript-fixture",
        asr_model: "precomputed-v1",
        language: "en",
        language_probability: null,
        status: "completed",
        error_code: null,
        entry_id: null,
        highlight_id: null,
        source_segment_id: "voice-segment-patient",
        created_at: "2026-08-27T00:00:00Z",
        completed_at: "2026-08-27T00:00:00Z",
        patient_safe: true,
        segments: [],
      },
    });
    renderApp();
    const panel = await screen.findByTestId("voice-panel");
    expect(panel).toHaveTextContent("patient follow-up");
    expect(panel).not.toHaveTextContent("nurse follow-up");
    expect(
      panel.querySelector("button[aria-label*='microphone' i]"),
    ).toBeNull();
    fireEvent.click(
      within(panel).getByRole("button", {
        name: "Create care-note suggestion",
      }),
    );
    expect(await screen.findByTestId("voice-session-result")).toHaveTextContent(
      "Suggestion status: Ready for review",
    );
    expect(screen.queryByRole("button", { name: "View source" })).toBeNull();
  });

  it("shows a safe audio loading error in English and Chinese", async () => {
    const sample = {
      sample_id: "nurse-follow-up",
      label: "Synthetic nurse follow-up",
      scope: "clinical" as const,
      interaction_type: "ai_nurse_consult_summary",
      duration_ms: 24000,
      audio_url: "/ignored-relative-audio-url",
      provider_disclosure: "internal test disclosure",
    };
    mockAuthenticatedApi(staffUser, {
      voiceProviderResponse: { enabled: true },
      voiceSamplesResponse: [sample],
      voiceAudioStatus: 503,
    });
    renderApp();
    const englishError = await screen.findByTestId("voice-audio-error");
    expect(englishError).toHaveTextContent(
      "This audio sample could not be loaded.",
    );
    expect(englishError).not.toHaveTextContent("503");
    expect(englishError).not.toHaveTextContent("localhost:8000");

    cleanup();
    window.history.replaceState({}, "", "/?lang=zh-CN");
    mockAuthenticatedApi(staffUser, {
      voiceProviderResponse: { enabled: true },
      voiceSamplesResponse: [sample],
      voiceAudioStatus: 503,
    });
    renderApp();
    const chineseError = await screen.findByTestId("voice-audio-error");
    expect(chineseError).toHaveTextContent("这段音频暂时无法加载。");
    expect(chineseError).not.toHaveTextContent("503");
    expect(chineseError).not.toHaveTextContent("localhost:8000");
  });

  it("revokes audio object URLs when switching samples and unmounting", async () => {
    const samples = [
      {
        sample_id: "nurse-follow-up",
        label: "Synthetic nurse follow-up",
        scope: "clinical" as const,
        interaction_type: "ai_nurse_consult_summary",
        duration_ms: 24000,
        audio_url: "/ignored-nurse-audio-url",
        provider_disclosure: "internal test disclosure",
      },
      {
        sample_id: "patient-follow-up",
        label: "Synthetic patient follow-up",
        scope: "patient" as const,
        interaction_type: "ai_patient_session_summary",
        duration_ms: 24000,
        audio_url: "/ignored-patient-audio-url",
        provider_disclosure: "internal test disclosure",
      },
    ];
    mockAuthenticatedApi(staffUser, {
      voiceProviderResponse: { enabled: true },
      voiceSamplesResponse: samples,
    });
    const rendered = renderApp();
    const panel = await screen.findByTestId("voice-panel");
    await waitFor(() => expect(URL.createObjectURL).toHaveBeenCalledTimes(1));
    fireEvent.change(within(panel).getByLabelText("Choose a conversation"), {
      target: { value: "patient-follow-up" },
    });
    await waitFor(() => expect(URL.createObjectURL).toHaveBeenCalledTimes(2));
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:nightingale-test-1");
    rendered.unmount();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:nightingale-test-2");
  });

  it("ignores a stale audio response after switching samples", async () => {
    const samples = [
      {
        sample_id: "nurse-follow-up",
        label: "Synthetic nurse follow-up",
        scope: "clinical" as const,
        interaction_type: "ai_nurse_consult_summary",
        duration_ms: 24000,
        audio_url: "/ignored-nurse-audio-url",
        provider_disclosure: "internal test disclosure",
      },
      {
        sample_id: "patient-follow-up",
        label: "Synthetic patient follow-up",
        scope: "patient" as const,
        interaction_type: "ai_patient_session_summary",
        duration_ms: 24000,
        audio_url: "/ignored-patient-audio-url",
        provider_disclosure: "internal test disclosure",
      },
    ];
    const fetchMock = mockAuthenticatedApi(staffUser, {
      voiceProviderResponse: { enabled: true },
      voiceSamplesResponse: samples,
      voiceAudioDelayMs: 20,
    });
    const rendered = renderApp();
    const panel = await screen.findByTestId("voice-panel");
    fireEvent.change(within(panel).getByLabelText("Choose a conversation"), {
      target: { value: "patient-follow-up" },
    });
    await waitFor(() => expect(URL.createObjectURL).toHaveBeenCalledTimes(1));
    expect(
      fetchMock.mock.calls.filter(([input]) =>
        String(input).includes("/audio"),
      ),
    ).toHaveLength(2);
    expect(screen.getByTestId("voice-audio")).toHaveAttribute(
      "src",
      "blob:nightingale-test-1",
    );
    rendered.unmount();
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
      await screen.findByRole("region", { name: "原始来源" }),
    ).toBeInTheDocument();
    expect(screen.getByText("原始来源片段")).toBeInTheDocument();
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
      "We couldn't sign you in. Check your details and try again.",
    );
  });

  it("loads Glance with six items, AI labels, and role-aware controls", async () => {
    mockAuthenticatedApi();
    renderApp();
    expect(
      await screen.findByText(/6 items need attention/),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Nurse consultation").length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: "Open source" })).toHaveLength(
      6,
    );
    expect(screen.getAllByRole("button", { name: "Comments" }).length).toBe(2);
  });

  it("renders a protected conflict card without generic review controls", async () => {
    mockAuthenticatedApi(staffUser, {
      glanceResponse: protectedGlanceResponse,
      clinicalConflictResponse: clinicalConflict,
      feedbackResponse: {
        applied_to_profile: false,
        suppression_reason: "protected_safety_class",
      },
      assertionSources: {
        [positiveAssertion.id]: assertionSource(
          positiveAssertion,
          "Pending renal panel requires coordination.",
          "staff_note",
          "staff",
        ),
        [negativeAssertion.id]: assertionSource(
          negativeAssertion,
          "no known allergies noted.",
          "ai_patient_session_summary",
          "system",
        ),
      },
    });
    renderApp();
    await screen.findByText("Conflicting allergy information");
    const card = getProtectedCard();
    expect(card).toHaveTextContent("Conflicting allergy information");
    expect(card).toHaveTextContent("Protected attention");
    expect(card).toHaveTextContent("Needs clinician review");
    expect(within(card).queryByRole("button", { name: "Accept" })).toBeNull();
    expect(within(card).queryByRole("button", { name: "Reject" })).toBeNull();
    fireEvent.click(within(card).getByTestId("ranking-details"));
    expect(card).toHaveTextContent("Before minimum");
    expect(card).toHaveTextContent("Minimum display priority");
    expect(card).toHaveTextContent("Minimum applied");
    expect(card).toHaveTextContent(
      "This unresolved allergy conflict has a deterministic minimum display priority.",
    );

    fireEvent.click(within(card).getByRole("button", { name: "Pin" }));
    expect(
      await screen.findByTestId("protected-feedback-notice"),
    ).toHaveTextContent(
      "This protected safety item does not train preference ranking while unresolved.",
    );
    fireEvent.click(
      within(card).getByRole("button", { name: "Review conflict" }),
    );
    const drawer = await screen.findByTestId("clinical-conflict-drawer");
    expect(drawer).toHaveTextContent("Allergy conflict review");
    expect(drawer).toHaveTextContent("Allergy reported");
    expect(drawer).toHaveTextContent("Allergy denied");
    expect(drawer).toHaveTextContent(
      "It has not decided which one is clinically correct.",
    );
    expect(drawer).toHaveTextContent(
      "Read-only for Staff. A clinician must record the clinical decision.",
    );
    expect(
      within(drawer).queryByRole("button", {
        name: "Record clinical decision",
      }),
    ).toBeNull();

    const reported = within(drawer).getByTestId("clinical-assertion-present");
    await fireEvent.click(
      within(reported).getByRole("button", { name: /View source/ }),
    );
    expect(
      await screen.findByRole("region", { name: "Original source" }),
    ).toBeVisible();
    const sourcePanel = screen.getByRole("region", { name: "Original source" });
    expect(within(sourcePanel).getByTestId("source-quote")).toHaveTextContent(
      "Pending renal panel",
    );
    const denied = within(drawer).getByTestId("clinical-assertion-absent");
    await fireEvent.click(
      within(denied).getByRole("button", { name: /View source/ }),
    );
    await waitFor(() =>
      expect(within(sourcePanel).getByTestId("source-quote")).toHaveTextContent(
        "no known allergies",
      ),
    );
    fireEvent.click(screen.getByRole("button", { name: "Close source" }));
    fireEvent.click(
      screen.getByRole("button", { name: "Close conflict review" }),
    );
  });

  it("lets a clinician record a cautious conflict decision", async () => {
    const fetchMock = mockAuthenticatedApi(clinicianUser, {
      glanceResponse: protectedGlanceResponse,
      clinicalConflictResponse: clinicalConflict,
      adjudicationResponse: needsMoreConflict,
      assertionSources: {
        [positiveAssertion.id]: assertionSource(
          positiveAssertion,
          "Pending renal panel requires coordination.",
          "staff_note",
          "staff",
        ),
        [negativeAssertion.id]: assertionSource(
          negativeAssertion,
          "no known allergies noted.",
          "ai_patient_session_summary",
          "system",
        ),
      },
    });
    renderApp();
    await screen.findByText("Conflicting allergy information");
    const card = getProtectedCard();
    fireEvent.click(
      within(card).getByRole("button", { name: "Review conflict" }),
    );
    const drawer = await screen.findByTestId("clinical-conflict-drawer");
    const decision = await within(drawer).findByLabelText("Clinical decision");
    expect(decision).toHaveValue("needs_more_information");
    fireEvent.change(decision, { target: { value: "needs_more_information" } });
    fireEvent.click(
      within(drawer).getByRole("button", { name: "Record clinical decision" }),
    );
    await waitFor(() => expect(drawer).toHaveTextContent("Decision recorded."));
    const adjudicationCall = fetchMock.mock.calls.find(
      ([input, init]) =>
        String(input).includes("/clinical-conflicts/") &&
        String(input).endsWith("/adjudicate") &&
        init?.method === "PATCH",
    );
    expect(adjudicationCall).toBeDefined();
    expect(JSON.parse(String(adjudicationCall?.[1]?.body))).toEqual({
      expected_version: 1,
      resolution: "needs_more_information",
    });
    expect(drawer).toHaveTextContent("Review version 2");
  });

  it("keeps the conflict drawer open and refreshes after an adjudication 409", async () => {
    mockAuthenticatedApi(clinicianUser, {
      glanceResponse: protectedGlanceResponse,
      clinicalConflictResponse: clinicalConflict,
      latestClinicalConflictResponse: needsMoreConflict,
      adjudicationStatus: 409,
      assertionSources: {
        [positiveAssertion.id]: assertionSource(
          positiveAssertion,
          "Pending renal panel requires coordination.",
          "staff_note",
          "staff",
        ),
        [negativeAssertion.id]: assertionSource(
          negativeAssertion,
          "no known allergies noted.",
          "ai_patient_session_summary",
          "system",
        ),
      },
    });
    renderApp();
    await screen.findByText("Conflicting allergy information");
    const card = getProtectedCard();
    fireEvent.click(
      within(card).getByRole("button", { name: "Review conflict" }),
    );
    const drawer = await screen.findByTestId("clinical-conflict-drawer");
    fireEvent.change(
      await within(drawer).findByLabelText("Clinical decision"),
      {
        target: { value: "confirmed_absent" },
      },
    );
    fireEvent.click(
      within(drawer).getByRole("button", { name: "Record clinical decision" }),
    );
    expect(
      await within(drawer).findByTestId("clinical-conflict-stale"),
    ).toHaveTextContent("This conflict was updated by another clinician.");
    expect(drawer).toHaveTextContent("Review version 2");
    expect(within(drawer).getByLabelText("Clinical decision")).toHaveValue(
      "needs_more_information",
    );
  });

  it("records one metadata-only Glance impression after render", async () => {
    const fetchMock = mockAuthenticatedApi();
    renderApp();
    await screen.findByText(/6 items need attention/);
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(
          ([input, init]) =>
            String(input).endsWith("/glance-impressions") &&
            init?.method === "POST",
        ),
      ).toHaveLength(1),
    );
    const impressionCall = fetchMock.mock.calls.find(
      ([input, init]) =>
        String(input).endsWith("/glance-impressions") &&
        init?.method === "POST",
    );
    const body = JSON.parse(String(impressionCall?.[1]?.body));
    expect(body.requested_limit).toBe(6);
    expect(body.surfaced_items).toHaveLength(6);
    expect(JSON.stringify(body)).not.toContain("Pending renal panel");
    expect(JSON.stringify(body)).not.toContain("risk_reason");
    expect(JSON.stringify(body)).not.toContain("quote");
  });

  it("does not duplicate an impression for an unchanged SSE refresh", async () => {
    const eventSource = installFakeEventSource();
    const fetchMock = mockAuthenticatedApi();
    renderApp();
    await screen.findByText(/6 items need attention/);
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(
          ([input, init]) =>
            String(input).endsWith("/glance-impressions") &&
            init?.method === "POST",
        ),
      ).toHaveLength(1),
    );
    eventSource.emit("entry");
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(([input]) =>
          String(input).endsWith("/timeline"),
        ).length,
      ).toBeGreaterThan(1),
    );
    await new Promise((resolve) => window.setTimeout(resolve, 20));
    expect(
      fetchMock.mock.calls.filter(
        ([input, init]) =>
          String(input).endsWith("/glance-impressions") &&
          init?.method === "POST",
      ),
    ).toHaveLength(1);
  });

  it("keeps Glance usable when impression telemetry fails", async () => {
    mockAuthenticatedApi(staffUser, { impressionStatus: 503 });
    renderApp();
    expect(await screen.findByTestId("top-card")).toBeVisible();
    await screen.findByText(/6 items need attention/);
    expect(screen.getByText(/6 items need attention/)).toBeVisible();
  });

  it("keeps History rows on aligned columns and labels the current row", async () => {
    const versions: Version[] = [
      {
        id: "version-staff-1",
        entry_id: "entry-staff",
        version_number: 1,
        content: "Original staff note.",
        created_by_user_id: "staff-user",
        created_by_role: "staff",
        base_version: 0,
        reverted_from_version: null,
        created_at: "2026-08-24T08:00:00Z",
      },
      {
        id: "version-staff-2",
        entry_id: "entry-staff",
        version_number: 2,
        content: "Pending renal panel requires coordination.",
        created_by_user_id: "staff-user",
        created_by_role: "staff",
        base_version: 1,
        reverted_from_version: null,
        created_at: "2026-08-25T08:00:00Z",
      },
    ];
    mockAuthenticatedApi(staffUser, { versionsResponse: versions });
    renderApp();
    const staffCard = await screen.findByTestId("timeline-entry-entry-staff");
    fireEvent.click(within(staffCard).getByRole("button", { name: "History" }));
    const history = await within(staffCard).findByRole("region", {
      name: "History",
    });
    const rows = within(history).getAllByTestId(/^history-row-/);
    expect(rows).toHaveLength(2);
    for (const row of rows) {
      expect(row.className).toContain(
        "sm:grid-cols-[minmax(0,1fr)_minmax(10rem,auto)_9rem]",
      );
    }
    const previousRow = within(history).getByTestId("history-row-1");
    expect(
      within(previousRow).getByRole("button", { name: "Compare" }),
    ).toBeInTheDocument();
    expect(
      within(previousRow).getByRole("button", { name: "Revert" }),
    ).toBeInTheDocument();
    const currentRow = within(history).getByTestId("history-row-2");
    expect(currentRow).toHaveAttribute("data-current", "true");
    expect(
      within(currentRow).getByTestId("history-current-row-label"),
    ).toHaveTextContent("Current");
    expect(within(currentRow).queryAllByRole("button")).toHaveLength(0);
  });

  it("keeps implementation language out of the primary product surfaces", async () => {
    mockAuthenticatedApi();
    renderApp();
    await screen.findByText(/6 items need attention/);
    const top = await screen.findByTestId("top-card");
    expect(top).toHaveTextContent("6 items need attention");
    expect(top).toHaveTextContent("Priority 100");
    expect(top).not.toHaveTextContent("P100");
    expect(top).not.toHaveTextContent("source-linked");
    expect(top).not.toHaveTextContent("No explicit risk tag");
    expect(top).not.toHaveTextContent("No action label");

    const aiPanel = screen.getByTestId("ai-scribe-panel");
    expect(aiPanel).toHaveTextContent("AI-assisted note");
    expect(aiPanel).not.toHaveTextContent("Active provider");
    expect(aiPanel).not.toHaveTextContent("fixture-redacted-v1");
    expect(aiPanel).not.toHaveTextContent("deterministic-local");

    const historical = screen.getByTestId("historical-context");
    expect(historical).toHaveTextContent(
      "Recent context, earlier context, and historical summaries",
    );
    expect(historical).not.toHaveTextContent("Hot context");
    expect(historical).not.toHaveTextContent("Warm index");
    expect(historical).not.toHaveTextContent("policy gate-d-v1");

    fireEvent.click(
      (await screen.findAllByRole("button", { name: "Open source" }))[0],
    );
    const source = await screen.findByRole("region", {
      name: "Original source",
    });
    const technicalDetails = screen.getByTestId("source-technical-details");
    expect(technicalDetails).not.toHaveAttribute("open");
    expect(screen.getByText("Python code point")).not.toBeVisible();
    expect(
      screen.getByText(/SHA-256 is stored with the highlight\./),
    ).not.toBeVisible();
    fireEvent.click(within(technicalDetails).getByText("Technical details"));
    expect(technicalDetails).toHaveAttribute("open");
    expect(source).toHaveTextContent("Exact span:");
  });

  it("shows bounded ranking contributions and sends pin feedback", async () => {
    mockAuthenticatedApi();
    renderApp();
    const details = (await screen.findAllByTestId("ranking-details"))[0];
    fireEvent.click(details);
    expect(
      (
        await screen.findAllByText(
          "Priority helps organise the view. It is not a medical risk score.",
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
      expect(screen.getByText("No discussion yet.")).toBeVisible(),
    );
    fireEvent.keyDown(document, { key: "Escape" });
    await waitFor(() => expect(document.activeElement).toBe(commentsButton));

    mockAuthenticatedApi(staffUser, { commentsStatus: 500 });
    fireEvent.click(commentsButton);
    expect(screen.getByTestId("comments-drawer")).toBeVisible();
    expect(await screen.findByTestId("comments-error")).toHaveTextContent(
      "We couldn't complete that action. Your existing record was not changed.",
    );
  });

  it("keeps Comments open across refreshes without reconnecting SSE", async () => {
    const eventSource = installFakeEventSource();
    const fetchMock = mockAuthenticatedApi(staffUser, {
      commentsDelayMs: 40,
    });
    renderApp();
    const commentsButton = (
      await screen.findAllByRole("button", { name: "Comments" })
    )[0];
    fireEvent.click(commentsButton);
    const drawer = screen.getByTestId("comments-drawer");
    const body = await screen.findByLabelText("Comment body");
    body.focus();
    expect(eventSource.count()).toBe(1);

    eventSource.emit("entry");
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(([input]) =>
          String(input).endsWith("/timeline"),
        ).length,
      ).toBeGreaterThan(1),
    );
    expect(drawer).toBeVisible();
    expect(document.activeElement).toBe(body);
    await new Promise((resolve) => window.setTimeout(resolve, 3200));
    expect(drawer).toBeVisible();
    expect(eventSource.count()).toBe(1);

    fireEvent.keyDown(document, { key: "Escape" });
    await waitFor(() =>
      expect(screen.queryByTestId("comments-drawer")).toBeNull(),
    );
    const editButton = screen.getAllByRole("button", { name: "Edit" })[0];
    fireEvent.click(editButton);
    expect(eventSource.count()).toBe(1);
  });

  it("closes Comments when the patient scope changes", async () => {
    mockAuthenticatedApi(staffUser, {
      patients: [
        patient,
        {
          ...patient,
          id: "patient-b",
          synthetic_display_name: "Jordan Lim",
        },
      ],
    });
    renderApp();
    const commentsButton = (
      await screen.findAllByRole("button", { name: "Comments" })
    )[0];
    fireEvent.click(commentsButton);
    expect(screen.getByTestId("comments-drawer")).toBeVisible();
    fireEvent.change(screen.getByLabelText("Select patient"), {
      target: { value: "patient-b" },
    });
    await waitFor(() =>
      expect(screen.queryByTestId("comments-drawer")).not.toBeInTheDocument(),
    );
  });

  it("closes a Comments drawer safely when refresh removes its entry", async () => {
    const eventSource = installFakeEventSource();
    mockAuthenticatedApi(staffUser, { timelineAfterRefresh: [] });
    renderApp();
    const commentsButton = (
      await screen.findAllByRole("button", { name: "Comments" })
    )[0];
    fireEvent.click(commentsButton);
    expect(screen.getByTestId("comments-drawer")).toBeVisible();
    eventSource.emit("entry");
    await waitFor(() =>
      expect(screen.queryByTestId("comments-drawer")).not.toBeInTheDocument(),
    );
    expect(screen.getByRole("alert")).toHaveTextContent(
      "This record changed and the discussion was closed safely.",
    );
  });

  it("preserves source and task drawers during a background refresh", async () => {
    const eventSource = installFakeEventSource();
    const fetchMock = mockAuthenticatedApi(staffUser, { endOffset: 19 });
    renderApp();
    const sourceButton = (
      await screen.findAllByRole("button", {
        name: "Open source",
      })
    )[0];
    fireEvent.click(sourceButton);
    expect(
      await screen.findByRole("region", { name: "Original source" }),
    ).toBeInTheDocument();
    eventSource.emit("entry");
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(([input]) =>
          String(input).endsWith("/timeline"),
        ).length,
      ).toBeGreaterThan(1),
    );
    expect(
      screen.getByRole("region", { name: "Original source" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Close source" }));
    const assignButton = (
      await screen.findAllByRole("button", { name: "Assign task" })
    )[0];
    fireEvent.click(assignButton);
    expect(screen.getByTestId("task-drawer")).toBeVisible();
    eventSource.emit("entry");
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(([input]) =>
          String(input).endsWith("/timeline"),
        ).length,
      ).toBeGreaterThan(2),
    );
    expect(screen.getByTestId("task-drawer")).toBeVisible();
  });

  it("closes Comments from a deliberate backdrop interaction", async () => {
    mockAuthenticatedApi();
    renderApp();
    const commentsButton = (
      await screen.findAllByRole("button", { name: "Comments" })
    )[0];
    fireEvent.click(commentsButton);
    const backdrop = screen.getByTestId("comments-drawer-backdrop");
    fireEvent.mouseDown(backdrop);
    await waitFor(() =>
      expect(screen.queryByTestId("comments-drawer")).not.toBeInTheDocument(),
    );
  });

  it("replaces the selected entry without flashing the Comments drawer closed", async () => {
    mockAuthenticatedApi();
    renderApp();
    const commentButtons = await screen.findAllByRole("button", {
      name: "Comments",
    });
    fireEvent.click(commentButtons[0]);
    expect(screen.getByTestId("comments-drawer")).toBeVisible();
    fireEvent.click(commentButtons[1]);
    expect(screen.getByTestId("comments-drawer")).toBeVisible();
    expect(screen.getByTestId("comments-panel")).toHaveAttribute(
      "data-entry-id",
      "entry-ai",
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
      "Historical summary · not the original record",
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
      screen.getByRole("region", { name: "Original source" }),
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
      screen.queryByRole("region", { name: "Original source" }),
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
    expect(await screen.findByText("Original source")).toBeInTheDocument();
    const sourcePanel = screen.getByRole("region", { name: "Original source" });
    fireEvent.click(within(sourcePanel).getByText("Technical details"));
    expect(within(sourcePanel).getByText(/Exact span/)).toBeInTheDocument();
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
    expect(await screen.findByText("Your care summary")).toBeInTheDocument();
    expect(
      screen.queryByText("Top Card · Glance View"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Comments" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByTestId("ai-scribe-panel")).not.toBeInTheDocument();
  });
});
