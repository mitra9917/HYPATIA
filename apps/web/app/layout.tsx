import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-display-loaded",
});

const body = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body-loaded",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono-loaded",
});

export const metadata: Metadata = {
  title: "HYPATIA — the camera that does science",
  description:
    "Point any camera at anything that moves. HYPATIA finds the law, predicts the future, and designs the next experiment. Built with Meta Muse + SAM 3.1.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body
        style={{
          ["--font-display" as string]: "var(--font-display-loaded), serif",
          ["--font-body" as string]: "var(--font-body-loaded), sans-serif",
          ["--font-mono" as string]: "var(--font-mono-loaded), monospace",
        }}
      >
        {children}
      </body>
    </html>
  );
}
