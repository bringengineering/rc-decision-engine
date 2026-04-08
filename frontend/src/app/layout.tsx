import type { Metadata } from "next";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Header } from "@/components/layout/header";

export const metadata: Metadata = {
  title: "전기요금 예비진단 도구 | 브링 에너지",
  description: "전기요금 기반 예비진단 및 다음 단계 제안 도구",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-gray-50 font-sans">
        <TooltipProvider>
          <Header />
          <main className="flex-1">{children}</main>
        </TooltipProvider>
      </body>
    </html>
  );
}
