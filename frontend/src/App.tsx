import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";

import { ApiError, api } from "./api";
import type {
  Comment,
  PatientContext,
  Conflict,
  Diff,
  FeedbackEventType,
  GlanceItem,
  Me,
  Patient,
  ProvenanceSource,
  TimelineEntry,
  Version,
} from "./types";

const sourceKindLabels: Record<string, string> = {
  doctor_consult: "AI-scribed · Doctor consult",
  nurse_consult: "AI-scribed · Nurse consult",
  patient_ai_session: "AI-scribed · Patient session",
  system_event: "System event",
  manual: "Manual note",
};

const entryTypeLabels: Record<string, string> = {
  patient_facing_summary: "Patient summary",
  patient_instruction: "Patient instruction",
  staff_note: "Staff note",
  clinician_section: "Clinician section",
  ai_doctor_consult_summary: "Doctor consult summary",
  ai_nurse_consult_summary: "Nurse consult summary",
  ai_patient_session_summary: "Patient session summary",
  system_event: "System event",
};

const statusLabels: Record<string, string> = {
  suggested: "Suggested",
  accepted: "Accepted",
  rejected: "Rejected",
  superseded: "Superseded",
  conflict_review: "Conflict review",
};

const itemKindLabels: Record<string, string> = {
  information: "Information",
  action: "Open action",
  flag: "Flag",
};

const actionStateLabels: Record<string, string> = {
  open: "Open",
  completed: "Completed",
  not_applicable: "No action state",
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-SG", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function displayError(error: unknown) {
  if (error instanceof ApiError) {
    if (
      typeof error.body.detail === "object" &&
      error.body.detail?.actual_version
    ) {
      return `${error.message}. Current version is ${error.body.detail.actual_version}; reload the history before retrying.`;
    }
    return error.message;
  }
  return error instanceof Error
    ? error.message
    : "The request could not be completed.";
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
  const result = exactCodepointSpan(text, quote, startOffset, endOffset);
  if (!result.valid) {
    return (
      <div>
        <p
          className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs leading-5 text-rose-800"
          role="alert"
          data-testid="provenance-integrity-warning"
        >
          Integrity warning: {result.reason} No approximate text match was
          highlighted.
        </p>
        <p className="mt-3 whitespace-pre-wrap">{text}</p>
      </div>
    );
  }
  return (
    <>
      {result.before}
      <mark
        className="rounded bg-amber-100 px-1 text-amber-950"
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
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  kind?: "primary" | "secondary" | "quiet" | "danger";
  type?: "button" | "submit";
  ariaLabel?: string;
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
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className={`rounded-lg border px-3 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[kind]}`}
    >
      {children}
    </button>
  );
}

