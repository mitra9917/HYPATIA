import type { Metadata } from "next";
import { AppShell } from "@/components/shell/AppShell";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "HYPATIA — the camera that does science",
  description:
    "Point any camera at anything that moves. HYPATIA finds the law, predicts the future, and designs the next experiment.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
