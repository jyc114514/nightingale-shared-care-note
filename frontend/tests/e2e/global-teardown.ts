import { execFileSync } from "node:child_process";
import { readFileSync, rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const e2eRoot = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(e2eRoot, "..", "..");
const repositoryRoot = path.resolve(frontendRoot, "..");
const serverPidPath = path.join(
  frontendRoot,
  "test-results",
  "gate-b",
  "server-pids.json",
);

function stopProcessTree(pid: number | undefined) {
  if (!pid) {
    return;
  }
  try {
    execFileSync("taskkill.exe", ["/PID", String(pid), "/T", "/F"], {
      stdio: "ignore",
      windowsHide: true,
    });
  } catch {
    // The process may already have exited; cleanup remains idempotent.
  }
}

async function removeWithRetry(target: string) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    try {
      rmSync(target, { force: true });
      return;
    } catch (error) {
      if (attempt === 19) {
        throw error;
      }
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
}

export default async function globalTeardown() {
  try {
    const pids = JSON.parse(readFileSync(serverPidPath, "utf8")) as {
      backendPid?: number;
      frontendPid?: number;
    };
    stopProcessTree(pids.frontendPid);
    stopProcessTree(pids.backendPid);
  } catch {
    // A failed setup may not have written the PID file.
  }
  await removeWithRetry(
    path.join(repositoryRoot, ".uv-cache", "gate-b-e2e.sqlite"),
  );
  await removeWithRetry(
    path.join(frontendRoot, "test-results", "gate-b", "e2e-password.txt"),
  );
  await removeWithRetry(serverPidPath);
}