function LoginScreen({
  onLogin,
  initialError,
}: {
  onLogin: (user: Me) => void;
  initialError?: string | null;
}) {
  const [email, setEmail] = useState("staff.a@clinic-a.test");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(initialError ?? null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await api.login(email, password);
      onLogin(result.user);
    } catch (requestError) {
      setError(displayError(requestError));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f4f7fb] px-5 py-10 text-slate-900">
      <section className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50">
        <div className="mb-8">
          <p className="text-xs font-bold uppercase tracking-[0.28em] text-blue-700">
            Nightingale · Gate B
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight">
            Shared Care Note
          </h1>
          <p className="mt-3 text-sm leading-6 text-slate-500">
            Sign in to review synthetic longitudinal care records. Every
            AI-scribed item remains a suggestion until a clinician reviews it.
          </p>
        </div>
        <form className="space-y-4" onSubmit={submit}>
          <label className="block text-sm font-semibold text-slate-700">
            Email
            <input
              aria-label="Email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 font-normal outline-none ring-blue-200 transition focus:border-blue-500 focus:ring-4"
              type="email"
              autoComplete="username"
              required
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Password
            <input
              aria-label="Password"
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
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </form>
        <div className="mt-8 border-t border-slate-100 pt-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
            Synthetic demo personas
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              ["staff.a@clinic-a.test", "Staff"],
              ["clinician.a@clinic-a.test", "Clinician"],
              ["sarah.patient@clinic-a.test", "Patient"],
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
            Persona buttons select the synthetic email only; password is never
            embedded in the UI.
          </p>
        </div>
      </section>
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
  if (!source) {
    return (
      <section
        className="rounded-2xl border border-slate-200 bg-white p-5"
        aria-label="Source navigation"
      >
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
          Source navigation
        </p>
        <h2 className="mt-2 text-lg font-semibold text-slate-800">
          Choose a Glance item
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          The exact immutable quote, version and source reference will appear
          here when you click a card.
        </p>
      </section>
    );
  }
  return (
    <section
      className="rounded-2xl border border-blue-200 bg-blue-50/60 p-5"
      aria-label="Immutable source"
      data-source-entry-id={source.source_entry_id}
      data-source-version-id={source.source_version_id}
      data-source-version={source.version_number}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">
            Immutable source
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-900">
            {entryTypeLabels[source.entry_type] ?? source.entry_type}
          </h2>
        </div>
        <div className="flex items-start gap-2">
          <Pill tone="blue">v{source.version_number}</Pill>
          <Button kind="quiet" onClick={onClose}>
            Close source
          </Button>
        </div>
      </div>
      {source.version_number !== source.current_entry_version && (
        <p
          className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-900"
          data-testid="immutable-version-warning"
        >
          This highlight is anchored to immutable version v
          {source.version_number}; current entry is v
          {source.current_entry_version}.
        </p>
      )}
      <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
        <div>
          <dt className="text-slate-500">Occurred</dt>
          <dd className="mt-1 font-semibold text-slate-800">
            {formatDate(source.occurred_at)}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">Offset unit</dt>
          <dd className="mt-1 font-semibold text-slate-800">
            Python code point
          </dd>
        </div>
        <div className="col-span-2">
          <dt className="text-slate-500">Source reference</dt>
          <dd className="mt-1 break-words font-mono text-slate-800">
            {source.source_reference ?? "—"}
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
        Exact span: [{source.start_offset}, {source.end_offset}) · SHA-256 is
        stored with the highlight.
      </p>
    </section>
  );
}

