import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/App";

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

describe("Phase 0 shell", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok", phase: "0-scaffold" }),
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the project identity and real backend health state", async () => {
    renderApp();

    expect(screen.getByRole("heading", { name: "Nightingale" })).toBeInTheDocument();
    expect(screen.getByText("Phase 0 · scaffold")).toBeInTheDocument();
    expect(await screen.findByText("Backend online")).toBeInTheDocument();
    expect(screen.getByText("GET /health · ok · 0-scaffold")).toBeInTheDocument();
  });
});

