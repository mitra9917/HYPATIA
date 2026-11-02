"use client";

import { SiteNav } from "./SiteNav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <SiteNav />
      </header>
      <main className="app-shell__main">{children}</main>
      <footer className="app-shell__footer">
        <span>HYPATIA — observe · measure · hypothesize · imagine · experiment · accept</span>
      </footer>
    </div>
  );
}
