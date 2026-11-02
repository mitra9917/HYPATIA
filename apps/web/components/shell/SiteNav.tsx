"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/lab", label: "Lab" },
  { href: "/sessions", label: "Sessions" },
  { href: "/library", label: "Laws" },
  { href: "/notebook", label: "Notebook" },
  { href: "/settings", label: "Settings" },
  { href: "/about", label: "About" },
] as const;

export function SiteNav() {
  const pathname = usePathname();

  return (
    <nav className="site-nav" aria-label="Primary">
      <Link href="/" className="site-nav__brand">
        HYPATIA
      </Link>
      <ul className="site-nav__links">
        {LINKS.map(({ href, label }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <li key={href}>
              <Link href={href} className={active ? "is-active" : undefined} aria-current={active ? "page" : undefined}>
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
