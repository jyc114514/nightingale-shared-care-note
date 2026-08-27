import { afterEach, describe, expect, it, vi } from "vitest";

import { api, voiceAudioRequestUrl } from "../src/api";

function audioResponse(contentType = "audio/wav", status = 200): Response {
  const blob = new Blob(["RIFF synthetic audio"], { type: contentType });
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": contentType }),
    blob: vi.fn(async () => blob),
  } as unknown as Response;
}

describe("voice audio API boundary", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("resolves the development audio path through the API host", () => {
    expect(
      voiceAudioRequestUrl(
        "patient-a",
        "nurse-follow-up",
        "http://localhost:8000",
      ),
    ).toBe(
      "http://localhost:8000/patients/patient-a/voice/samples/nurse-follow-up/audio",
    );
  });

  it("keeps production audio same-origin", () => {
    expect(voiceAudioRequestUrl("patient-a", "patient-follow-up", "")).toBe(
      "/patients/patient-a/voice/samples/patient-follow-up/audio",
    );
  });

  it("loads only an authenticated WAV response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(audioResponse());
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();

    const blob = await api.loadVoiceAudio(
      "patient-a",
      "nurse-follow-up",
      controller.signal,
    );

    expect(blob).toBeInstanceOf(Blob);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/patients/patient-a/voice/samples/nurse-follow-up/audio",
      expect.objectContaining({
        credentials: "include",
        signal: controller.signal,
      }),
    );
  });

  it("rejects unauthorized or non-audio responses without accepting arbitrary URLs", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(audioResponse("audio/wav", 403))
      .mockResolvedValueOnce(audioResponse("text/plain"));
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      api.loadVoiceAudio("patient-a", "nurse-follow-up"),
    ).rejects.toThrow("HTTP 403");
    await expect(
      api.loadVoiceAudio("patient-a", "nurse-follow-up"),
    ).rejects.toThrow("audio_content_type_invalid");
    await expect(
      api.loadVoiceAudio("https://unexpected.example", "sample"),
    ).rejects.toThrow("audio_path_invalid");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
