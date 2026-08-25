import { execFileSync, spawn, type ChildProcess } from "node:child_process";
import { randomBytes } from "node:crypto";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const e2eRoot = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(e2eRoot, "..", "..");
const repositoryRoot = path.resolve(frontendRoot, "..");
const backendRoot = path.join(repositoryRoot, "backend");
const databasePath = path.join(
  repositoryRoot,
  ".uv-cache",
  "gate-b-e2e.sqlite",
);
const passwordPath = path.join(
  frontendRoot,
  "test-results",
  "gate-b",
  "e2e-password.txt",
);
const serverPidPath = path.join(
  frontendRoot,
  "test-results",
  "gate-b",
  "server-pids.json",
);
const pythonExecutable =
  "C:\\Users\\JI YANCHEN\\Desktop\\ai_trading_playground\\ai_env\\python.exe";
const databaseUrl = `sqlite:///${databasePath.replaceAll("\\", "/")}`;
const viteScript = path.join(
  frontendRoot,
  "node_modules",
  "vite",
  "bin",
  "vite.js",
);

async function waitForUrl(url: string, child: ChildProcess) {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) {
      throw new Error(`E2E server exited before becoming ready: ${url}`);
    }
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch {
      // The server is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`Timed out waiting for E2E server: ${url}`);
}

export default async function globalSetup() {
  const password =
    process.env.E2E_DEMO_PASSWORD ?? randomBytes(18).toString("base64url");
  const environment = {
    ...process.env,
    APP_ENV: "test",
    DATABASE_URL: databaseUrl,
    DEMO_SEED_PASSWORD: password,
    SESSION_SECRET: "gate-b-e2e-session-secret-local-only-32-chars",
    COOKIE_SECURE: "false",
    ALLOWED_ORIGINS: "http://localhost:5173,http://127.0.0.1:5173",
  };
  rmSync(databasePath, { force: true });
  mkdirSync(path.dirname(passwordPath), { recursive: true });
  writeFileSync(passwordPath, password, { encoding: "utf8" });
  execFileSync(pythonExecutable, ["-m", "alembic", "upgrade", "head"], {
    cwd: backendRoot,
    env: environment,
    stdio: "pipe",
  });
  execFileSync(pythonExecutable, ["-m", "app.scripts.seed_demo"], {
    cwd: backendRoot,
    env: environment,
    stdio: "pipe",
  });

  const startedServers: ChildProcess[] = [];
  try {
    const backend = spawn(
      pythonExecutable,
      [
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
      ],
      {
        cwd: backendRoot,
        env: environment,
        stdio: "ignore",
        windowsHide: true,
      },
    );
    startedServers.push(backend);
    await waitForUrl("http://127.0.0.1:8000/health", backend);

    const frontend = spawn(
      process.execPath,
      [viteScript, "--host", "127.0.0.1", "--port", "5173"],
      {
        cwd: frontendRoot,
        env: { ...process.env, VITE_API_BASE_URL: "http://127.0.0.1:8000" },
        stdio: "ignore",
        windowsHide: true,
      },
    );
    startedServers.push(frontend);
    await waitForUrl("http://127.0.0.1:5173", frontend);
    writeFileSync(
      serverPidPath,
      JSON.stringify(
        { backendPid: backend.pid, frontendPid: frontend.pid },
        null,
        2,
      ),
      { encoding: "utf8" },
    );
  } catch (error) {
    for (const server of startedServers) {
      server.kill();
    }
    throw error;
  }
  process.env.E2E_DEMO_PASSWORD = password;
  process.env.DATABASE_URL = databaseUrl;
}
