"use client";

import katex from "katex";
import { useMemo } from "react";

type Props = {
  latex: string;
  display?: boolean;
  className?: string;
};

/** Render session law strings (may include `\pi`, `\sqrt`, etc.). */
export function KatexMath({ latex, display = false, className }: Props) {
  const html = useMemo(() => {
    const trimmed = latex.trim();
    if (!trimmed) return "";
    try {
      return katex.renderToString(trimmed, {
        throwOnError: false,
        displayMode: display,
        strict: "ignore",
      });
    } catch {
      return trimmed.replace(/</g, "&lt;");
    }
  }, [latex, display]);

  if (!html) {
    return <span className={className}>—</span>;
  }

  if (display) {
    return (
      <div
        className={className ? `katex-display-wrap ${className}` : "katex-display-wrap"}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  }

  return (
    <span
      className={className ? `katex-inline ${className}` : "katex-inline"}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
