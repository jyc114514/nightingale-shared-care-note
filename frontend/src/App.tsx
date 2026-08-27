import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent as ReactKeyboardEvent,
  type Ref,
  type RefObject,
  type ReactNode,
} from "react";

import { ApiError, api } from "./api";
import { I18nProvider, LanguageToggle, useI18n } from "./i18n";
import type { Locale, Translate, TranslationKey } from "./i18n/types";
import type {
  Comment,
  PatientContext,
  Conflict,
  Diff,
  FeedbackEventType,
  GlanceItem,
  AIJob,
  AIProviderInfo,
  Me,
  MentionUser,
  Patient,
  ProvenanceSource,
  Task,
  TaskStatus,
  TimelineEntry,
  TranscriptSegment,
  VoiceProviderInfo,
  VoiceSample,
  VoiceSession,
  Version,
} from "./types";

const sourceKindKeys: Record<string, TranslationKey> = {
  doctor_consult: "sourceKind.doctor",
  nurse_consult: "sourceKind.nurse",
  patient_ai_session: "sourceKind.patient",
  system_event: "sourceKind.system",
  manual: "sourceKind.manual",
  voice_patient: "sourceKind.voicePatient",
  voice_clinical: "sourceKind.voiceClinical",
};

const sourceLabelKeys: Record<string, TranslationKey> = {
  "AI-scribed · Doctor consult": "sourceKind.doctor",
  "AI-scribed · Nurse consult": "sourceKind.nurse",
  "AI-scribed · Patient session": "sourceKind.patient",
  "AI-scribed - Doctor consult": "sourceKind.doctor",
  "AI-scribed - Nurse consult": "sourceKind.nurse",
  "AI-scribed - Patient session": "sourceKind.patient",
  "System event": "sourceKind.system",
  "Manual note": "sourceKind.manual",
  "Assigned task": "sourceKind.task",
  "Synthetic patient audio": "sourceKind.voicePatient",
  "Synthetic clinical audio": "sourceKind.voiceClinical",
};

const entryTypeKeys: Record<string, TranslationKey> = {
  patient_facing_summary: "entryType.patientSummary",
  patient_instruction: "entryType.patientInstruction",
  staff_note: "entryType.staffNote",
  clinician_section: "entryType.clinicianSection",
  ai_doctor_consult_summary: "entryType.doctorSummary",
  ai_nurse_consult_summary: "entryType.nurseSummary",
  ai_patient_session_summary: "entryType.patientSession",
  system_event: "entryType.systemEvent",
};

const statusKeys: Record<string, TranslationKey> = {
  suggested: "status.suggested",
  accepted: "status.accepted",
  rejected: "status.rejected",
  superseded: "status.superseded",
  conflict_review: "status.conflictReview",
};

const itemKindKeys: Record<string, TranslationKey> = {
  information: "itemKind.information",
  action: "itemKind.action",
  flag: "itemKind.flag",
};

const actionStateKeys: Record<string, TranslationKey> = {
  open: "actionState.open",
  completed: "actionState.completed",
  not_applicable: "actionState.notApplicable",
  in_progress: "task.status.inProgress",
};

const roleKeys: Record<string, TranslationKey> = {
  patient: "role.patient",
  staff: "role.staff",
  clinician: "role.clinician",
  admin: "role.admin",
  system: "sourceKind.system",
};

const taskStatusKeys: Record<TaskStatus, TranslationKey> = {
  open: "task.status.open",
  in_progress: "task.status.inProgress",
  done: "task.status.done",
};

const realtimeStatusKeys: Record<
  "connecting" | "connected" | "reconnecting" | "unavailable",
  TranslationKey
> = {
  connecting: "realtime.connecting",
  connected: "realtime.connected",
  reconnecting: "realtime.reconnecting",
  unavailable: "realtime.unavailable",
};

