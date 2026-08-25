import { useQuery } from "@tanstack/react-query";

type HealthStatus = {
  status: string;
  phase: string;
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${apiBaseUrl}/health`);
  if (!response.ok) {
    throw new Error(`Backend returned HTTP ${response.status}`);
  }
  return (await response.json()) as HealthStatus;
}

export function App() {
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
  });

  const backendLabel = healthQuery.isPending
    ? "Checking backend…"
    : healthQuery.isError
      ? "Backend unavailable"
      : "Backend online";

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl flex-col justify-between gap-12">
        <header className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-300">
              Clinic collaboration scaffold
            </p>
            <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">Nightingale</h1>
            <p className="mt-4 max-w-xl text-base leading-7 text-slate-300 sm:text-lg">
              A trust-centered longitudinal care-note project. Phase 0 establishes the
              reproducible application shell only.
            </p>
          </div>
          <span className="w-fit rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-sm font-medium text-cyan-200">
            Phase 0 · scaffold
          </span>
        </header>

        <section className="grid gap-4 sm:grid-cols-2" aria-label="Phase 0 status">
          <article className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl shadow-cyan-950/20">
            <p className="text-sm font-medium text-slate-400">Current boundary</p>
            <h2 className="mt-3 text-xl font-semibold">Foundation before features</h2>
            <p className="mt-3 text-sm leading-6 text-slate-400">
              Authentication, RBAC, timeline, AI processing, provenance, and bonus capabilities
              are intentionally deferred to later gates.
            </p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl shadow-cyan-950/20">
            <p className="text-sm font-medium text-slate-400">Backend health</p>
            <div className="mt-3 flex items-center gap-3">
              <span
                className={`h-3 w-3 rounded-full ${healthQuery.isError ? "bg-rose-400" : healthQuery.isPending ? "bg-amber-300" : "bg-emerald-400"}`}
                aria-hidden="true"
              />
              <h2 className="text-xl font-semibold" aria-live="polite">
                {backendLabel}
              </h2>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-400">
              {healthQuery.data
                ? `GET /health · ${healthQuery.data.status} · ${healthQuery.data.phase}`
                : "Start the FastAPI process on port 8000 to verify the connection."}
            </p>
          </article>
        </section>

        <footer className="border-t border-slate-800 pt-5 text-sm text-slate-500">
          Synthetic data only · No clinical workflow is implemented in this phase.
        </footer>
      </div>
    </main>
  );
}

