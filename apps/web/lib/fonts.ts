import { Instrument_Serif, Inter, JetBrains_Mono } from "next/font/google";

export const fontDisplay = Instrument_Serif({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-instrument-serif",
});

export const fontBody = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const fontMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jetbrains-mono",
});

export const fontVariables = `${fontDisplay.variable} ${fontBody.variable} ${fontMono.variable}`;
