/** Scientific webcam burst defaults (P1.13 / Playbook #26, issue #53). */

export const WEBCAM_BURST_MIN_S = 5;
export const WEBCAM_BURST_MAX_S = 15;
export const WEBCAM_BURST_DEFAULT_S = 8;

export const WEBCAM_WIDTH = 1280;
export const WEBCAM_HEIGHT = 720;
export const WEBCAM_FPS = 30;

export function clampBurstSeconds(seconds: number): number {
  return Math.min(WEBCAM_BURST_MAX_S, Math.max(WEBCAM_BURST_MIN_S, Math.round(seconds)));
}

export function scientificVideoConstraints(): MediaTrackConstraints {
  return {
    facingMode: "environment",
    width: { ideal: WEBCAM_WIDTH, max: WEBCAM_WIDTH },
    height: { ideal: WEBCAM_HEIGHT, max: WEBCAM_HEIGHT },
    frameRate: { ideal: WEBCAM_FPS, max: WEBCAM_FPS },
  };
}

export function pickWebmMimeType(): string {
  if (typeof MediaRecorder === "undefined") {
    return "video/webm";
  }
  if (MediaRecorder.isTypeSupported("video/webm;codecs=vp9")) {
    return "video/webm;codecs=vp9";
  }
  return "video/webm";
}

export function webcamUnavailableMessage(): string {
  if (typeof navigator === "undefined") {
    return "Webcam requires a browser.";
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    return "This browser does not support camera capture. Use Upload clip instead.";
  }
  return "Camera unavailable. Allow permission for this site or use Upload clip.";
}
