import type { LawSummary } from "./types";

/** Normalize LaTeX for deduplication (whitespace, common forms). */
export function normalizeLawLatex(latex: string): string {
  return latex.replace(/\s+/g, " ").trim().toLowerCase();
}

export type GroupedLaw = {
  key: string;
  law_latex: string;
  domain: string;
  entries: LawSummary[];
  best: LawSummary;
};

const DOMAIN_FROM_LATEX: { match: RegExp; domain: string }[] = [
  { match: /pendulum|sqrt\{l\/g\}|\\sqrt\{l/i, domain: "Mechanics · pendulum" },
  { match: /N\(t\)|logistic|cell/i, domain: "Biology · cells" },
  { match: /T\s*=\s*k\s*L/i, domain: "Mechanics · scaling" },
];

export function inferLawDomain(latex: string): string {
  for (const { match, domain } of DOMAIN_FROM_LATEX) {
    if (match.test(latex)) return domain;
  }
  return "General";
}

/** Deduplicate by law formula; keep all session entries under one card. */
export function groupLaws(laws: LawSummary[]): GroupedLaw[] {
  const map = new Map<string, LawSummary[]>();
  for (const law of laws) {
    const key = normalizeLawLatex(law.law_latex);
    const bucket = map.get(key) ?? [];
    bucket.push(law);
    map.set(key, bucket);
  }
  const groups: GroupedLaw[] = [];
  for (const [key, entries] of map) {
    const sorted = [...entries].sort((a, b) => (b.stages_completed ?? 0) - (a.stages_completed ?? 0));
    const best = sorted[0];
    groups.push({
      key,
      law_latex: best.law_latex,
      domain: inferLawDomain(best.law_latex),
      entries: sorted,
      best,
    });
  }
  groups.sort((a, b) => a.domain.localeCompare(b.domain) || a.law_latex.localeCompare(b.law_latex));
  return groups;
}

export function filterGroupedLaws(groups: GroupedLaw[], query: string): GroupedLaw[] {
  const q = query.trim().toLowerCase();
  if (!q) return groups;
  return groups.filter(
    (g) =>
      g.law_latex.toLowerCase().includes(q) ||
      g.domain.toLowerCase().includes(q) ||
      g.entries.some((e) => e.session_id.toLowerCase().includes(q)),
  );
}