function formatDate(value: string, locale: Locale = "en") {
  return new Intl.DateTimeFormat(locale === "zh-CN" ? "zh-CN" : "en-SG", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function scrollToElement(element: HTMLElement | null) {
  if (!element || typeof element.scrollIntoView !== "function") return;
  const reducedMotion = window.matchMedia?.(
    "(prefers-reduced-motion: reduce)",
  ).matches;
  element.scrollIntoView({
    behavior: reducedMotion ? "auto" : "smooth",
    block: "center",
  });
}

function displayError(error: unknown, t: Translate) {
  if (error instanceof ApiError) {
    if (
      typeof error.body.detail === "object" &&
      error.body.detail?.actual_version
    ) {
      return t("error.versionConflict", {
        message: error.message,
        version: error.body.detail.actual_version,
      });
    }
    return error.message;
  }
  return error instanceof Error ? error.message : t("error.request");
}

function isInternalUser(user: Me) {
  return user.memberships.length > 0;
}

function primaryRole(user: Me) {
  return user.memberships[0]?.role ?? "patient";
}

function canEditEntry(user: Me, entry: TimelineEntry) {
  return user.memberships.some(
    (membership) =>
      (membership.role === "staff" && entry.entry_type === "staff_note") ||
      (membership.role === "clinician" &&
        entry.entry_type === "clinician_section"),
  );
}

type ExactSpanResult =
  | { valid: true; before: string; quote: string; after: string }
  | { valid: false; reason: string };

export function exactCodepointSpan(
  text: string,
  quote: string,
  startOffset: number,
  endOffset: number,
): ExactSpanResult {
  const codepoints = Array.from(text);
  if (
    !Number.isInteger(startOffset) ||
    !Number.isInteger(endOffset) ||
    startOffset < 0 ||
    endOffset <= startOffset ||
    endOffset > codepoints.length
  ) {
    return { valid: false, reason: "Offsets are outside the immutable text." };
  }
  const selected = codepoints.slice(startOffset, endOffset).join("");
  if (selected !== quote) {
    return {
      valid: false,
      reason: "The immutable codepoint slice does not match the stored quote.",
    };
  }
  return {
    valid: true,
    before: codepoints.slice(0, startOffset).join(""),
    quote: selected,
    after: codepoints.slice(endOffset).join(""),
  };
}

function ExactSpanView({
  text,
  quote,
  startOffset,
  endOffset,
}: {
  text: string;
  quote: string;
  startOffset: number;
  endOffset: number;
}) {
  const { t } = useI18n();
  const result = exactCodepointSpan(text, quote, startOffset, endOffset);
  if (!result.valid) {
    return (
      <div>
        <p
          className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs leading-5 text-rose-800"
          role="alert"
          data-testid="provenance-integrity-warning"
        >
          {t("source.integrity", { reason: result.reason })}{" "}
          {t("source.noApprox")}
        </p>
        <p className="mt-3 whitespace-pre-wrap">{text}</p>
      </div>
    );
  }
  return (
    <>
      {result.before}
      <mark
        className="rounded bg-amber-100 text-amber-950 underline decoration-amber-500 decoration-2 underline-offset-2"
        data-testid="source-quote"
      >
        {result.quote}
      </mark>
      {result.after}
    </>
  );
}

function Pill({
  children,
  tone = "slate",
}: {
  children: ReactNode;
  tone?: string;
}) {
  const tones: Record<string, string> = {
    slate: "border-slate-200 bg-slate-50 text-slate-600",
    blue: "border-blue-200 bg-blue-50 text-blue-700",
    amber: "border-amber-200 bg-amber-50 text-amber-800",
    green: "border-emerald-200 bg-emerald-50 text-emerald-700",
    red: "border-rose-200 bg-rose-50 text-rose-700",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${tones[tone] ?? tones.slate}`}
    >
      {children}
    </span>
  );
}

function Button({
  children,
  onClick,
  disabled = false,
  kind = "secondary",
  type = "button",
  ariaLabel,
  ariaExpanded,
  ariaControls,
  buttonRef,
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  kind?: "primary" | "secondary" | "quiet" | "danger";
  type?: "button" | "submit";
  ariaLabel?: string;
  ariaExpanded?: boolean;
  ariaControls?: string;
  buttonRef?: Ref<HTMLButtonElement>;
}) {
  const styles = {
    primary: "border-blue-700 bg-blue-700 text-white hover:bg-blue-800",
    secondary:
      "border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:text-blue-700",
    quiet:
      "border-transparent bg-transparent text-slate-500 hover:bg-slate-100 hover:text-slate-800",
    danger: "border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100",
  };
  return (
    <button
      type={type}
      ref={buttonRef}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      className={`min-h-11 rounded-lg border px-3 py-2 text-sm font-semibold transition focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-200 disabled:cursor-not-allowed disabled:opacity-50 ${styles[kind]}`}
    >
      {children}
    </button>
  );
}

function ContextualDrawer({
  open,
  title,
  closeLabel,
  onClose,
  initialFocusRef,
  children,
  testId,
}: {
  open: boolean;
  title: string;
  closeLabel: string;
  onClose: () => void;
  initialFocusRef?: Ref<HTMLElement>;
  children: ReactNode;
  testId: string;
}) {
  const panelRef = useRef<HTMLElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const explicitCloseRef = useRef(false);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;
  const requestClose = () => {
    explicitCloseRef.current = true;
    onCloseRef.current();
  };

  useEffect(() => {
    if (!open) return;
    explicitCloseRef.current = false;
    previousFocusRef.current = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusTimer = window.setTimeout(() => {
      const focusTarget =
        (initialFocusRef as RefObject<HTMLElement>)?.current ??
        closeButtonRef.current;
      focusTarget?.focus();
    }, 0);
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        requestClose();
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) return;
      const focusable = Array.from(
        panelRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((element) => !element.hasAttribute("disabled"));
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
      if (explicitCloseRef.current) previousFocusRef.current?.focus();
      previousFocusRef.current = null;
    };
  }, [initialFocusRef, open]);

  if (!open) return null;
  const titleId = `${testId}-title`;
  return (
    <div
      className="fixed inset-0 z-40 bg-slate-950/35"
      data-testid={`${testId}-backdrop`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) requestClose();
      }}
    >
      <section
        ref={panelRef}
        id={testId}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        data-testid={testId}
        className="ml-auto flex h-full w-full max-w-xl flex-col border-l border-slate-200 bg-white shadow-2xl"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4 sm:px-7">
          <h2 id={titleId} className="text-lg font-semibold text-slate-900">
            {title}
          </h2>
          <Button
            kind="quiet"
            buttonRef={closeButtonRef}
            onClick={requestClose}
            ariaLabel={closeLabel}
          >
            {closeLabel}
          </Button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto p-5 sm:p-7">
          {children}
        </div>
      </section>
    </div>
  );
}

type PreviewMode = "auto" | "desktop" | "mobile";

const previewDimensions = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
} as const;

function DemoPreview() {
  const { t } = useI18n();
  const [mode, setMode] = useState<PreviewMode>("auto");
  const [scale, setScale] = useState(1);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const dimensions = mode === "auto" ? null : previewDimensions[mode];
  useEffect(() => {
    if (!dimensions) return;
    const updateScale = () => {
      const availableWidth = Math.max(320, window.innerWidth - 48);
      const availableHeight = Math.max(320, window.innerHeight - 220);
      setScale(
        Math.min(
          1,
          availableWidth / dimensions.width,
          availableHeight / dimensions.height,
        ),
      );
    };
    updateScale();
    window.addEventListener("resize", updateScale);
    return () => window.removeEventListener("resize", updateScale);
  }, [dimensions]);

  useEffect(() => {
    if (!dimensions) return;
    previousFocusRef.current = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusTimer = window.setTimeout(
      () => closeButtonRef.current?.focus(),
      0,
    );
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setMode("auto");
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
      previousFocusRef.current?.focus();
    };
  }, [dimensions]);

  const previewUrl = useMemo(() => {
    if (!dimensions || mode === "auto") return "";
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set("preview", mode);
    nextUrl.searchParams.set("embedded", "1");
    return nextUrl.toString();
  }, [dimensions, mode]);

  return (
    <>
      <label className="inline-flex items-center rounded-lg border border-slate-200 bg-white px-2 shadow-sm">
        <span className="sr-only">{t("preview.label")}</span>
        <select
          aria-label={t("preview.label")}
          data-testid="demo-preview-select"
          value={mode}
          onChange={(event) => setMode(event.target.value as PreviewMode)}
          className="min-h-11 bg-transparent px-1 text-xs font-semibold text-slate-700 outline-none focus:ring-4 focus:ring-blue-200"
        >
          <option value="auto">{t("preview.auto")}</option>
          <option value="desktop">{t("preview.desktop")}</option>
          <option value="mobile">{t("preview.mobile")}</option>
        </select>
      </label>
      {dimensions && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
          data-testid="demo-preview"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setMode("auto");
          }}
        >
          <section
            className="flex max-h-[calc(100vh-2rem)] w-full max-w-[min(1500px,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-labelledby="demo-preview-title"
          >
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 px-5 py-4 sm:px-7">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">
                  {t("preview.label")}
                </p>
                <h2
                  id="demo-preview-title"
                  className="mt-1 text-lg font-semibold"
                >
                  {t("preview.title")}
                </h2>
                <p
                  className="mt-1 text-sm font-semibold text-slate-600"
                  data-testid="preview-dimensions"
                >
                  {t("preview.dimensions", dimensions)}
                </p>
              </div>
              <Button
                kind="quiet"
                buttonRef={closeButtonRef}
                onClick={() => setMode("auto")}
                ariaLabel={t("preview.close")}
              >
                {t("preview.close")}
              </Button>
            </div>
            <div className="min-h-0 flex-1 overflow-auto bg-slate-100 p-4 sm:p-6">
              <div
                className="mx-auto shadow-xl"
                data-testid="preview-frame-shell"
                style={{
                  width: dimensions.width * scale,
                  height: dimensions.height * scale,
                }}
              >
                <iframe
                  title={
                    mode === "mobile"
                      ? t("preview.frameMobile")
                      : t("preview.frameDesktop")
                  }
                  data-testid="demo-preview-iframe"
                  src={previewUrl}
                  width={dimensions.width}
                  height={dimensions.height}
                  style={{
                    display: "block",
                    width: dimensions.width,
                    height: dimensions.height,
                    transform: `scale(${scale})`,
                    transformOrigin: "top left",
                  }}
                />
              </div>
            </div>
            <p className="border-t border-slate-200 px-5 py-3 text-xs leading-5 text-slate-500 sm:px-7">
              {t("preview.disclaimer")}
            </p>
          </section>
        </div>
      )}
    </>
  );
}

function LearningGuide({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { t } = useI18n();
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    if (!open) return;
    previousFocusRef.current = document.activeElement as HTMLElement | null;
    window.setTimeout(() => closeButtonRef.current?.focus(), 0);
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onCloseRef.current();
        return;
      }
      if (event.key !== "Tab") return;
      const dialog = document.querySelector<HTMLElement>('[role="dialog"]');
      if (!dialog) return;
      const focusable = Array.from(
        dialog.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((element) => !element.hasAttribute("disabled"));
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      previousFocusRef.current?.focus();
    };
  }, [open]);

  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/40 px-4 py-8"
      data-testid="learning-guide-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        className="mx-auto max-w-3xl rounded-3xl border border-slate-200 bg-white p-5 shadow-2xl sm:p-7"
        role="dialog"
        aria-modal="true"
        aria-labelledby="learning-guide-title"
        data-testid="learning-guide"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
              {t("brand.gate")}
            </p>
            <h2
              id="learning-guide-title"
              className="mt-2 text-2xl font-semibold"
            >
              {t("guide.title")}
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              {t("guide.intro")}
            </p>
          </div>
          <Button
            kind="quiet"
            onClick={() => onCloseRef.current()}
            ariaLabel={t("guide.close")}
            buttonRef={closeButtonRef}
          >
            {t("guide.close")}
          </Button>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <article className="rounded-2xl border border-blue-100 bg-blue-50 p-4 sm:col-span-2">
            <h3 className="font-semibold text-slate-900">
              {t("guide.product.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.product.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.roles.title")}
            </h3>
            <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-700">
              <li>{t("guide.roles.staff")}</li>
              <li>{t("guide.roles.clinician")}</li>
              <li>{t("guide.roles.patient")}</li>
              <li>{t("guide.roles.system")}</li>
            </ul>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.top.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.top.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.status.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.status.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.provenance.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.provenance.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.collaboration.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.collaboration.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-amber-100 bg-amber-50 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.ai.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.ai.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.context.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.context.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.checklist.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.checklist.body")}
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-900">
              {t("guide.ux.title")}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {t("guide.ux.body")}
            </p>
          </article>
        </div>
        <p className="mt-5 text-xs leading-5 text-slate-500">
          {t("guide.sourceNotice")}
        </p>
      </section>
    </div>
  );
}

function LoginScreen({
  onLogin,
  initialError,
}: {
  onLogin: (user: Me) => void;
  initialError?: string | null;
}) {
  const { t } = useI18n();
  const [email, setEmail] = useState("staff.a@clinic-a.test");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(initialError ?? null);
  const [guideOpen, setGuideOpen] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await api.login(email, password);
      onLogin(result.user);
    } catch (requestError) {
      setError(displayError(requestError, t));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f4f7fb] px-5 py-10 text-slate-900">
      <section className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.28em] text-blue-700">
              {t("login.eyebrow")}
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight">
              {t("login.title")}
            </h1>
          </div>
          <div className="flex flex-col items-end gap-2">
            <LanguageToggle />
            <Button kind="quiet" onClick={() => setGuideOpen(true)}>
              {t("login.guide")}
            </Button>
          </div>
        </div>
        <p className="-mt-4 mb-8 text-sm leading-6 text-slate-500">
          {t("login.description")}
        </p>
        <form className="space-y-4" onSubmit={submit}>
          <label className="block text-sm font-semibold text-slate-700">
            {t("login.email")}
            <input
              aria-label={t("login.email")}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 font-normal outline-none ring-blue-200 transition focus:border-blue-500 focus:ring-4"
              type="email"
              autoComplete="username"
              required
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            {t("login.password")}
            <input
              aria-label={t("login.password")}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 font-normal outline-none ring-blue-200 transition focus:border-blue-500 focus:ring-4"
              type="password"
              autoComplete="current-password"
              required
            />
          </label>
          {error && (
            <p
              className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700"
              role="alert"
            >
              {error}
            </p>
          )}
          <Button type="submit" kind="primary" disabled={busy}>
            {busy ? t("login.signingIn") : t("login.signIn")}
          </Button>
        </form>
        <div className="mt-8 border-t border-slate-100 pt-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
            {t("login.personasTitle")}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              ["staff.a@clinic-a.test", t("login.persona.staff")],
              ["clinician.a@clinic-a.test", t("login.persona.clinician")],
              ["sarah.patient@clinic-a.test", t("login.persona.patient")],
            ].map(([personaEmail, label]) => (
              <Button
                key={personaEmail}
                kind="quiet"
                onClick={() => setEmail(personaEmail)}
              >
                {label}
              </Button>
            ))}
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-400">
            {t("login.personaHint")}
          </p>
        </div>
      </section>
      <LearningGuide open={guideOpen} onClose={() => setGuideOpen(false)} />
    </main>
  );
}

function SourcePanel({
  source,
  onClose,
}: {
  source: ProvenanceSource | null;
  onClose: () => void;
}) {
  const { locale, t } = useI18n();
  if (!source) {
    return (
      <section
        className="rounded-2xl border border-slate-200 bg-white p-5"
        aria-label={t("source.navigation")}
      >
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
          {t("source.navigation")}
        </p>
        <h2 className="mt-2 text-lg font-semibold text-slate-800">
          {t("source.chooseTitle")}
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          {t("source.chooseBody")}
        </p>
      </section>
    );
  }
  return (
    <section
      className="rounded-2xl border border-blue-200 bg-blue-50/60 p-5"
      aria-label={t("source.immutable")}
      data-source-entry-id={source.source_entry_id}
      data-source-version-id={source.source_version_id}
      data-source-version={source.version_number}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">
            {t("source.immutable")}
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-900">
            {t(entryTypeKeys[source.entry_type] ?? "entryType.systemEvent")}
          </h2>
        </div>
        <div className="flex items-start gap-2">
          <Pill tone="blue">v{source.version_number}</Pill>
          <Button kind="quiet" onClick={onClose}>
            {t("source.close")}
          </Button>
        </div>
      </div>
      {source.version_number !== source.current_entry_version && (
        <p
          className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-900"
          data-testid="immutable-version-warning"
        >
          {t("source.versionWarning", {
            version: source.version_number,
            current: source.current_entry_version,
          })}
        </p>
      )}
      <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
        <div>
          <dt className="text-slate-500">{t("source.occurred")}</dt>
          <dd className="mt-1 font-semibold text-slate-800">
            {formatDate(source.occurred_at, locale)}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">{t("source.offsetUnit")}</dt>
          <dd className="mt-1 font-semibold text-slate-800">
            {t("source.pythonCodepoint")}
          </dd>
        </div>
        <div className="col-span-2">
          <dt className="text-slate-500">{t("source.reference")}</dt>
          <dd className="mt-1 break-words font-mono text-slate-800">
            {source.source_reference ?? t("source.noReference")}
          </dd>
        </div>
      </dl>
      <blockquote className="mt-4 rounded-xl border border-blue-100 bg-white p-4 text-sm leading-7 text-slate-800">
        <ExactSpanView
          text={source.version_content}
          quote={source.quote}
          startOffset={source.start_offset}
          endOffset={source.end_offset}
        />
      </blockquote>
      <p className="mt-3 text-xs leading-5 text-slate-500">
        {t("source.exactSpan", {
          start: source.start_offset,
          end: source.end_offset,
        })}{" "}
        {t("source.sha")}
      </p>
    </section>
  );
}

function ImmutableTimelineSource({ source }: { source: ProvenanceSource }) {
  const { t } = useI18n();
  return (
    <section
      className="mt-4 rounded-xl border border-amber-200 bg-amber-50/70 p-4"
      aria-label={t("source.timelineAria")}
      data-testid="immutable-timeline-source"
      data-source-entry-id={source.source_entry_id}
      data-source-version={source.version_number}
    >
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-amber-800">
        {t("source.timelineTitle")}
      </p>
      <p className="mt-2 text-xs leading-5 text-amber-900">
        {t("source.anchored", {
          version: source.version_number,
          current: source.current_entry_version,
        })}
      </p>
      <p className="mt-2 text-xs leading-5 text-amber-900">
        {t("source.anchoredExplanation", {
          version: source.version_number,
          current: source.current_entry_version,
        })}
      </p>
      <div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-800">
        <span data-testid="source-rendered-text">
          <ExactSpanView
            text={source.version_content}
            quote={source.quote}
            startOffset={source.start_offset}
            endOffset={source.end_offset}
          />
        </span>
      </div>
    </section>
  );
}

function CommentNode({
  comment,
  childrenByParent,
  depth,
  visited,
  onReply,
  onResolve,
  onAssignTask,
  busy,
}: {
  comment: Comment;
  childrenByParent: Map<string, Comment[]>;
  depth: number;
  visited: Set<string>;
  onReply: (id: string | null) => void;
  onResolve: (comment: Comment) => Promise<void>;
  onAssignTask: (commentId: string) => void;
  busy: boolean;
}) {
  const { locale, t } = useI18n();
  if (visited.has(comment.id)) return null;
  const nextVisited = new Set(visited).add(comment.id);
  const children = childrenByParent.get(comment.id) ?? [];
  return (
    <article
      data-testid={`comment-${comment.id}`}
      className={`rounded-xl border p-3 ${depth > 0 ? "ml-5 border-slate-100 bg-slate-50" : "border-slate-200 bg-white"}`}
    >
      <div className="flex items-center justify-between gap-2 text-xs text-slate-400">
        <span>
          {comment.author_user_id.slice(0, 8)} ·{" "}
          {formatDate(comment.created_at, locale)}
        </span>
        <Pill tone={comment.is_resolved ? "green" : "slate"}>
          {comment.is_resolved ? t("comments.resolved") : t("comments.open")}
        </Pill>
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-700">{comment.body}</p>
      {comment.mentions && comment.mentions.length > 0 && (
        <p
          className="mt-2 text-xs text-blue-700"
          data-testid="comment-mentions"
        >
          {t("comments.mentionsLabel")}:{" "}
          {comment.mentions
            .map((mention) => `@${mention.display_name}`)
            .join(", ")}
        </p>
      )}
      <div className="mt-3 flex flex-wrap gap-2">
        <Button kind="quiet" onClick={() => onReply(comment.id)}>
          {t("comments.reply")}
        </Button>
        <Button
          kind="quiet"
          onClick={() => void onResolve(comment)}
          disabled={busy}
        >
          {comment.is_resolved
            ? t("comments.unresolve")
            : t("comments.resolve")}
        </Button>
        <Button kind="quiet" onClick={() => onAssignTask(comment.id)}>
          {t("comments.assignTask")}
        </Button>
      </div>
      {children.length > 0 && (
        <div className="mt-3 space-y-3" data-testid={`replies-${comment.id}`}>
          {children.map((child) => (
            <CommentNode
              key={child.id}
              comment={child}
              childrenByParent={childrenByParent}
              depth={depth + 1}
              visited={nextVisited}
              onReply={onReply}
              onResolve={onResolve}
              onAssignTask={onAssignTask}
              busy={busy}
            />
          ))}
        </div>
      )}
    </article>
  );
}

function CommentsPanel({
  entry,
  comments,
  replyTo,
  onReply,
  onSubmit,
  onResolve,
  mentionableUsers,
  onAssignTask,
  bodyRef,
  loading,
  error,
  busy,
}: {
  entry: TimelineEntry;
  comments: Comment[];
  replyTo: string | null;
  onReply: (id: string | null) => void;
  onSubmit: (body: string, mentionedUserIds: string[]) => Promise<void>;
  onResolve: (comment: Comment) => Promise<void>;
  mentionableUsers: MentionUser[];
  onAssignTask: (commentId: string) => void;
  bodyRef: RefObject<HTMLTextAreaElement | null>;
  loading: boolean;
  error: string | null;
  busy: boolean;
}) {
  const { t } = useI18n();
  const [body, setBody] = useState("");
  const [selectedMentionIds, setSelectedMentionIds] = useState<Set<string>>(
    new Set(),
  );
  const [mentionIndex, setMentionIndex] = useState(0);
  const mentionMatch = /(?:^|\s)@([^\s@]*)$/.exec(body);
  const mentionOptions = mentionMatch
    ? mentionableUsers.filter((user) =>
        user.display_name.toLowerCase().includes(mentionMatch[1].toLowerCase()),
      )
    : [];
  const commentIds = new Set(comments.map((comment) => comment.id));
  const childrenByParent = new Map<string, Comment[]>();
  for (const comment of comments) {
    if (comment.parent_comment_id === null) continue;
    const children = childrenByParent.get(comment.parent_comment_id) ?? [];
    children.push(comment);
    childrenByParent.set(comment.parent_comment_id, children);
  }
  const roots = comments.filter(
    (comment) =>
      comment.parent_comment_id === null ||
      !commentIds.has(comment.parent_comment_id),
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!body.trim()) return;
    await onSubmit(body.trim(), Array.from(selectedMentionIds));
    setBody("");
    setSelectedMentionIds(new Set());
  }

  function selectMention(user: MentionUser) {
    if (!mentionMatch || mentionMatch.index === undefined) return;
    const tokenStart = mentionMatch.index + mentionMatch[0].indexOf("@");
    setBody(`${body.slice(0, tokenStart)}@${user.display_name} `);
    setSelectedMentionIds((current) => new Set(current).add(user.user_id));
    setMentionIndex(0);
  }

  function handleBodyKeyDown(event: ReactKeyboardEvent<HTMLTextAreaElement>) {
    if (mentionOptions.length === 0) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setMentionIndex((current) => (current + 1) % mentionOptions.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setMentionIndex(
        (current) =>
          (current - 1 + mentionOptions.length) % mentionOptions.length,
      );
    } else if (event.key === "Enter") {
      event.preventDefault();
      selectMention(mentionOptions[mentionIndex]);
    } else if (event.key === "Escape") {
      event.preventDefault();
      setMentionIndex(0);
      setBody(body.replace(/(?:^|\s)@[^\s@]*$/, ""));
    }
  }

  return (
    <section
      className="space-y-4"
      aria-label={t("button.comments")}
      data-entry-id={entry.id}
      data-testid="comments-panel"
    >
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
        {t("comments.internal")}
      </p>
      {loading && (
        <p
          className="rounded-xl bg-blue-50 p-3 text-sm text-blue-800"
          role="status"
          aria-live="polite"
          data-testid="comments-loading"
        >
          {t("comments.loading")}
        </p>
      )}
      {error && (
        <p
          className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
          role="alert"
          data-testid="comments-error"
        >
          {error}
        </p>
      )}
      <div className="mt-4 space-y-3">
        {!loading && comments.length === 0 && (
          <p className="rounded-xl bg-slate-50 p-3 text-sm text-slate-500">
            {t("comments.noComments")}
          </p>
        )}
        {roots.map((comment) => (
          <CommentNode
            key={comment.id}
            comment={comment}
            childrenByParent={childrenByParent}
            depth={0}
            visited={new Set()}
            onReply={onReply}
            onResolve={onResolve}
            onAssignTask={onAssignTask}
            busy={busy}
          />
        ))}
      </div>
      <form
        className="mt-4 space-y-2 border-t border-slate-100 pt-4"
        onSubmit={submit}
      >
        {replyTo && (
          <p className="text-xs text-blue-700">
            {t("comments.replying")}{" "}
            <button
              className="underline"
              type="button"
              onClick={() => onReply(null)}
            >
              {t("comments.cancel")}
            </button>
          </p>
        )}
        <textarea
          ref={bodyRef}
          aria-label={t("comments.bodyLabel")}
          value={body}
          onChange={(event) => {
            setBody(event.target.value);
            setMentionIndex(0);
          }}
          onKeyDown={handleBodyKeyDown}
          placeholder={t("comments.placeholder")}
          aria-autocomplete="list"
          aria-controls="mention-suggestions"
          className="min-h-24 w-full resize-y rounded-xl border border-slate-200 p-3 text-sm outline-none ring-blue-200 focus:border-blue-500 focus:ring-4"
        />
        {mentionOptions.length > 0 && (
          <div
            id="mention-suggestions"
            className="rounded-xl border border-blue-100 bg-blue-50 p-2"
            role="listbox"
            aria-label={t("comments.mentionSuggestions")}
          >
            {mentionOptions.map((user, index) => (
              <button
                key={user.user_id}
                type="button"
                role="option"
                aria-selected={index === mentionIndex}
                className="block w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 hover:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-200"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => selectMention(user)}
              >
                @{user.display_name} · {user.role}
              </button>
            ))}
          </div>
        )}
        <Button type="submit" kind="primary" disabled={busy || !body.trim()}>
          {t("comments.add")}
        </Button>
      </form>
    </section>
  );
}

function HistoryPanel({
  entry,
  versions,
  diff,
  conflicts,
  canEdit,
  onDiff,
  onRevert,
}: {
  entry: TimelineEntry;
  versions: Version[];
  diff: Diff | null;
  conflicts: Conflict[];
  canEdit: boolean;
  onDiff: (version: number) => void;
  onRevert: (version: number) => void;
}) {
  const { locale, t } = useI18n();
  return (
    <section
      className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4"
      aria-label={t("history.title")}
    >
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold text-slate-800">
          {t("history.title")}
        </h3>
        <Pill>{t("history.current", { version: entry.current_version })}</Pill>
      </div>
      <div className="mt-3 space-y-2">
        {versions.map((version) => (
          <div
            key={version.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-white p-2 text-xs"
          >
            <span className="font-semibold text-slate-700">
              {t("history.versionRole", {
                version: version.version_number,
                role: t(roleKeys[version.created_by_role] ?? "role.system"),
              })}
            </span>
            <span className="text-slate-400">
              {formatDate(version.created_at, locale)}
            </span>
            <div className="flex gap-1">
              {version.version_number !== entry.current_version && (
                <Button
                  kind="quiet"
                  onClick={() => onDiff(version.version_number)}
                >
                  {t("history.compare")}
                </Button>
              )}
              {canEdit && version.version_number !== entry.current_version && (
                <Button
                  kind="quiet"
                  onClick={() => onRevert(version.version_number)}
                >
                  {t("history.revert")}
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
      {diff && (
        <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-950">
          <p className="font-bold">
            {t("history.diff", {
              from: diff.from_version,
              to: diff.to_version,
            })}
          </p>
          <p className="mt-2">
            <span className="font-semibold">{t("history.before")}</span>{" "}
            {diff.from_content}
          </p>
          <p className="mt-1">
            <span className="font-semibold">{t("history.after")}</span>{" "}
            {diff.to_content}
          </p>
        </div>
      )}
      {conflicts.length > 0 && (
        <section
          className="mt-3 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs leading-5 text-rose-950"
          aria-label={t("history.conflict.title")}
          data-testid="conflict-panel"
        >
          <p className="font-bold">{t("history.conflict.title")}</p>
          <p className="mt-1">{t("history.conflict.description")}</p>
          <div className="mt-3 space-y-3">
            {conflicts.map((conflict) => (
              <article
                key={conflict.id}
                className="rounded-lg border border-rose-200 bg-white p-3"
                data-testid={"conflict-" + conflict.id}
              >
                <p className="font-semibold">
                  {t("history.conflict.expected", {
                    expected: conflict.expected_version,
                    actual: conflict.actual_version,
                  })}
                </p>
                <p className="mt-2">
                  <span className="font-semibold">
                    {t("history.conflict.current")}
                  </span>{" "}
                  {entry.content}
                </p>
                <p className="mt-1">
                  <span className="font-semibold">
                    {t("history.conflict.attempted")}
                  </span>{" "}
                  {conflict.attempted_content}
                </p>
                <p className="mt-2 text-rose-700">
                  {t("history.conflict.status", { status: conflict.status })}
                </p>
              </article>
            ))}
          </div>
        </section>
      )}
    </section>
  );
}

function HistoricalContextPanel({
  context,
  internal,
  timeline,
  onOpenSource,
  onRefresh,
  refreshBusy,
}: {
  context: PatientContext | null;
  internal: boolean;
  timeline: TimelineEntry[];
  onOpenSource: (entryId: string) => void;
  onRefresh: (() => Promise<void>) | null;
  refreshBusy: boolean;
}) {
  const { locale, t } = useI18n();
  if (!context) return null;
  return (
    <section
      className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"
      aria-label={t("context.title")}
      data-testid="historical-context"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
            {t("context.title")}
          </p>
          <h2 className="mt-2 text-xl font-semibold">
            {t("context.subtitle")}
          </h2>
        </div>
        {onRefresh && (
          <Button
            kind="quiet"
            onClick={() => void onRefresh()}
            disabled={refreshBusy}
          >
            {refreshBusy ? t("context.refreshing") : t("context.refresh")}
          </Button>
        )}
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
          <p className="text-xs font-bold uppercase tracking-[0.15em] text-blue-700">
            {t("context.hot")}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {t("context.hotDescription", { count: context.hot_entries.length })}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase tracking-[0.15em] text-slate-500">
            {t("context.warm")}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {t("context.warmDescription", {
              count: context.warm_entries.length,
            })}
          </p>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {context.archival_summaries.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
            {t("context.none")}
          </p>
        ) : (
          context.archival_summaries.map((summary) => (
            <article
              key={summary.id}
              className="rounded-2xl border border-amber-100 bg-amber-50/60 p-4"
              data-testid="archival-summary"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-semibold text-slate-800">
                  {new Intl.DateTimeFormat(
                    locale === "zh-CN" ? "zh-CN" : "en-SG",
                    {
                      month: "long",
                      year: "numeric",
                    },
                  ).format(new Date(summary.period_start))}
                </p>
                <Pill tone="amber">{t("context.derivedSummary")}</Pill>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {summary.summary_text}
              </p>
              <p
                className="mt-2 text-sm font-semibold leading-6 text-amber-950"
                data-testid="derived-summary-label"
              >
                {t("context.derivedSummary")}
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {t("context.derivedExplanation")}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                {t("context.sourcePointer", {
                  count: summary.source_count,
                  plural: summary.source_count === 1 ? "" : "s",
                  policy: summary.policy_version,
                })}
              </p>
              <div className="mt-3 space-y-3">
                {summary.sources.map((source, index) => {
                  const entry = timeline.find(
                    (timelineEntry) =>
                      timelineEntry.id === source.source_entry_id,
                  );
                  const entryType = source.entry_type ?? entry?.entry_type;
                  return (
                    <div
                      key={`${summary.id}-${source.source_entry_id}-${source.source_version_id}`}
                      className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-200 bg-white p-3"
                      data-testid={`historical-source-${source.source_entry_id}`}
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-800">
                          {t("context.originalRecord", { number: index + 1 })}
                        </p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          {t("context.recordMetadata", {
                            type: t(
                              entryTypeKeys[entryType ?? ""] ??
                                "entryType.systemEvent",
                            ),
                            date: formatDate(source.occurred_at, locale),
                            version: source.version_number,
                          })}
                        </p>
                      </div>
                      <Button
                        kind="secondary"
                        onClick={() => onOpenSource(source.source_entry_id)}
                      >
                        {t("context.viewOriginalRecord")}
                      </Button>
                    </div>
                  );
                })}
              </div>
              <p className="mt-3 text-xs font-semibold text-amber-900">
                {t("context.originalTruth")}
              </p>
              {!internal && (
                <p className="mt-3 text-xs text-slate-500">
                  {t("context.patientPointers")}
                </p>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function TaskPanel({
  tasks,
  collaborators,
  canEdit,
  sourceLabel,
  sourceComment,
  onCreate,
  onUpdate,
  onCloseComposer,
  titleInputRef,
  error,
  focusedTaskId,
}: {
  tasks: Task[];
  collaborators: MentionUser[];
  canEdit: boolean;
  sourceLabel: string | null;
  sourceComment: string | null;
  onCreate: (title: string, assigneeId: string) => Promise<void>;
  onUpdate: (
    task: Task,
    patch: {
      title?: string;
      assigned_to_user_id?: string;
      status?: TaskStatus;
    },
  ) => Promise<void>;
  onCloseComposer: () => void;
  titleInputRef: RefObject<HTMLInputElement | null>;
  error: string | null;
  focusedTaskId: string | null;
}) {
  const { t } = useI18n();
  const [composerOpen, setComposerOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!assigneeId && collaborators[0])
      setAssigneeId(collaborators[0].user_id);
  }, [assigneeId, collaborators]);

  useEffect(() => {
    if (sourceLabel || sourceComment) setComposerOpen(true);
  }, [sourceComment, sourceLabel]);

  useEffect(() => {
    if (composerOpen) titleInputRef.current?.focus();
  }, [composerOpen, titleInputRef]);

  useEffect(() => {
    if (!focusedTaskId) return;
    const timer = window.setTimeout(() => {
      const taskElement = document.getElementById(`task-${focusedTaskId}`);
      scrollToElement(taskElement);
      taskElement?.focus();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [focusedTaskId]);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim() || !assigneeId) return;
    setBusy(true);
    try {
      await onCreate(title.trim(), assigneeId);
      setTitle("");
      setComposerOpen(false);
    } catch {
      // The parent renders the safe API error inside this drawer.
    } finally {
      setBusy(false);
    }
  }

  async function update(
    task: Task,
    patch: {
      title?: string;
      assigned_to_user_id?: string;
      status?: TaskStatus;
    },
  ) {
    setBusy(true);
    try {
      await onUpdate(task, patch);
    } catch {
      // The parent renders the safe API error inside this drawer.
    } finally {
      setBusy(false);
    }
  }

  return (
    <section
      className="rounded-2xl border border-slate-200 bg-white p-5"
      aria-label={t("task.panel")}
      data-testid="task-panel"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
            {t("task.panel")}
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-900">
            {tasks.length} · {t("task.panel")}
          </h2>
        </div>
        {canEdit && (
          <Button kind="quiet" onClick={() => setComposerOpen(true)}>
            {t("task.new")}
          </Button>
        )}
      </div>
      {error && (
        <p
          className="mt-3 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
          role="alert"
          data-testid="task-error"
        >
          {error}
        </p>
      )}
      {(sourceLabel || sourceComment) && (
        <div className="mt-3 space-y-2 rounded-lg bg-blue-50 p-3 text-xs leading-5 text-blue-800">
          <p>
            {sourceComment
              ? t("task.creatingForComment")
              : t("task.creatingFor", { label: sourceLabel ?? "" })}
          </p>
          {sourceLabel && (
            <p>{t("task.sourceEntry", { label: sourceLabel })}</p>
          )}
          {sourceComment && (
            <p className="break-words">
              {t("task.commentBody", { body: sourceComment })}
            </p>
          )}
        </div>
      )}
      {composerOpen && canEdit && (
        <form
          className="mt-4 space-y-3 border-t border-slate-100 pt-4"
          onSubmit={create}
        >
          <label className="block text-sm font-semibold text-slate-700">
            {t("task.titleLabel")}
            <input
              ref={titleInputRef}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder={t("task.titlePlaceholder")}
              aria-label={t("task.titleLabel")}
              className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              required
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            {t("task.assigneeLabel")}
            <select
              value={assigneeId}
              onChange={(event) => setAssigneeId(event.target.value)}
              aria-label={t("task.assigneeLabel")}
              className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              required
            >
              <option value="">{t("task.chooseAssignee")}</option>
              {collaborators.map((user) => (
                <option key={user.user_id} value={user.user_id}>
                  {user.display_name} · {user.role}
                </option>
              ))}
            </select>
          </label>
          <div className="flex flex-wrap gap-2">
            <Button
              type="submit"
              kind="primary"
              disabled={busy || !title.trim()}
            >
              {t("task.create")}
            </Button>
            <Button
              kind="quiet"
              onClick={() => {
                setComposerOpen(false);
                onCloseComposer();
              }}
            >
              {t("task.cancel")}
            </Button>
          </div>
        </form>
      )}
      <div className="mt-4 space-y-3">
        {tasks.length === 0 ? (
          <p className="rounded-xl bg-slate-50 p-3 text-sm text-slate-500">
            {t("task.empty")}
          </p>
        ) : (
          tasks.map((task) => (
            <article
              key={task.id}
              tabIndex={-1}
              className="rounded-xl border border-slate-200 bg-slate-50 p-3"
              data-testid={`task-${task.id}`}
            >
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-semibold text-slate-800">
                  {task.title}
                </p>
                <Pill tone={task.status === "done" ? "green" : "amber"}>
                  {t(taskStatusKeys[task.status])}
                </Pill>
              </div>
              <p className="mt-2 text-xs text-slate-500">
                {t("task.assignedTo", { name: task.assigned_to.display_name })}{" "}
                · {t("task.version", { version: task.version })}
              </p>
              {canEdit && task.status !== "done" && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <select
                    value={task.status}
                    aria-label={`${t("task.statusLabel")}: ${task.title}`}
                    onChange={(event) =>
                      void update(task, {
                        status: event.target.value as TaskStatus,
                      })
                    }
                    disabled={busy}
                    className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs outline-none focus:ring-4 focus:ring-blue-100"
                  >
                    <option value="open">{t("task.status.open")}</option>
                    <option value="in_progress">
                      {t("task.status.inProgress")}
                    </option>
                    <option value="done">{t("task.status.done")}</option>
                  </select>
                  {collaborators.length > 0 && (
                    <select
                      value={task.assigned_to.user_id}
                      aria-label={`${t("task.assigneeLabel")}: ${task.title}`}
                      onChange={(event) =>
                        void update(task, {
                          assigned_to_user_id: event.target.value,
                        })
                      }
                      disabled={busy}
                      className="max-w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs outline-none focus:ring-4 focus:ring-blue-100"
                    >
                      {collaborators.map((user) => (
                        <option key={user.user_id} value={user.user_id}>
                          {user.display_name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}

type AIScribeInteraction =
  | "ai_doctor_consult_summary"
  | "ai_nurse_consult_summary"
  | "ai_patient_session_summary";

const aiScribeExamples: Record<
  AIScribeInteraction,
  { text: string; reference: string }
> = {
  ai_doctor_consult_summary: {
    text: "During this synthetic doctor follow-up, the patient reported that the scheduled laboratory review remains pending. No diagnosis or treatment recommendation was made.",
    reference: "synthetic-doctor-demo",
  },
  ai_nurse_consult_summary: {
    text: "During this synthetic nurse follow-up, the patient reported that the scheduled laboratory review remains pending. No diagnosis or treatment recommendation was made.",
    reference: "synthetic-nurse-demo",
  },
  ai_patient_session_summary: {
    text: "During this synthetic AI-patient session, the patient asked what preparation is needed for the next visit. No diagnosis or treatment recommendation was made.",
    reference: "synthetic-patient-session-demo",
  },
};

function AIScribePanel({
  providerInfo,
  providerError,
  job,
  busy,
  onSubmit,
  onOpenSource,
}: {
  providerInfo: AIProviderInfo | null;
  providerError: string | null;
  job: AIJob | null;
  busy: boolean;
  onSubmit: (payload: {
    interaction_type: AIScribeInteraction;
    text: string;
    source_reference: string;
    idempotency_key: string;
  }) => Promise<void>;
  onOpenSource: (job: AIJob) => void;
}) {
  const { t } = useI18n();
  const [interactionType, setInteractionType] = useState<AIScribeInteraction>(
    "ai_doctor_consult_summary",
  );
  const [text, setText] = useState(
    aiScribeExamples.ai_doctor_consult_summary.text,
  );
  const [sourceReference, setSourceReference] = useState(
    aiScribeExamples.ai_doctor_consult_summary.reference,
  );
  const providerLabel =
    providerInfo?.mode === "deepseek" ? t("ai.deepseek") : t("ai.fixture");

  function changeInteraction(next: AIScribeInteraction) {
    setInteractionType(next);
    const example = aiScribeExamples[next];
    setText(example.text);
    setSourceReference(example.reference);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      interaction_type: interactionType,
      text: text.trim(),
      source_reference: sourceReference.trim(),
      idempotency_key: `ui-ai-${Date.now()}-${interactionType}`,
    });
  }

  return (
    <section
      className="rounded-3xl border border-amber-200 bg-amber-50/70 p-5 shadow-sm sm:p-7"
      aria-label={t("ai.panel")}
      data-testid="ai-scribe-panel"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-800">
            {t("ai.panel")}
          </p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">
            {t("ai.title")}
          </h2>
        </div>
        <Pill tone="amber">{providerLabel}</Pill>
      </div>
      <p className="mt-3 rounded-xl border border-amber-200 bg-white/80 p-3 text-sm font-semibold leading-6 text-amber-950">
        {t("ai.warning")}
      </p>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
        <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-semibold">
          {t("ai.provider")}: {providerLabel}
        </span>
        {providerInfo?.model && (
          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-semibold">
            {providerInfo.model}
          </span>
        )}
        {providerInfo?.mode === "deepseek" && !providerInfo.configured && (
          <span className="rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 font-semibold text-rose-700">
            {t("ai.notConfigured")}
          </span>
        )}
      </div>
      {providerError && (
        <p
          className="mt-3 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
          role="alert"
        >
          {providerError}
        </p>
      )}
      <form className="mt-5 space-y-4" onSubmit={submit}>
        <label className="block text-sm font-semibold text-slate-700">
          {t("ai.interactionType")}
          <select
            value={interactionType}
            onChange={(event) =>
              changeInteraction(event.target.value as AIScribeInteraction)
            }
            aria-label={t("ai.interactionType")}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          >
            <option value="ai_doctor_consult_summary">{t("ai.doctor")}</option>
            <option value="ai_nurse_consult_summary">{t("ai.nurse")}</option>
            <option value="ai_patient_session_summary">
              {t("ai.patientSession")}
            </option>
          </select>
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          {t("ai.text")}
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            aria-label={t("ai.text")}
            placeholder={t("ai.textPlaceholder")}
            className="mt-2 min-h-28 w-full resize-y rounded-xl border border-slate-200 bg-white p-3 text-sm leading-6 outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            required
          />
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          {t("ai.reference")}
          <input
            value={sourceReference}
            onChange={(event) => setSourceReference(event.target.value)}
            aria-label={t("ai.reference")}
            placeholder={t("ai.referencePlaceholder")}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            required
          />
        </label>
        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" kind="primary" disabled={busy || !text.trim()}>
            {busy ? t("ai.generating") : t("ai.generate")}
          </Button>
          {busy && (
            <span
              className="text-sm text-slate-600"
              role="status"
              aria-live="polite"
            >
              {t("ai.processing")}
            </span>
          )}
        </div>
      </form>
      {job && (
        <div
          className="mt-5 rounded-xl border border-slate-200 bg-white p-4 text-sm"
          data-testid="ai-job-result"
        >
          <p className="font-semibold text-slate-900">
            {t("ai.status")}: {job.status}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {t("ai.provider")}: {job.provider_name}
          </p>
          {job.status === "completed" ? (
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <p className="font-semibold text-amber-800">
                {t("ai.requiresReview")}
              </p>
              {job.highlight_id && (
                <Button kind="secondary" onClick={() => onOpenSource(job)}>
                  {t("ai.openSource")}
                </Button>
              )}
            </div>
          ) : job.status.startsWith("failed") ? (
            <p className="mt-3 text-rose-700" role="alert">
              {t("ai.safeError", { code: job.error_code ?? "provider_failed" })}
            </p>
          ) : (
            <p className="mt-3 text-slate-600">{t("ai.processing")}</p>
          )}
        </div>
      )}
    </section>
  );
}

function formatVoiceTime(milliseconds: number) {
  return `${(milliseconds / 1000).toFixed(1)}s`;
}

function VoicePanel({
  providerInfo,
  samples,
  session,
  busy,
  error,
  onProcess,
  onOpenSource,
}: {
  providerInfo: VoiceProviderInfo;
  samples: VoiceSample[];
  session: VoiceSession | null;
  busy: boolean;
  error: string | null;
  onProcess: (sampleId: string) => Promise<void>;
  onOpenSource: (highlightId: string) => Promise<void>;
}) {
  const { t } = useI18n();
  const [selectedSampleId, setSelectedSampleId] = useState(
    samples[0]?.sample_id ?? "",
  );
  const audioRef = useRef<HTMLAudioElement>(null);
  const selectedSample =
    samples.find((sample) => sample.sample_id === selectedSampleId) ??
    samples[0] ??
    null;

  useEffect(() => {
    if (!samples.some((sample) => sample.sample_id === selectedSampleId)) {
      setSelectedSampleId(samples[0]?.sample_id ?? "");
    }
  }, [samples, selectedSampleId]);

  function seekTo(segment: TranscriptSegment) {
    if (audioRef.current)
      audioRef.current.currentTime = segment.start_ms / 1000;
  }

  return (
    <section
      className="rounded-3xl border border-violet-200 bg-violet-50/70 p-5 shadow-sm sm:p-7"
      aria-label={t("voice.panel")}
      data-testid="voice-panel"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-violet-800">
            {t("voice.panel")}
          </p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">
            {t("voice.title")}
          </h2>
        </div>
        <Pill tone="blue">{providerInfo.provider_name}</Pill>
      </div>
      <p className="mt-3 rounded-xl border border-violet-200 bg-white/80 p-3 text-sm font-semibold leading-6 text-violet-950">
        {t("voice.warning")}
      </p>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
        <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-semibold">
          {t("voice.provider")}: {providerInfo.model}
        </span>
        <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-semibold">
          {providerInfo.disclosure}
        </span>
      </div>
      {error && (
        <p
          className="mt-3 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
          role="alert"
          data-testid="voice-error"
        >
          {error}
        </p>
      )}
      {selectedSample && (
        <div className="mt-5 space-y-4">
          <label className="block text-sm font-semibold text-slate-700">
            {t("voice.selectSample")}
            <select
              value={selectedSample.sample_id}
              onChange={(event) => setSelectedSampleId(event.target.value)}
              aria-label={t("voice.selectSample")}
              className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            >
              {samples.map((sample) => (
                <option key={sample.sample_id} value={sample.sample_id}>
                  {sample.label} · {sample.scope}
                </option>
              ))}
            </select>
          </label>
          <audio
            ref={audioRef}
            controls
            preload="metadata"
            src={selectedSample.audio_url}
            aria-label={t("voice.audioLabel", { label: selectedSample.label })}
            className="w-full"
            data-testid="voice-audio"
          />
          <p className="text-xs text-slate-600">
            {t("voice.duration", {
              duration: formatVoiceTime(selectedSample.duration_ms),
            })}
          </p>
          <Button
            kind="primary"
            disabled={busy}
            onClick={() => void onProcess(selectedSample.sample_id)}
          >
            {busy ? t("voice.processing") : t("voice.process")}
          </Button>
        </div>
      )}
      {session && (
        <div
          className="mt-5 rounded-xl border border-slate-200 bg-white p-4 text-sm"
          data-testid="voice-session-result"
        >
          <p className="font-semibold text-slate-900">
            {t("voice.status")}: {session.status}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {t("voice.provider")}: {session.asr_provider} · {session.asr_model}
          </p>
          {session.status.startsWith("failed") ? (
            <p className="mt-3 text-rose-700" role="alert">
              {t("voice.failed", {
                code: session.error_code ?? "voice_failed",
              })}
            </p>
          ) : session.status !== "completed" ? (
            <p className="mt-3 text-slate-600" role="status">
              {t("voice.processing")}
            </p>
          ) : (
            <>
              <p className="mt-3 font-semibold text-amber-800">
                {t("voice.requiresReview")}
              </p>
              <div
                className="mt-3 space-y-2"
                aria-label={t("voice.transcript")}
              >
                {session.segments.map((segment) => (
                  <button
                    key={segment.id}
                    type="button"
                    className="block w-full rounded-lg border border-slate-200 bg-slate-50 p-3 text-left transition hover:border-violet-300 hover:bg-violet-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-violet-200"
                    data-testid={`voice-segment-${segment.segment_index}`}
                    onClick={() => seekTo(segment)}
                  >
                    <span className="font-semibold text-violet-800">
                      {formatVoiceTime(segment.start_ms)} -{" "}
                      {formatVoiceTime(segment.end_ms)}
                    </span>
                    <span className="mt-1 block leading-6 text-slate-700">
                      {segment.text}
                    </span>
                    <span className="mt-1 block text-xs text-slate-500">
                      {segment.confidence === null
                        ? t("voice.confidenceUnavailable")
                        : t("voice.confidence", {
                            confidence: segment.confidence.toFixed(2),
                          })}
                    </span>
                  </button>
                ))}
              </div>
              {session.highlight_id && !session.patient_safe && (
                <Button
                  kind="secondary"
                  onClick={() =>
                    void onOpenSource(session.highlight_id as string)
                  }
                >
                  {t("voice.openSource")}
                </Button>
              )}
            </>
          )}
        </div>
      )}
    </section>
  );
}

function Workspace({ user, onLogout }: { user: Me; onLogout: () => void }) {
  const { locale, t } = useI18n();
  const internal = isInternalUser(user);
  const role = primaryRole(user);
  const [patients, setPatients] = useState<Patient[]>([]);
  const queryParams = new URLSearchParams(window.location.search);
  const isEmbeddedPreview = queryParams.get("embedded") === "1";
  const [patientId, setPatientId] = useState(
    queryParams.get("patient") ?? user.patient_ids[0] ?? "",
  );
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [glance, setGlance] = useState<GlanceItem[]>([]);
  const [context, setContext] = useState<PatientContext | null>(null);
  const [collaborators, setCollaborators] = useState<MentionUser[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [realtimeStatus, setRealtimeStatus] = useState<
    "connecting" | "connected" | "reconnecting" | "unavailable"
  >("connecting");
  const [remoteUpdatePending, setRemoteUpdatePending] = useState(false);
  const [taskSource, setTaskSource] = useState<{
    entryId: string | null;
    commentId: string | null;
    label: string | null;
  } | null>(null);
  const [taskDrawerOpen, setTaskDrawerOpen] = useState(false);
  const [taskFocusId, setTaskFocusId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const [source, setSource] = useState<ProvenanceSource | null>(null);
  const [sourceLoading, setSourceLoading] = useState(false);
  const [focusEntryId, setFocusEntryId] = useState<string | null>(null);
  const [commentsEntryId, setCommentsEntryId] = useState<string | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const [commentBusy, setCommentBusy] = useState(false);
  const [commentsError, setCommentsError] = useState<string | null>(null);
  const [historyEntryId, setHistoryEntryId] = useState<string | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [diff, setDiff] = useState<Diff | null>(null);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [editingEntryId, setEditingEntryId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState("");
  const [mutationError, setMutationError] = useState<string | null>(null);
  const [taskError, setTaskError] = useState<string | null>(null);
  const [mutationBusy, setMutationBusy] = useState(false);
  const [feedbackBusyId, setFeedbackBusyId] = useState<string | null>(null);
  const [pinnedItems, setPinnedItems] = useState<Set<string>>(new Set());
  const [guideOpen, setGuideOpen] = useState(false);
  const [aiProviderInfo, setAIProviderInfo] = useState<AIProviderInfo | null>(
    null,
  );
  const [aiProviderError, setAIProviderError] = useState<string | null>(null);
  const [aiJob, setAIJob] = useState<AIJob | null>(null);
  const [aiBusy, setAIBusy] = useState(false);
  const [pendingAIEntryId, setPendingAIEntryId] = useState<string | null>(null);
  const [voiceProviderInfo, setVoiceProviderInfo] =
    useState<VoiceProviderInfo | null>(null);
  const [voiceSamples, setVoiceSamples] = useState<VoiceSample[]>([]);
  const [voiceSession, setVoiceSession] = useState<VoiceSession | null>(null);
  const [voiceBusy, setVoiceBusy] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const commentsInputRef = useRef<HTMLTextAreaElement>(null);
  const commentsReturnFocusRef = useRef<HTMLElement | null>(null);
  const commentsRequestRef = useRef(0);
  const commentsEntryIdRef = useRef<string | null>(null);
  const editingEntryIdRef = useRef<string | null>(null);
  const translationRef = useRef(t);
  const taskTitleInputRef = useRef<HTMLInputElement>(null);
  const taskReturnFocusRef = useRef<HTMLElement | null>(null);
  commentsEntryIdRef.current = commentsEntryId;
  editingEntryIdRef.current = editingEntryId;
  translationRef.current = t;

  useEffect(() => {
    let active = true;
    api
      .patients()
      .then((result) => {
        if (!active) return;
        setPatients(result);
        setPatientId((current) =>
          result.some((patient) => patient.id === current)
            ? current
            : result[0]?.id || "",
        );
      })
      .catch((error) => active && setLoadError(displayError(error, t)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [user.id]);

  useEffect(() => {
    commentsRequestRef.current += 1;
    commentsEntryIdRef.current = null;
    editingEntryIdRef.current = null;
    commentsReturnFocusRef.current = null;
    taskReturnFocusRef.current = null;
    setSource(null);
    setContext(null);
    setCollaborators([]);
    setTasks([]);
    setTimeline([]);
    setGlance([]);
    setTaskSource(null);
    setTaskDrawerOpen(false);
    setTaskFocusId(null);
    setTaskError(null);
    setAIJob(null);
    setPendingAIEntryId(null);
    setSourceLoading(false);
    setFocusEntryId(null);
    setCommentsEntryId(null);
    setComments([]);
    setCommentsError(null);
    setReplyTo(null);
    setCommentBusy(false);
    setHistoryEntryId(null);
    setVersions([]);
    setDiff(null);
    setConflicts([]);
    setEditingEntryId(null);
    setEditingText("");
    setRemoteUpdatePending(false);
    setMutationError(null);
  }, [patientId, internal, user.id]);

  useEffect(() => {
    if (!patientId) return;
    let active = true;
    setLoading(true);
    setLoadError(null);
    const requestedHighlightId = new URLSearchParams(
      window.location.search,
    ).get("highlight");
    const glanceRequest = internal
      ? api.glance(patientId)
      : Promise.resolve([] as GlanceItem[]);
    const collaboratorsRequest = internal
      ? api.mentionableUsers(patientId)
      : Promise.resolve([] as MentionUser[]);
    const tasksRequest = internal
      ? api.tasks(patientId)
      : Promise.resolve([] as Task[]);
    Promise.all([
      api.timeline(patientId),
      glanceRequest,
      api.context(patientId),
      collaboratorsRequest,
      tasksRequest,
    ])
      .then(
        async ([
          timelineResult,
          glanceResult,
          contextResult,
          collaboratorsResult,
          tasksResult,
        ]) => {
          if (!active) return;
          const activeCommentEntryId = commentsEntryIdRef.current;
          if (
            activeCommentEntryId &&
            !timelineResult.some((entry) => entry.id === activeCommentEntryId)
          ) {
            commentsRequestRef.current += 1;
            commentsEntryIdRef.current = null;
            setCommentsEntryId(null);
            setComments([]);
            setCommentsError(null);
            setReplyTo(null);
            setCommentBusy(false);
            setMutationError(
              translationRef.current("comments.entryUnavailable"),
            );
          }
          setTimeline(timelineResult);
          setGlance(glanceResult);
          setContext(contextResult);
          setCollaborators(collaboratorsResult);
          setTasks(tasksResult);
          if (internal && requestedHighlightId) {
            setSourceLoading(true);
            const linkedSource = await api.source(requestedHighlightId);
            if (
              active &&
              linkedSource.highlight.patient_id === patientId &&
              timelineResult.some(
                (entry) => entry.id === linkedSource.source_entry_id,
              )
            ) {
              setSource(linkedSource);
              setFocusEntryId(linkedSource.source_entry_id);
              window.setTimeout(() => {
                scrollToElement(
                  document.getElementById(
                    "timeline-entry-" + linkedSource.source_entry_id,
                  ),
                );
              }, 0);
              window.setTimeout(() => setFocusEntryId(null), 2400);
            }
            if (active) setSourceLoading(false);
          }
        },
      )
      .catch((error) => active && setLoadError(displayError(error, t)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [patientId, internal, refreshToken]);

  useEffect(() => {
    setPinnedItems(new Set());
  }, [patientId]);

  const canUseAIScribe = role === "staff" || role === "clinician";

  useEffect(() => {
    if (!canUseAIScribe) {
      setAIProviderInfo(null);
      setAIProviderError(null);
      return;
    }
    setAIProviderInfo(null);
    setAIProviderError(null);
    void api
      .aiProvider()
      .then(setAIProviderInfo)
      .catch((error) => setAIProviderError(displayError(error, t)));
  }, [canUseAIScribe, t, user.id]);

  useEffect(() => {
    let active = true;
    api
      .voiceProvider()
      .then((result) => active && setVoiceProviderInfo(result))
      .catch((error) => active && setVoiceError(displayError(error, t)));
    return () => {
      active = false;
    };
  }, [t, user.id]);

  useEffect(() => {
    if (!patientId || !voiceProviderInfo?.enabled) {
      setVoiceSamples([]);
      setVoiceSession(null);
      return;
    }
    let active = true;
    setVoiceError(null);
    api
      .voiceSamples(patientId)
      .then(
        (result) =>
          active && setVoiceSamples(Array.isArray(result) ? result : []),
      )
      .catch((error) => active && setVoiceError(displayError(error, t)));
    return () => {
      active = false;
    };
  }, [patientId, t, voiceProviderInfo?.enabled]);

  useEffect(() => {
    if (
      !pendingAIEntryId ||
      !timeline.some((entry) => entry.id === pendingAIEntryId)
    )
      return;
    setFocusEntryId(pendingAIEntryId);
    window.setTimeout(() => {
      scrollToElement(
        document.getElementById(`timeline-entry-${pendingAIEntryId}`),
      );
    }, 0);
    window.setTimeout(() => setFocusEntryId(null), 2400);
    setPendingAIEntryId(null);
  }, [pendingAIEntryId, timeline]);

  useEffect(() => {
    if (!patientId || !internal || typeof EventSource === "undefined") {
      setRealtimeStatus("unavailable");
      return;
    }
    setRealtimeStatus("connecting");
    const stream = new EventSource(api.eventsUrl(patientId), {
      withCredentials: true,
    });
    stream.onopen = () => setRealtimeStatus("connected");
    stream.onerror = () => setRealtimeStatus("reconnecting");
    stream.addEventListener("collaboration", (event) => {
      try {
        const payload = JSON.parse((event as MessageEvent<string>).data) as {
          resource_type?: string;
        };
        const activeCommentsEntryId = commentsEntryIdRef.current;
        if (payload.resource_type === "comment" && activeCommentsEntryId) {
          void api
            .comments(activeCommentsEntryId)
            .then(setComments)
            .catch((error) =>
              setCommentsError(displayError(error, translationRef.current)),
            );
          return;
        }
        if (payload.resource_type === "task") {
          void refreshTasksAndGlance().catch((error) =>
            setLoadError(displayError(error, translationRef.current)),
          );
          return;
        }
        if (editingEntryIdRef.current) {
          setRemoteUpdatePending(true);
        } else {
          setRefreshToken((value) => value + 1);
        }
      } catch {
        // Event payloads are metadata-only invalidations; malformed events are ignored.
      }
    });
    return () => stream.close();
  }, [patientId, internal, user.id]);

  const selectedPatient = useMemo(
    () => patients.find((patient) => patient.id === patientId),
    [patients, patientId],
  );
  const selectedEntry =
    timeline.find((entry) => entry.id === commentsEntryId) ?? null;

  async function openSource(item: GlanceItem) {
    setSourceLoading(true);
    setMutationError(null);
    try {
      const result = await api.source(item.id);
      setSource(result);
      setFocusEntryId(result.source_entry_id);
      window.history.replaceState(
        {},
        "",
        `?patient=${patientId}&highlight=${item.id}`,
      );
      window.setTimeout(() => {
        scrollToElement(
          document.getElementById(`timeline-entry-${result.source_entry_id}`),
        );
      }, 0);
      window.setTimeout(() => setFocusEntryId(null), 2400);
    } catch (error) {
      setMutationError(displayError(error, t));
    } finally {
      setSourceLoading(false);
    }
  }

  async function openHighlightSource(highlightId: string) {
    if (!patientId) return;
    setSourceLoading(true);
    setMutationError(null);
    try {
      const result = await api.source(highlightId);
      setSource(result);
      setPendingAIEntryId(result.source_entry_id);
      setFocusEntryId(result.source_entry_id);
      const nextUrl = new URL(window.location.href);
      nextUrl.searchParams.set("patient", patientId);
      nextUrl.searchParams.set("highlight", highlightId);
      window.history.replaceState(
        {},
        "",
        `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`,
      );
      window.setTimeout(() => {
        scrollToElement(
          document.getElementById(`timeline-entry-${result.source_entry_id}`),
        );
      }, 0);
      window.setTimeout(() => setFocusEntryId(null), 2400);
    } catch (error) {
      setMutationError(displayError(error, t));
    } finally {
      setSourceLoading(false);
    }
  }

  async function openAIJobSource(job: AIJob) {
    if (!patientId || !job.highlight_id) return;
    setSourceLoading(true);
    setMutationError(null);
    try {
      const result = await api.source(job.highlight_id);
      setSource(result);
      setPendingAIEntryId(result.source_entry_id);
      setFocusEntryId(result.source_entry_id);
      const nextUrl = new URL(window.location.href);
      nextUrl.searchParams.set("patient", patientId);
      nextUrl.searchParams.set("highlight", job.highlight_id);
      window.history.replaceState(
        {},
        "",
        `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`,
      );
      window.setTimeout(() => {
        scrollToElement(
          document.getElementById(`timeline-entry-${result.source_entry_id}`),
        );
      }, 0);
      window.setTimeout(() => setFocusEntryId(null), 2400);
    } catch (error) {
      setMutationError(displayError(error, t));
    } finally {
      setSourceLoading(false);
    }
  }

  async function submitAIScribe(payload: {
    interaction_type:
      | "ai_doctor_consult_summary"
      | "ai_nurse_consult_summary"
      | "ai_patient_session_summary";
    text: string;
    source_reference: string;
    idempotency_key: string;
  }) {
    if (!patientId) return;
    setAIBusy(true);
    setAIProviderError(null);
    setMutationError(null);
    try {
      const job = await api.submitAIProcessing(patientId, payload);
      setAIJob(job);
      if (job.status === "completed") {
        setPendingAIEntryId(job.entry_id);
        setRefreshToken((value) => value + 1);
        if (job.highlight_id) await openAIJobSource(job);
      }
    } catch (error) {
      setAIProviderError(displayError(error, t));
    } finally {
      setAIBusy(false);
    }
  }

  async function processVoice(sampleId: string) {
    if (!patientId) return;
    setVoiceBusy(true);
    setVoiceError(null);
    try {
      const session = await api.createVoiceSession(patientId, {
        sample_id: sampleId,
        idempotency_key: `ui-voice-${Date.now()}-${sampleId}`,
      });
      setVoiceSession(session);
      if (session.status === "completed" && session.highlight_id) {
        setPendingAIEntryId(session.entry_id);
        setRefreshToken((value) => value + 1);
        if (!session.patient_safe)
          await openHighlightSource(session.highlight_id);
      }
    } catch (error) {
      setVoiceError(displayError(error, t));
    } finally {
      setVoiceBusy(false);
    }
  }

  function closeSource() {
    setSource(null);
    setFocusEntryId(null);
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.delete("highlight");
    nextUrl.searchParams.set("patient", patientId);
    window.history.replaceState(
      {},
      "",
      `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`,
    );
  }

  async function loadHistory(entryId: string) {
    const [nextVersions, nextConflicts] = await Promise.all([
      api.versions(entryId),
      api.conflicts(entryId),
    ]);
    setHistoryEntryId(entryId);
    setVersions(nextVersions);
    setConflicts(nextConflicts);
    setDiff(null);
  }

  function openComments(entryId: string) {
    commentsReturnFocusRef.current =
      document.activeElement as HTMLElement | null;
    commentsEntryIdRef.current = entryId;
    const requestId = commentsRequestRef.current + 1;
    commentsRequestRef.current = requestId;
    setMutationError(null);
    setCommentsError(null);
    setCommentsEntryId(entryId);
    setComments([]);
    setReplyTo(null);
    setCommentBusy(true);
    void api
      .comments(entryId)
      .then((nextComments) => {
        if (commentsRequestRef.current === requestId) setComments(nextComments);
      })
      .catch((error) => {
        if (commentsRequestRef.current === requestId)
          setCommentsError(displayError(error, t));
      })
      .finally(() => {
        if (commentsRequestRef.current === requestId) setCommentBusy(false);
      });
  }

  function closeComments() {
    commentsEntryIdRef.current = null;
    setCommentsEntryId(null);
    setCommentsError(null);
    setReplyTo(null);
    window.setTimeout(() => commentsReturnFocusRef.current?.focus(), 0);
  }

  async function refreshComments() {
    if (!commentsEntryId) return;
    setComments(await api.comments(commentsEntryId));
  }

  async function submitComment(body: string, mentionedUserIds: string[]) {
    if (!commentsEntryId) return;
    setCommentBusy(true);
    try {
      await api.addComment(
        commentsEntryId,
        body,
        replyTo ?? undefined,
        mentionedUserIds,
      );
      setReplyTo(null);
      await refreshComments();
    } catch (error) {
      setCommentsError(displayError(error, t));
    } finally {
      setCommentBusy(false);
    }
  }

  function openTaskComposer(entryId: string | null, commentId: string | null) {
    taskReturnFocusRef.current = document.activeElement as HTMLElement | null;
    const entry = entryId ? timeline.find((item) => item.id === entryId) : null;
    setTaskError(null);
    setTaskFocusId(null);
    setTaskDrawerOpen(true);
    setTaskSource({
      entryId,
      commentId,
      label: entry
        ? `${t(entryTypeKeys[entry.entry_type] ?? "entryType.systemEvent")} v${entry.current_version}`
        : null,
    });
  }

  function openTaskDrawer(taskId: string | null = null) {
    taskReturnFocusRef.current = document.activeElement as HTMLElement | null;
    setTaskError(null);
    setTaskSource(null);
    setTaskFocusId(taskId);
    setTaskDrawerOpen(true);
  }

  function closeTaskDrawer() {
    setTaskDrawerOpen(false);
    setTaskSource(null);
    setTaskFocusId(null);
    setTaskError(null);
    window.setTimeout(() => taskReturnFocusRef.current?.focus(), 0);
  }

  async function refreshTasksAndGlance() {
    if (!patientId || !internal) return;
    const [nextTasks, nextGlance] = await Promise.all([
      api.tasks(patientId),
      api.glance(patientId),
    ]);
    setTasks(nextTasks);
    setGlance(nextGlance);
  }

  async function createTask(title: string, assigneeId: string) {
    if (!patientId) return;
    setTaskError(null);
    try {
      await api.createTask(patientId, {
        title,
        assigned_to_user_id: assigneeId,
        ...(taskSource?.entryId ? { source_entry_id: taskSource.entryId } : {}),
        ...(taskSource?.commentId
          ? { source_comment_id: taskSource.commentId }
          : {}),
      });
      await refreshTasksAndGlance();
      setTaskSource(null);
    } catch (error) {
      setTaskError(displayError(error, t));
      throw error;
    }
  }

  async function updateTask(
    task: Task,
    patch: {
      title?: string;
      assigned_to_user_id?: string;
      status?: TaskStatus;
    },
  ) {
    setTaskError(null);
    try {
      await api.updateTask(task.id, {
        expected_version: task.version,
        ...patch,
      });
      await refreshTasksAndGlance();
    } catch (error) {
      setTaskError(displayError(error, t));
      throw error;
    }
  }

  function focusTask(taskId: string) {
    openTaskDrawer(taskId);
  }

  async function resolveComment(comment: Comment) {
    setCommentBusy(true);
    try {
      await api.resolveComment(comment.id, !comment.is_resolved);
      await refreshComments();
    } catch (error) {
      setCommentsError(displayError(error, t));
    } finally {
      setCommentBusy(false);
    }
  }

  async function openHistory(entryId: string) {
    if (historyEntryId === entryId) {
      setHistoryEntryId(null);
      setVersions([]);
      setDiff(null);
      setConflicts([]);
      return;
    }
    setMutationError(null);
    try {
      await loadHistory(entryId);
    } catch (error) {
      setMutationError(displayError(error, t));
    }
  }

  async function openDiff(entry: TimelineEntry, version: number) {
    try {
      setDiff(await api.diff(entry.id, version, entry.current_version));
    } catch (error) {
      setMutationError(displayError(error, t));
    }
  }

  async function revert(entry: TimelineEntry, version: number) {
    setMutationBusy(true);
    setMutationError(null);
    try {
      await api.revert(entry.id, version, entry.current_version);
      setRefreshToken((value) => value + 1);
      if (historyEntryId === entry.id) await loadHistory(entry.id);
    } catch (error) {
      setMutationError(displayError(error, t));
      if (error instanceof ApiError && error.status === 409) {
        try {
          setRefreshToken((value) => value + 1);
          await loadHistory(entry.id);
        } catch (historyError) {
          setMutationError(displayError(historyError, t));
        }
      }
    } finally {
      setMutationBusy(false);
    }
  }

  async function saveEntry(entry: TimelineEntry) {
    if (!editingText.trim()) return;
    setMutationBusy(true);
    setMutationError(null);
    try {
      await api.updateEntry(
        entry.id,
        entry.current_version,
        editingText.trim(),
      );
      editingEntryIdRef.current = null;
      setEditingEntryId(null);
      setRemoteUpdatePending(false);
      setRefreshToken((value) => value + 1);
      if (historyEntryId === entry.id) await loadHistory(entry.id);
    } catch (error) {
      setMutationError(displayError(error, t));
      if (error instanceof ApiError && error.status === 409) {
        try {
          setRefreshToken((value) => value + 1);
          await loadHistory(entry.id);
        } catch (historyError) {
          setMutationError(displayError(historyError, t));
        }
      }
    } finally {
      setMutationBusy(false);
    }
  }

  async function review(item: GlanceItem, status: GlanceItem["status"]) {
    setMutationBusy(true);
    setMutationError(null);
    try {
      await api.reviewHighlight(item.id, status);
      setRefreshToken((value) => value + 1);
      if (source?.highlight.id === item.id) {
        setSource(null);
        window.history.replaceState({}, "", "?patient=" + patientId);
      }
    } catch (error) {
      setMutationError(displayError(error, t));
    } finally {
      setMutationBusy(false);
    }
  }

  async function sendFeedback(item: GlanceItem, eventType: FeedbackEventType) {
    setFeedbackBusyId(item.id);
    setMutationError(null);
    try {
      await api.feedback(
        item.id,
        eventType,
        `ui:${eventType}:${item.id}:${Date.now()}`,
      );
      setPinnedItems((current) => {
        const next = new Set(current);
        if (eventType === "pinned") next.add(item.id);
        if (eventType === "unpinned") next.delete(item.id);
        return next;
      });
      setRefreshToken((value) => value + 1);
    } catch (error) {
      setMutationError(displayError(error, t));
    } finally {
      setFeedbackBusyId(null);
    }
  }

  function openContextSource(entryId: string) {
    setSource(null);
    setFocusEntryId(entryId);
    window.history.replaceState({}, "", `?patient=${patientId}`);
    window.setTimeout(() => {
      scrollToElement(document.getElementById(`timeline-entry-${entryId}`));
    }, 0);
    window.setTimeout(() => setFocusEntryId(null), 2400);
  }

  async function refreshContext() {
    if (!patientId) return;
    setMutationBusy(true);
    setMutationError(null);
    try {
      await api.refreshContext(patientId);
      setContext(await api.context(patientId));
    } catch (error) {
      setMutationError(displayError(error, t));
    } finally {
      setMutationBusy(false);
    }
  }

  async function logout() {
    try {
      await api.logout();
    } finally {
      onLogout();
    }
  }

  return (
    <div className="min-h-screen bg-[#f4f7fb] text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4 px-5 py-4 lg:px-8">
          <div className="flex items-center gap-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-700 text-lg font-bold text-white">
              N
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
                {t("brand.gate")}
              </p>
              <h1 className="mt-1 text-xl font-semibold tracking-tight">
                {t("brand.name")}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-semibold text-slate-800">
                {user.display_name}
              </p>
              <p className="text-xs text-slate-500">
                {t("header.cookieSession", {
                  role: t(roleKeys[role] ?? "role.patient"),
                })}
              </p>
              {internal && (
                <p
                  className="text-[11px] text-slate-400"
                  data-testid="realtime-status"
                >
                  {t("realtime.label")}: {t(realtimeStatusKeys[realtimeStatus])}
                </p>
              )}
            </div>
            <div className="flex flex-wrap items-center justify-end gap-2">
              <LanguageToggle />
              {!isEmbeddedPreview && <DemoPreview />}
              <Button kind="quiet" onClick={() => setGuideOpen(true)}>
                {t("header.guide")}
              </Button>
              <Button kind="quiet" onClick={() => void logout()}>
                {t("header.signOut")}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1600px] gap-5 px-5 py-5 lg:grid-cols-[230px_minmax(0,1fr)_330px] lg:px-8">
        <aside className="space-y-4">
          <section className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              {t("patients.title")}
            </p>
            <label className="sr-only" htmlFor="patient-select">
              {t("patients.select")}
            </label>
            <select
              id="patient-select"
              aria-label={t("patients.select")}
              value={patientId}
              onChange={(event) => {
                const nextPatientId = event.target.value;
                setPatientId(nextPatientId);
                commentsEntryIdRef.current = null;
                editingEntryIdRef.current = null;
                setSource(null);
                setFocusEntryId(null);
                window.history.replaceState(
                  {},
                  "",
                  "?patient=" + nextPatientId,
                );
              }}
              className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-semibold outline-none focus:border-blue-500"
            >
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.synthetic_display_name}
                </option>
              ))}
            </select>
            {selectedPatient && (
              <p className="mt-3 text-xs leading-5 text-slate-500">
                {t("patients.scope")}
              </p>
            )}
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              {t("trust.title")}
            </p>
            <ul className="mt-3 space-y-3 text-sm leading-5 text-slate-600">
              <li>
                <span className="mr-2 text-emerald-600">●</span>
                {t("trust.immutable")}
              </li>
              <li>
                <span className="mr-2 text-amber-600">●</span>
                {t("trust.ai")}
              </li>
              <li>
                <span className="mr-2 text-blue-600">●</span>
                {t("trust.audit")}
              </li>
            </ul>
          </section>
        </aside>

        <section className="min-w-0 space-y-5">
          <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
                  {t("workspace.longitudinal")}
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                  {selectedPatient?.synthetic_display_name ??
                    t("timeline.loading")}
                </h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  {t("workspace.description")}
                </p>
              </div>
              <Pill tone={internal ? "blue" : "slate"}>
                {internal
                  ? t("workspace.internalView", {
                      role: t(roleKeys[role] ?? "role.patient"),
                    })
                  : t("workspace.patientView")}
              </Pill>
            </div>
          </section>

          {loadError && (
            <p
              className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700"
              role="alert"
            >
              {loadError}
            </p>
          )}
          {mutationError && (
            <p
              className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
              role="alert"
            >
              {mutationError}
            </p>
          )}
          {remoteUpdatePending && (
            <p
              className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900"
              role="status"
              aria-live="polite"
            >
              <span>{t("realtime.pending")}</span>
              <Button
                kind="secondary"
                disabled={editingEntryId !== null}
                onClick={() => {
                  setRemoteUpdatePending(false);
                  setRefreshToken((value) => value + 1);
                }}
              >
                {t("realtime.refresh")}
              </Button>
            </p>
          )}

          {voiceProviderInfo?.enabled &&
            patientId &&
            voiceSamples.length > 0 && (
              <VoicePanel
                providerInfo={voiceProviderInfo}
                samples={voiceSamples}
                session={voiceSession}
                busy={voiceBusy}
                error={voiceError}
                onProcess={processVoice}
                onOpenSource={openHighlightSource}
              />
            )}

          {canUseAIScribe && patientId && (
            <AIScribePanel
              providerInfo={aiProviderInfo}
              providerError={aiProviderError}
              job={aiJob}
              busy={aiBusy}
              onSubmit={submitAIScribe}
              onOpenSource={openAIJobSource}
            />
          )}

          {internal ? (
            <section
              className="rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-5 shadow-sm sm:p-7"
              aria-label={t("top.aria")}
              data-testid="top-card"
            >
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
                    {t("top.eyebrow")}
                  </p>
                  <h2 className="mt-2 text-xl font-semibold tracking-tight">
                    {t("top.title")}
                  </h2>
                </div>
                <p className="text-xs text-slate-500">
                  {t("top.count", { count: glance.length })}
                </p>
              </div>
              {glance.length === 0 ? (
                <p className="mt-5 rounded-2xl border border-dashed border-blue-200 bg-white/70 p-5 text-sm text-slate-500">
                  {t("top.empty")}
                </p>
              ) : (
                <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {glance.map((item) => (
                    <article
                      key={item.id}
                      data-testid="glance-item"
                      className="rounded-2xl border border-white bg-white p-4 shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex flex-wrap gap-2">
                          <Pill
                            tone={
                              item.status === "suggested" ||
                              item.status === "conflict_review"
                                ? "amber"
                                : "green"
                            }
                          >
                            {t(statusKeys[item.status] ?? "status.accepted")}
                          </Pill>
                          <Pill
                            tone={
                              item.item_kind === "action" ||
                              item.item_kind === "flag"
                                ? "amber"
                                : "slate"
                            }
                          >
                            {t(
                              itemKindKeys[item.item_kind] ??
                                "itemKind.information",
                            )}
                          </Pill>
                        </div>
                        <span className="text-xs font-semibold text-slate-400">
                          P{item.display_priority}
                        </span>
                      </div>
                      <p className="mt-3 text-sm font-semibold leading-6 text-slate-800">
                        {item.content_summary}
                      </p>
                      <p className="mt-2 text-xs leading-5 text-slate-500">
                        {item.risk_reason}
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2 text-xs">
                        <Pill tone={item.risk_level ? "red" : "slate"}>
                          {item.risk_level
                            ? t("top.explicitRisk", { risk: item.risk_level })
                            : t("top.noRisk")}
                        </Pill>
                        <span
                          className="rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 font-semibold text-blue-800"
                          data-testid="glance-action"
                        >
                          {t("top.action", {
                            label: item.action_label ?? t("top.noActionLabel"),
                            state: t(
                              actionStateKeys[item.action_state] ??
                                "actionState.notApplicable",
                            ),
                          })}
                        </span>
                      </div>
                      <details className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs">
                        <summary
                          className="cursor-pointer font-semibold text-slate-700"
                          data-testid="ranking-details"
                        >
                          {t("ranking.why")}{" "}
                          <span className="font-normal text-slate-500">
                            {t("ranking.disclaimer")}
                          </span>
                        </summary>
                        <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-slate-600">
                          <dt>{t("ranking.base")}</dt>
                          <dd className="text-right font-semibold">
                            {item.base_priority}
                          </dd>
                          <dt>{t("ranking.recency")}</dt>
                          <dd className="text-right font-semibold">
                            +{item.recency_contribution}
                          </dd>
                          <dt>{t("ranking.explicitRisk")}</dt>
                          <dd className="text-right font-semibold">
                            +{item.explicit_risk_contribution}
                          </dd>
                          <dt>{t("ranking.openAction")}</dt>
                          <dd className="text-right font-semibold">
                            +{item.unresolved_action_contribution}
                          </dd>
                          <dt>{t("ranking.confirmation")}</dt>
                          <dd className="text-right font-semibold">
                            +{item.clinician_confirmation_contribution}
                          </dd>
                          <dt>{t("ranking.adaptive")}</dt>
                          <dd className="text-right font-semibold">
                            {item.adaptive_feedback_adjustment >= 0 ? "+" : ""}
                            {item.adaptive_feedback_adjustment}
                          </dd>
                          <dt className="font-semibold text-slate-800">
                            {t("ranking.final")}
                          </dt>
                          <dd className="text-right font-bold text-blue-700">
                            {item.display_priority}
                          </dd>
                        </dl>
                      </details>
                      <p className="mt-3 text-xs font-semibold text-blue-700">
                        {t(
                          sourceLabelKeys[item.source_label] ??
                            "sourceKind.manual",
                        )}
                      </p>
                      {item.resource_type === "task" &&
                        item.assigned_to_display_name && (
                          <p className="mt-2 text-xs text-slate-500">
                            {t("task.assignedTo", {
                              name: item.assigned_to_display_name,
                            })}
                          </p>
                        )}
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.resource_type === "task" && item.task_id ? (
                          <Button
                            kind="secondary"
                            onClick={() => focusTask(item.task_id ?? "")}
                          >
                            {t("button.openTask")}
                          </Button>
                        ) : (
                          <Button
                            kind="secondary"
                            onClick={() => void openSource(item)}
                            disabled={sourceLoading}
                          >
                            {t("button.openSource")}
                          </Button>
                        )}
                        {role !== "admin" && (
                          <Button
                            kind="quiet"
                            onClick={() =>
                              void sendFeedback(
                                item,
                                pinnedItems.has(item.id)
                                  ? "unpinned"
                                  : "pinned",
                              )
                            }
                            disabled={feedbackBusyId === item.id}
                          >
                            {pinnedItems.has(item.id)
                              ? t("button.unpin")
                              : t("button.pin")}
                          </Button>
                        )}
                        {role === "clinician" &&
                          (item.status === "suggested" ||
                            item.status === "conflict_review") && (
                            <>
                              <Button
                                kind="primary"
                                onClick={() => void review(item, "accepted")}
                                disabled={mutationBusy}
                              >
                                {t("button.accept")}
                              </Button>
                              <Button
                                kind="danger"
                                onClick={() => void review(item, "rejected")}
                                disabled={mutationBusy}
                              >
                                {t("button.reject")}
                              </Button>
                            </>
                          )}
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>
          ) : (
            <section className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-7">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                {t("patient.privacy")}
              </p>
              <h2 className="mt-2 text-xl font-semibold">
                {t("patient.hiddenTitle")}
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                {t("patient.hiddenBody")}
              </p>
            </section>
          )}

          <HistoricalContextPanel
            context={context}
            internal={internal}
            timeline={timeline}
            onOpenSource={openContextSource}
            onRefresh={internal && role !== "admin" ? refreshContext : null}
            refreshBusy={mutationBusy}
          />

          <section
            className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"
            aria-label={t("timeline.aria")}
          >
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                  {t("timeline.title")}
                </p>
                <h2 className="mt-2 text-xl font-semibold">
                  {t("timeline.subtitle")}
                </h2>
              </div>
              {loading && <Pill tone="blue">{t("timeline.loading")}</Pill>}
            </div>
            {loading && timeline.length === 0 ? (
              <div
                className="mt-5 space-y-3"
                aria-label={t("timeline.loadingLabel")}
                aria-live="polite"
                role="status"
              >
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
              </div>
            ) : timeline.length === 0 ? (
              <p className="mt-5 rounded-2xl bg-slate-50 p-5 text-sm text-slate-500">
                {t("timeline.empty")}
              </p>
            ) : (
              <div className="relative mt-5 space-y-4 before:absolute before:bottom-3 before:left-3 before:top-3 before:w-px before:bg-slate-200">
                {timeline.map((entry) => {
                  const editable = internal && canEditEntry(user, entry);
                  const isFocused = focusEntryId === entry.id;
                  const isEditing = editingEntryId === entry.id;
                  return (
                    <article
                      key={entry.id}
                      id={`timeline-entry-${entry.id}`}
                      data-testid={`timeline-entry-${entry.id}`}
                      className={`relative ml-0 rounded-2xl border bg-white p-4 pl-8 transition sm:p-5 sm:pl-10 ${isFocused ? "border-amber-400 ring-4 ring-amber-100" : "border-slate-200"}`}
                    >
                      <span
                        className="absolute left-1.5 top-6 h-3 w-3 rounded-full border-2 border-white bg-blue-600 shadow"
                        aria-hidden="true"
                      />
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="font-semibold text-slate-900">
                              {t(
                                entryTypeKeys[entry.entry_type] ??
                                  "entryType.systemEvent",
                              )}
                            </h3>
                            {entry.entry_type.startsWith("ai_") && (
                              <Pill tone="amber">
                                Clinician review required
                              </Pill>
                            )}
                          </div>
                          <p className="mt-1 text-xs text-slate-500">
                            {formatDate(entry.occurred_at, locale)} ·{" "}
                            {t(
                              sourceKindKeys[entry.source_kind] ??
                                "sourceKind.system",
                            )}
                          </p>
                          <p className="mt-1 text-xs text-slate-400">
                            {t("timeline.authored", {
                              author: t(
                                roleKeys[entry.author_role] ?? "role.patient",
                              ),
                              owner: t(
                                roleKeys[entry.owner_role] ?? "role.patient",
                              ),
                            })}
                          </p>
                        </div>
                        <Pill>v{entry.current_version}</Pill>
                      </div>
                      {isEditing ? (
                        <div className="mt-4 space-y-2">
                          <textarea
                            aria-label={`${t("button.edit")} ${t(entryTypeKeys[entry.entry_type] ?? "entryType.systemEvent")}`}
                            value={editingText}
                            onChange={(event) =>
                              setEditingText(event.target.value)
                            }
                            className="min-h-24 w-full rounded-xl border border-blue-200 p-3 text-sm outline-none focus:ring-4 focus:ring-blue-100"
                          />
                          <div className="flex gap-2">
                            <Button
                              kind="primary"
                              onClick={() => void saveEntry(entry)}
                              disabled={mutationBusy}
                            >
                              {t("button.saveRevision")}
                            </Button>
                            <Button
                              kind="quiet"
                              onClick={() => {
                                editingEntryIdRef.current = null;
                                setEditingEntryId(null);
                                setRemoteUpdatePending(false);
                              }}
                            >
                              {t("button.cancel")}
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-700">
                          {entry.content}
                        </p>
                      )}
                      {source?.source_entry_id === entry.id && (
                        <ImmutableTimelineSource source={source} />
                      )}
                      <div className="mt-4 flex flex-wrap gap-2">
                        {internal && (
                          <Button
                            kind="secondary"
                            onClick={() => void openComments(entry.id)}
                            ariaExpanded={commentsEntryId === entry.id}
                            ariaControls="comments-drawer"
                          >
                            {t("button.comments")}
                          </Button>
                        )}
                        {internal && (
                          <Button
                            kind="secondary"
                            onClick={() => void openHistory(entry.id)}
                          >
                            {historyEntryId === entry.id
                              ? t("button.hideHistory")
                              : t("button.history")}
                          </Button>
                        )}
                        {internal && role !== "admin" && (
                          <Button
                            kind="secondary"
                            onClick={() => openTaskComposer(entry.id, null)}
                          >
                            {t("button.assignTask")}
                          </Button>
                        )}
                        {editable && !isEditing && (
                          <Button
                            kind="quiet"
                            onClick={() => {
                              editingEntryIdRef.current = entry.id;
                              setEditingEntryId(entry.id);
                              setEditingText(entry.content);
                            }}
                          >
                            {t("button.edit")}
                          </Button>
                        )}
                      </div>
                      {historyEntryId === entry.id && (
                        <HistoryPanel
                          entry={entry}
                          versions={versions}
                          diff={diff}
                          conflicts={conflicts}
                          canEdit={editable}
                          onDiff={(version) => void openDiff(entry, version)}
                          onRevert={(version) => void revert(entry, version)}
                        />
                      )}
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        </section>

        <aside className="space-y-5">
          <SourcePanel source={source} onClose={closeSource} />
          <section className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              {t("workspace.noteTitle")}
            </p>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              {t("workspace.noteBody")}
            </p>
          </section>
        </aside>
      </main>
      {selectedEntry && internal && (
        <ContextualDrawer
          open={commentsEntryId !== null}
          title={`${t(entryTypeKeys[selectedEntry.entry_type] ?? "entryType.systemEvent")} · ${t("comments.internal")}`}
          closeLabel={t("comments.close")}
          onClose={closeComments}
          initialFocusRef={commentsInputRef}
          testId="comments-drawer"
        >
          <CommentsPanel
            entry={selectedEntry}
            comments={comments}
            replyTo={replyTo}
            onReply={setReplyTo}
            onSubmit={submitComment}
            onResolve={resolveComment}
            mentionableUsers={collaborators}
            onAssignTask={(commentId) =>
              openTaskComposer(selectedEntry.id, commentId)
            }
            bodyRef={commentsInputRef}
            loading={commentBusy}
            error={commentsError}
            busy={commentBusy}
          />
        </ContextualDrawer>
      )}
      {internal && (
        <ContextualDrawer
          open={taskDrawerOpen}
          title={t("task.panel")}
          closeLabel={t("task.close")}
          onClose={closeTaskDrawer}
          initialFocusRef={taskTitleInputRef}
          testId="task-drawer"
        >
          <TaskPanel
            tasks={tasks}
            collaborators={collaborators}
            canEdit={role !== "admin"}
            sourceLabel={taskSource?.label ?? null}
            sourceComment={
              taskSource?.commentId
                ? (comments.find(
                    (comment) => comment.id === taskSource.commentId,
                  )?.body ?? null)
                : null
            }
            onCreate={createTask}
            onUpdate={updateTask}
            onCloseComposer={() => setTaskSource(null)}
            titleInputRef={taskTitleInputRef}
            error={taskError}
            focusedTaskId={taskFocusId}
          />
        </ContextualDrawer>
      )}
      <LearningGuide open={guideOpen} onClose={() => setGuideOpen(false)} />
    </div>
  );
}

function AppContent() {
  const { t } = useI18n();
  const [user, setUser] = useState<Me | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [sessionError, setSessionError] = useState<string | null>(null);

  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch((error) => {
        if (!(error instanceof ApiError && error.status === 401))
          setSessionError(displayError(error, t));
      })
      .finally(() => setCheckingSession(false));
  }, []);

  if (checkingSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f4f7fb] text-sm text-slate-500">
        {t("app.checking")}
      </main>
    );
  }
  if (user) return <Workspace user={user} onLogout={() => setUser(null)} />;
  return <LoginScreen onLogin={setUser} initialError={sessionError} />;
}

export function App() {
  return (
    <I18nProvider>
      <AppContent />
    </I18nProvider>
  );
}
