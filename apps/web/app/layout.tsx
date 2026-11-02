import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HYPATIA — the camera that does science",
  description:
    "Point any camera at anything that moves. HYPATIA finds the law, predicts the future, and designs the next experiment. Built with Meta Muse + SAM 3.1.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