function ImmutableTimelineSource({ source }: { source: ProvenanceSource }) {
  return (
    <section
      className="mt-4 rounded-xl border border-amber-200 bg-amber-50/70 p-4"
      aria-label="Immutable timeline source"
      data-testid="immutable-timeline-source"
      data-source-entry-id={source.source_entry_id}
      data-source-version={source.version_number}
    >
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-amber-800">
        Immutable source span
      </p>
      <p className="mt-2 text-xs leading-5 text-amber-900">
        Anchored to immutable version v{source.version_number}; current entry is
        v{source.current_entry_version}.
      </p>
      <div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-800">
        <ExactSpanView
          text={source.version_content}
          quote={source.quote}
          startOffset={source.start_offset}
          endOffset={source.end_offset}
        />
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
  busy,
}: {
  comment: Comment;
  childrenByParent: Map<string, Comment[]>;
  depth: number;
  visited: Set<string>;
  onReply: (id: string | null) => void;
  onResolve: (comment: Comment) => Promise<void>;
  busy: boolean;
}) {
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
          {formatDate(comment.created_at)}
        </span>
        <Pill tone={comment.is_resolved ? "green" : "slate"}>
          {comment.is_resolved ? "Resolved" : "Open"}
        </Pill>
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-700">{comment.body}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button kind="quiet" onClick={() => onReply(comment.id)}>
          Reply
        </Button>
        <Button
          kind="quiet"
          onClick={() => void onResolve(comment)}
          disabled={busy}
        >
          {comment.is_resolved ? "Unresolve" : "Resolve"}
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
  onClose,
  busy,
}: {
  entry: TimelineEntry;
  comments: Comment[];
  replyTo: string | null;
  onReply: (id: string | null) => void;
  onSubmit: (body: string) => Promise<void>;
  onResolve: (comment: Comment) => Promise<void>;
  onClose: () => void;
  busy: boolean;
}) {
  const [body, setBody] = useState("");
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
    await onSubmit(body.trim());
    setBody("");
  }

  return (
    <section
      className="rounded-2xl border border-slate-200 bg-white p-5"
      aria-label="Comments"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
            Internal discussion
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-900">
            {entryTypeLabels[entry.entry_type] ?? entry.entry_type}
          </h2>
        </div>
        <Button kind="quiet" onClick={onClose} ariaLabel="Close comments">
          Close
        </Button>
      </div>
      <div className="mt-4 space-y-3">
        {comments.length === 0 && (
          <p className="rounded-xl bg-slate-50 p-3 text-sm text-slate-500">
            No comments yet.
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
            Replying to a comment{" "}
            <button
              className="underline"
              type="button"
              onClick={() => onReply(null)}
            >
              cancel
            </button>
          </p>
        )}
        <textarea
          aria-label="Comment body"
          value={body}
          onChange={(event) => setBody(event.target.value)}
          placeholder="Add an internal follow-up…"
          className="min-h-24 w-full resize-y rounded-xl border border-slate-200 p-3 text-sm outline-none ring-blue-200 focus:border-blue-500 focus:ring-4"
        />
        <Button type="submit" kind="primary" disabled={busy || !body.trim()}>
          Add comment
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
  return (
    <section
      className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4"
      aria-label="Revision history"
    >
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold text-slate-800">Revision history</h3>
        <Pill>Current v{entry.current_version}</Pill>
      </div>
      <div className="mt-3 space-y-2">
        {versions.map((version) => (
          <div
            key={version.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-white p-2 text-xs"
          >
            <span className="font-semibold text-slate-700">
              v{version.version_number} · {version.created_by_role}
            </span>
            <span className="text-slate-400">
              {formatDate(version.created_at)}
            </span>
            <div className="flex gap-1">
              {version.version_number !== entry.current_version && (
                <Button
                  kind="quiet"
                  onClick={() => onDiff(version.version_number)}
                >
                  Compare
                </Button>
              )}
              {canEdit && version.version_number !== entry.current_version && (
                <Button
                  kind="quiet"
                  onClick={() => onRevert(version.version_number)}
                >
                  Revert
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
      {diff && (
        <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-950">
          <p className="font-bold">
            Diff v{diff.from_version} → v{diff.to_version}
          </p>
          <p className="mt-2">
            <span className="font-semibold">Before:</span> {diff.from_content}
          </p>
          <p className="mt-1">
            <span className="font-semibold">After:</span> {diff.to_content}
          </p>
        </div>
      )}
      {conflicts.length > 0 && (
        <section
          className="mt-3 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs leading-5 text-rose-950"
          aria-label="Optimistic concurrency conflicts"
          data-testid="conflict-panel"
        >
          <p className="font-bold">Optimistic concurrency conflict</p>
          <p className="mt-1">
            A stale write was preserved for human review. This is a revision
            conflict, not a clinical semantic decision.
          </p>
          <div className="mt-3 space-y-3">
            {conflicts.map((conflict) => (
              <article
                key={conflict.id}
                className="rounded-lg border border-rose-200 bg-white p-3"
                data-testid={"conflict-" + conflict.id}
              >
                <p className="font-semibold">
                  Expected v{conflict.expected_version}; actual v
                  {conflict.actual_version}
                </p>
                <p className="mt-2">
                  <span className="font-semibold">Current content:</span>{" "}
                  {entry.content}
                </p>
                <p className="mt-1">
                  <span className="font-semibold">
                    Preserved attempted content:
                  </span>{" "}
                  {conflict.attempted_content}
                </p>
                <p className="mt-2 text-rose-700">
                  Status: {conflict.status}; no silent last-write-wins.
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
  onOpenSource,
  onRefresh,
  refreshBusy,
}: {
  context: PatientContext | null;
  internal: boolean;
  onOpenSource: (entryId: string) => void;
  onRefresh: (() => Promise<void>) | null;
  refreshBusy: boolean;
}) {
  if (!context) return null;
  return (
    <section
      className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"
      aria-label="Historical context"
      data-testid="historical-context"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
            Historical context
          </p>
          <h2 className="mt-2 text-xl font-semibold">
            Hot, warm, and derived cold history
          </h2>
        </div>
        {onRefresh && (
          <Button
            kind="quiet"
            onClick={() => void onRefresh()}
            disabled={refreshBusy}
          >
            {refreshBusy ? "Refreshing" : "Refresh derived context"}
          </Button>
        )}
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
          <p className="text-xs font-bold uppercase tracking-[0.15em] text-blue-700">
            Hot context
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {context.hot_entries.length} canonical entries remain available with
            full detail for this scope.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase tracking-[0.15em] text-slate-500">
            Warm index
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {context.warm_entries.length} older entries remain discoverable by
            metadata without moving content into the cold summary.
          </p>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {context.archival_summaries.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
            No derived archival periods are available yet.
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
                  {new Intl.DateTimeFormat("en-SG", {
                    month: "long",
                    year: "numeric",
                  }).format(new Date(summary.period_start))}
                </p>
                <Pill tone="amber">Derived summary · not canonical source</Pill>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {summary.summary_text}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                {summary.source_count} source pointer
                {summary.source_count === 1 ? "" : "s"} · policy{" "}
                {summary.policy_version}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {summary.sources.map((source) => (
                  <Button
                    key={`${summary.id}-${source.source_entry_id}-${source.source_version_id}`}
                    kind="secondary"
                    onClick={() => onOpenSource(source.source_entry_id)}
                  >
                    Open canonical source
                  </Button>
                ))}
              </div>
              {!internal && (
                <p className="mt-3 text-xs text-slate-500">
                  Only patient-facing source pointers are included in this view.
                </p>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function Workspace({ user, onLogout }: { user: Me; onLogout: () => void }) {
  const internal = isInternalUser(user);
  const role = primaryRole(user);
  const [patients, setPatients] = useState<Patient[]>([]);
  const queryParams = new URLSearchParams(window.location.search);
  const [patientId, setPatientId] = useState(
    queryParams.get("patient") ?? user.patient_ids[0] ?? "",
  );
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [glance, setGlance] = useState<GlanceItem[]>([]);
  const [context, setContext] = useState<PatientContext | null>(null);
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
  const [historyEntryId, setHistoryEntryId] = useState<string | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [diff, setDiff] = useState<Diff | null>(null);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [editingEntryId, setEditingEntryId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState("");
  const [mutationError, setMutationError] = useState<string | null>(null);
  const [mutationBusy, setMutationBusy] = useState(false);
  const [feedbackBusyId, setFeedbackBusyId] = useState<string | null>(null);
  const [pinnedItems, setPinnedItems] = useState<Set<string>>(new Set());

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
      .catch((error) => active && setLoadError(displayError(error)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [user.id]);

  useEffect(() => {
    if (!patientId) return;
    let active = true;
    setLoading(true);
    setLoadError(null);
    setSource(null);
    setContext(null);
    setSourceLoading(false);
    setFocusEntryId(null);
    setCommentsEntryId(null);
    const requestedHighlightId = new URLSearchParams(
      window.location.search,
    ).get("highlight");
    const glanceRequest = internal
      ? api.glance(patientId)
      : Promise.resolve([] as GlanceItem[]);
    Promise.all([
      api.timeline(patientId),
      glanceRequest,
      api.context(patientId),
    ])
      .then(async ([timelineResult, glanceResult, contextResult]) => {
        if (!active) return;
        setTimeline(timelineResult);
        setGlance(glanceResult);
        setContext(contextResult);
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
              document
                .getElementById(
                  "timeline-entry-" + linkedSource.source_entry_id,
                )
                ?.scrollIntoView?.({ behavior: "smooth", block: "center" });
            }, 0);
            window.setTimeout(() => setFocusEntryId(null), 2400);
          }
          if (active) setSourceLoading(false);
        }
      })
      .catch((error) => active && setLoadError(displayError(error)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [patientId, internal, refreshToken]);

  useEffect(() => {
    setPinnedItems(new Set());
  }, [patientId]);

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
        const timelineEntry = document.getElementById(
          `timeline-entry-${result.source_entry_id}`,
        );
        timelineEntry?.scrollIntoView?.({
          behavior: "smooth",
          block: "center",
        });
      }, 0);
      window.setTimeout(() => setFocusEntryId(null), 2400);
    } catch (error) {
      setMutationError(displayError(error));
    } finally {
      setSourceLoading(false);
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

  async function openComments(entryId: string) {
    setMutationError(null);
    setCommentBusy(true);
    try {
      setComments(await api.comments(entryId));
      setCommentsEntryId(entryId);
      setReplyTo(null);
    } catch (error) {
      setMutationError(displayError(error));
    } finally {
      setCommentBusy(false);
    }
  }

  async function refreshComments() {
    if (!commentsEntryId) return;
    setComments(await api.comments(commentsEntryId));
  }

  async function submitComment(body: string) {
    if (!commentsEntryId) return;
    setCommentBusy(true);
    try {
      await api.addComment(commentsEntryId, body, replyTo ?? undefined);
      setReplyTo(null);
      await refreshComments();
    } catch (error) {
      setMutationError(displayError(error));
    } finally {
      setCommentBusy(false);
    }
  }

  async function resolveComment(comment: Comment) {
    setCommentBusy(true);
    try {
      await api.resolveComment(comment.id, !comment.is_resolved);
      await refreshComments();
    } catch (error) {
      setMutationError(displayError(error));
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
      setMutationError(displayError(error));
    }
  }

  async function openDiff(entry: TimelineEntry, version: number) {
    try {
      setDiff(await api.diff(entry.id, version, entry.current_version));
    } catch (error) {
      setMutationError(displayError(error));
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
      setMutationError(displayError(error));
      if (error instanceof ApiError && error.status === 409) {
        try {
          setRefreshToken((value) => value + 1);
          await loadHistory(entry.id);
        } catch (historyError) {
          setMutationError(displayError(historyError));
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
      setEditingEntryId(null);
      setRefreshToken((value) => value + 1);
      if (historyEntryId === entry.id) await loadHistory(entry.id);
    } catch (error) {
      setMutationError(displayError(error));
      if (error instanceof ApiError && error.status === 409) {
        try {
          setRefreshToken((value) => value + 1);
          await loadHistory(entry.id);
        } catch (historyError) {
          setMutationError(displayError(historyError));
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
      setMutationError(displayError(error));
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
      setMutationError(displayError(error));
    } finally {
      setFeedbackBusyId(null);
    }
  }

  function openContextSource(entryId: string) {
    setSource(null);
    setFocusEntryId(entryId);
    window.history.replaceState({}, "", `?patient=${patientId}`);
    window.setTimeout(() => {
      document
        .getElementById(`timeline-entry-${entryId}`)
        ?.scrollIntoView?.({ behavior: "smooth", block: "center" });
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
      setMutationError(displayError(error));
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
                Nightingale · Gate B
              </p>
              <h1 className="mt-1 text-xl font-semibold tracking-tight">
                Shared Care Note
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-semibold text-slate-800">
                {user.display_name}
              </p>
              <p className="text-xs text-slate-500">{role} · cookie session</p>
            </div>
            <Button kind="quiet" onClick={() => void logout()}>
              Sign out
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1600px] gap-5 px-5 py-5 lg:grid-cols-[230px_minmax(0,1fr)_330px] lg:px-8">
        <aside className="space-y-4">
          <section className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              Patients
            </p>
            <label className="sr-only" htmlFor="patient-select">
              Select patient
            </label>
            <select
              id="patient-select"
              aria-label="Select patient"
              value={patientId}
              onChange={(event) => {
                const nextPatientId = event.target.value;
                setPatientId(nextPatientId);
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
                Synthetic patient · clinic scope verified server-side.
              </p>
            )}
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              Trust boundary
            </p>
            <ul className="mt-3 space-y-3 text-sm leading-5 text-slate-600">
              <li>
                <span className="mr-2 text-emerald-600">●</span>Source versions
                are immutable.
              </li>
              <li>
                <span className="mr-2 text-amber-600">●</span>AI output stays
                suggested until review.
              </li>
              <li>
                <span className="mr-2 text-blue-600">●</span>Clinician actions
                are audited as metadata.
              </li>
            </ul>
          </section>
        </aside>

        <section className="min-w-0 space-y-5">
          <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
                  Longitudinal workspace
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                  {selectedPatient?.synthetic_display_name ?? "Loading patient"}
                </h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  A calm, source-linked view of what changed, what needs
                  attention, and which suggestions still require clinical trust
                  review.
                </p>
              </div>
              <Pill tone={internal ? "blue" : "slate"}>
                {internal ? `${role} view` : "Patient view"}
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

          {internal ? (
            <section
              className="rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-5 shadow-sm sm:p-7"
              aria-label="Top Card"
              data-testid="top-card"
            >
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
                    Top Card · Glance View
                  </p>
                  <h2 className="mt-2 text-xl font-semibold tracking-tight">
                    What needs attention now
                  </h2>
                </div>
                <p className="text-xs text-slate-500">
                  {glance.length} active source-linked items · max 6
                </p>
              </div>
              {glance.length === 0 ? (
                <p className="mt-5 rounded-2xl border border-dashed border-blue-200 bg-white/70 p-5 text-sm text-slate-500">
                  No active highlights. Suggestions that were rejected or
                  superseded stay out of this view but remain in source history.
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
                            {statusLabels[item.status]}
                          </Pill>
                          <Pill
                            tone={
                              item.item_kind === "action" ||
                              item.item_kind === "flag"
                                ? "amber"
                                : "slate"
                            }
                          >
                            {itemKindLabels[item.item_kind]}
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
                            ? `Explicit risk: ${item.risk_level}`
                            : "No explicit risk tag"}
                        </Pill>
                        <span
                          className="rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 font-semibold text-blue-800"
                          data-testid="glance-action"
                        >
                          Action: {item.action_label ?? "No action label"} ·{" "}
                          {actionStateLabels[item.action_state] ??
                            item.action_state}
                        </span>
                      </div>
                      <details className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs">
                        <summary
                          className="cursor-pointer font-semibold text-slate-700"
                          data-testid="ranking-details"
                        >
                          Why ranked?{" "}
                          <span className="font-normal text-slate-500">
                            Ranking priority, not a medical risk score.
                          </span>
                        </summary>
                        <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-slate-600">
                          <dt>Base</dt>
                          <dd className="text-right font-semibold">
                            {item.base_priority}
                          </dd>
                          <dt>Recency</dt>
                          <dd className="text-right font-semibold">
                            +{item.recency_contribution}
                          </dd>
                          <dt>Explicit risk</dt>
                          <dd className="text-right font-semibold">
                            +{item.explicit_risk_contribution}
                          </dd>
                          <dt>Open action</dt>
                          <dd className="text-right font-semibold">
                            +{item.unresolved_action_contribution}
                          </dd>
                          <dt>Clinician confirmation</dt>
                          <dd className="text-right font-semibold">
                            +{item.clinician_confirmation_contribution}
                          </dd>
                          <dt>Adaptive feedback</dt>
                          <dd className="text-right font-semibold">
                            {item.adaptive_feedback_adjustment >= 0 ? "+" : ""}
                            {item.adaptive_feedback_adjustment}
                          </dd>
                          <dt className="font-semibold text-slate-800">
                            Final priority
                          </dt>
                          <dd className="text-right font-bold text-blue-700">
                            {item.display_priority}
                          </dd>
                        </dl>
                      </details>
                      <p className="mt-3 text-xs font-semibold text-blue-700">
                        {item.source_label}
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <Button
                          kind="secondary"
                          onClick={() => void openSource(item)}
                          disabled={sourceLoading}
                        >
                          Open source
                        </Button>
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
                            {pinnedItems.has(item.id) ? "Unpin" : "Pin"}
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
                                Accept
                              </Button>
                              <Button
                                kind="danger"
                                onClick={() => void review(item, "rejected")}
                                disabled={mutationBusy}
                              >
                                Reject
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
                Patient privacy
              </p>
              <h2 className="mt-2 text-xl font-semibold">
                Internal Glance View is hidden
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                This session receives patient-facing summaries and instructions
                only. Internal comments, raw AI notes and review states are not
                returned by the server.
              </p>
            </section>
          )}

          <HistoricalContextPanel
            context={context}
            internal={internal}
            onOpenSource={openContextSource}
            onRefresh={internal && role !== "admin" ? refreshContext : null}
            refreshBusy={mutationBusy}
          />

          <section
            className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"
            aria-label="Timeline"
          >
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                  Longitudinal timeline
                </p>
                <h2 className="mt-2 text-xl font-semibold">
                  Occurred time, source, and revision state
                </h2>
              </div>
              {loading && <Pill tone="blue">Loading</Pill>}
            </div>
            {loading && timeline.length === 0 ? (
              <div className="mt-5 space-y-3" aria-label="Loading timeline">
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
              </div>
            ) : timeline.length === 0 ? (
              <p className="mt-5 rounded-2xl bg-slate-50 p-5 text-sm text-slate-500">
                No timeline entries are available for this scope.
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
                              {entryTypeLabels[entry.entry_type] ??
                                entry.entry_type}
                            </h3>
                            {entry.entry_type.startsWith("ai_") && (
                              <Pill tone="amber">
                                Clinician review required
                              </Pill>
                            )}
                          </div>
                          <p className="mt-1 text-xs text-slate-500">
                            {formatDate(entry.occurred_at)} ·{" "}
                            {sourceKindLabels[entry.source_kind] ??
                              entry.source_kind}
                          </p>
                          <p className="mt-1 text-xs text-slate-400">
                            Authored by {entry.author_role} · owner{" "}
                            {entry.owner_role}
                          </p>
                        </div>
                        <Pill>v{entry.current_version}</Pill>
                      </div>
                      {isEditing ? (
                        <div className="mt-4 space-y-2">
                          <textarea
                            aria-label={`Edit ${entryTypeLabels[entry.entry_type] ?? entry.entry_type}`}
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
                              Save revision
                            </Button>
                            <Button
                              kind="quiet"
                              onClick={() => setEditingEntryId(null)}
                            >
                              Cancel
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
                            disabled={commentBusy}
                          >
                            Comments
                          </Button>
                        )}
                        {internal && (
                          <Button
                            kind="secondary"
                            onClick={() => void openHistory(entry.id)}
                          >
                            {historyEntryId === entry.id
                              ? "Hide history"
                              : "History"}
                          </Button>
                        )}
                        {editable && !isEditing && (
                          <Button
                            kind="quiet"
                            onClick={() => {
                              setEditingEntryId(entry.id);
                              setEditingText(entry.content);
                            }}
                          >
                            Edit
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
          {selectedEntry && internal && (
            <CommentsPanel
              entry={selectedEntry}
              comments={comments}
              replyTo={replyTo}
              onReply={setReplyTo}
              onSubmit={submitComment}
              onResolve={resolveComment}
              onClose={() => setCommentsEntryId(null)}
              busy={commentBusy}
            />
          )}
          <section className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              Workspace note
            </p>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Nightingale stores source identity, version and review metadata
              separately from clinical truth. A conflict state is a prompt for
              human review, not an automatic diagnosis.
            </p>
          </section>
        </aside>
      </main>
    </div>
  );
}

export function App() {
  const [user, setUser] = useState<Me | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [sessionError, setSessionError] = useState<string | null>(null);

  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch((error) => {
        if (!(error instanceof ApiError && error.status === 401))
          setSessionError(displayError(error));
      })
      .finally(() => setCheckingSession(false));
  }, []);

  if (checkingSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f4f7fb] text-sm text-slate-500">
        Checking secure session…
      </main>
    );
  }
  if (user) return <Workspace user={user} onLogout={() => setUser(null)} />;
  return <LoginScreen onLogin={setUser} initialError={sessionError} />;
}
