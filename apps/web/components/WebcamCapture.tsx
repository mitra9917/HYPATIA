"use client";

import { useCallback, useRef, useState } from "react";

type Props = {
  disabled?: boolean;
  seconds?: number;
  onCapture: (file: File) => void;
  onError?: (message: string) => void;
};

/** Short webcam burst → WebM upload for observe/measure (P1.7 / Playbook #25). */
export function WebcamCapture({ disabled, seconds = 4, onCapture, onError }: Props) {
  const [recording, setRecording] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  async function startBurst() {
    if (disabled || recording) return;
    setPreview(null);
    chunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      const mime = MediaRecorder.isTypeSupported("video/webm;codecs=vp9")
        ? "video/webm;codecs=vp9"
        : "video/webm";
      const recorder = new MediaRecorder(stream, { mimeType: mime });
      recorderRef.current = recorder;
      recorder.ondataavailable = (ev) => {
        if (ev.data.size > 0) chunksRef.current.push(ev.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mime });
        const file = new File([blob], `hypatia-webcam-${Date.now()}.webm`, { type: mime });
        setPreview(URL.createObjectURL(blob));
        onCapture(file);
        stopStream();
        setRecording(false);
      };
      recorder.start(200);
      setRecording(true);
      window.setTimeout(() => {
        if (recorder.state === "recording") {
          recorder.stop();
        }
      }, seconds * 1000);
    } catch (e) {
      stopStream();
      setRecording(false);
      onError?.(e instanceof Error ? e.message : "Webcam access denied or unavailable");
    }
  }

  return (
    <div className="webcam-capture">
      <button type="button" className="btn secondary" disabled={disabled || recording} onClick={() => void startBurst()}>
        {recording ? `Recording ${seconds}s…` : `Webcam burst (${seconds}s)`}
      </button>
      {preview ? (
        <video className="webcam-preview" src={preview} muted playsInline controls aria-label="Webcam burst preview" />
      ) : null}
    </div>
  );
}
