"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Header() {
  const pathname = usePathname();

  // Hide header on print/report pages
  if (pathname?.includes("/report")) return null;

  return (
    <header className="border-b bg-white print:hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-lg font-semibold text-gray-900">
              전기요금 예비진단
            </Link>
            <nav className="flex items-center gap-6">
              <Link
                href="/"
                className={`text-sm ${
                  pathname === "/" ? "text-blue-600 font-medium" : "text-gray-600 hover:text-gray-900"
                }`}
              >
                대시보드
              </Link>
              <Link
                href="/settings"
                className={`text-sm ${
                  pathname === "/settings"
                    ? "text-blue-600 font-medium"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                설정
              </Link>
            </nav>
          </div>
          <div className="text-xs text-gray-400">v1.0 MVP</div>
        </div>
      </div>
    </header>
  );
}
