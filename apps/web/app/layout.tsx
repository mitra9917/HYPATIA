import type { Metadata } from "next";
import { AppShell } from "@/components/shell/AppShell";
import { fontVariables } from "@/lib/fonts";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "HYPATIA — the camera that does science",
  description:
    "Point any camera at anything that moves. HYPATIA finds the law, predicts the future, and designs the next experiment.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={fontVariables}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
