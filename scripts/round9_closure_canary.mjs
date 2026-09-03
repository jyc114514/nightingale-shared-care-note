const BASE_URL = process.env.CANARY_URL ?? "https://nightingale-shared-care-note.onrender.com";
const SAMPLE_COUNT = Number(process.env.CANARY_SAMPLES ?? 15);
const INTERVAL_MS = Number(process.env.CANARY_INTERVAL_MS ?? 60_000);

async function request(url, options = {}) {
  const started = performance.now();
  const response = await fetch(url, {
    redirect: "manual",
    ...options,
  });
  return {
    status: response.status,
    elapsed_ms: Number((performance.now() - started).toFixed(3)),
    content_type: response.headers.get("content-type") ?? "",
    location: response.headers.get("location") ?? "",
    body: await response.text(),
  };
}

function assetPath(html, extension) {
  const match = html.match(new RegExp(`(?:src|href)=["']([^"']+\\.${extension})`, "i"));
  if (!match) throw new Error(`current ${extension} asset was not found in root HTML`);
  return match[1];
}

function assertStatus(label, observed, expected) {
  if (observed.status !== expected) {
    throw new Error(`${label} expected ${expected}, observed ${observed.status}`);
  }
}

const httpHealth = await request(`${BASE_URL.replace("https://", "http://")}/health`);
assertStatus("HTTP health redirect", httpHealth, 301);
if (!httpHealth.location.startsWith(`${BASE_URL}/health`)) {
  throw new Error("HTTP health did not redirect to the HTTPS health endpoint");
}

const health = await request(`${BASE_URL}/health`);
assertStatus("HTTPS health", health, 200);
const root = await request(`${BASE_URL}/`);
assertStatus("SPA root", root, 200);
const jsPath = assetPath(root.body, "js");
const cssPath = assetPath(root.body, "css");
const authMe = await request(`${BASE_URL}/auth/me`);
const patients = await request(`${BASE_URL}/patients`);
assertStatus("Unauthenticated auth/me", authMe, 401);
assertStatus("Unauthenticated patients", patients, 401);

const samples = [];
for (let index = 1; index <= SAMPLE_COUNT; index += 1) {
  const [sampleHealth, sampleRoot, sampleJs, sampleCss] = await Promise.all([
    request(`${BASE_URL}/health`),
    request(`${BASE_URL}/`),
    request(`${BASE_URL}${jsPath}`),
    request(`${BASE_URL}${cssPath}`),
  ]);
  const statuses = [sampleHealth, sampleRoot, sampleJs, sampleCss].map(
    (response) => response.status,
  );
  const failures = statuses.filter((status) => status < 200 || status >= 300).length;
  const five_xx = statuses.filter((status) => status >= 500).length;
  samples.push({
    sample: index,
    statuses,
    failures,
    five_xx,
    elapsed_ms: [sampleHealth, sampleRoot, sampleJs, sampleCss].map(
      (response) => response.elapsed_ms,
    ),
  });
  console.log(JSON.stringify(samples.at(-1)));
  if (index < SAMPLE_COUNT) await new Promise((resolve) => setTimeout(resolve, INTERVAL_MS));
}

const failure_count = samples.reduce((total, sample) => total + sample.failures, 0);
const five_xx_count = samples.reduce((total, sample) => total + sample.five_xx, 0);
console.log(
  JSON.stringify({
    status: failure_count === 0 ? "PASS" : "FAIL",
    base_url: BASE_URL,
    samples: SAMPLE_COUNT,
    interval_ms: INTERVAL_MS,
    failure_count,
    five_xx_count,
    http_health_status: httpHealth.status,
    https_health_status: health.status,
    unauthenticated_auth_me_status: authMe.status,
    unauthenticated_patients_status: patients.status,
  }),
);
