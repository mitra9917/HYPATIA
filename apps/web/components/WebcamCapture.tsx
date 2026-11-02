"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  clampBurstSeconds,
  pickWebmMimeType,
  scientificVideoConstraints,
  WEBCAM_BURST_DEFAULT_S,
  WEBCAM_BURST_MAX_S,
  WEBCAM_BURST_MIN_S,
  webcamUnavailableMessage,
} from "@/lib/webcam";

type Props = {
  disabled?: boolean;
  onCapture: (file: File) => void;
};

type PermissionState = "idle" | "recording" | "denied" | "unsupported";

/** 5–15s scientific burst at 720p/30 → same POST /api/sessions as upload (P1.13 / #53). */
export function WebcamCapture({ disabled, onCapture }: Props) {
  const [burstSeconds, setBurstSeconds] = useState(WEBCAM_BURST_DEFAULT_S);
  const [recording, setRecording] = useState(false);
  const [permission, setPermission] = useState<PermissionState>("idle");
  const [preview, setPreview] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const liveVideoRef = useRef<HTMLVideoElement | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (liveVideoRef.current) {
      liveVideoRef.current.srcObject = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      stopStream();
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview, stopStream]);

  async function startBurst() {
    if (disabled || recording) return;
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setPermission("unsupported");
      return;
    }

    setPreview(null);
    setPermission("idle");
    chunksRef.current = [];
    const seconds = clampBurstSeconds(burstSeconds);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: scientificVideoConstraints(),
        audio: false,
      });
      streamRef.current = stream;
      if (liveVideoRef.current) {
        liveVideoRef.current.srcObject = stream;
        void liveVideoRef.current.play();
      }

      const mime = pickWebmMimeType();
      const recorder = new MediaRecorder(stream, {
        mimeType: mime,
        videoBitsPerSecond: 2_500_000,
      });
      recorderRef.current = recorder;
      recorder.ondataavailable = (ev) => {
        if (ev.data.size > 0) chunksRef.current.push(ev.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mime });
        const file = new File([blob], `hypatia-webcam-${Date.now()}.webm`, { type: mime });
        const url = URL.createObjectURL(blob);
        setPreview(url);
        onCapture(file);
        stopStream();
        setRecording(false);
        setCountdown(null);
        if (timerRef.current) window.clearInterval(timerRef.current);
      };
      recorder.start(250);
      setRecording(true);
      setCountdown(seconds);
      timerRef.current = window.setInterval(() => {
        setCountdown((c) => {
          if (c == null || c <= 1) {
            if (recorder.state === "recording") recorder.stop();
            return null;
          }
          return c - 1;
        });
      }, 1000);
      window.setTimeout(() => {
        if (recorder.state === "recording") recorder.stop();
      }, seconds * 1000);
    } catch (e) {
      stopStream();
      setRecording(false);
      setCountdown(null);
      const name = e instanceof Error ? e.name : "";
      if (name === "NotAllowedError" || name === "PermissionDeniedError") {
        setPermission("denied");
      } else {
        setPermission("unsupported");
      }
    }
  }

  return (
    <div className="webcam-capture">
      <p className="meta webcam-hint">
        Point at a pendulum or moving object · {WEBCAM_BURST_MIN_S}–{WEBCAM_BURST_MAX_S}s at 720p/30
        (same session API as upload)
      </p>
      <label className="meta burst-length">
        Burst length ({burstSeconds}s)
        <input
          type="range"
          min={WEBCAM_BURST_MIN_S}
          max={WEBCAM_BURST_MAX_S}
          value={burstSeconds}
          disabled={disabled || recording}
          onChange={(e) => setBurstSeconds(clampBurstSeconds(Number(e.target.value)))}
        />
      </label>
      <button type="button" className="btn secondary" disabled={disabled || recording} onClick={() => void startBurst()}>
        {recording ? `Recording… ${countdown ?? burstSeconds}s left` : `Start webcam burst (${burstSeconds}s)`}
      </button>

      {(permission === "denied" || permission === "unsupported") && (
        <p className="meta webcam-fallback" role="alert">
          {webcamUnavailableMessage()} Use <strong>Upload clip</strong> above instead.
        </p>
      )}

      {recording ? (
        <video ref={liveVideoRef} className="webcam-preview" muted playsInline aria-label="Live webcam while recording" />
      ) : null}

      {preview && !recording ? (
        <video className="webcam-preview" src={preview} muted playsInline controls aria-label="Recorded burst preview" />
      ) : null}
    </div>
  );
}
