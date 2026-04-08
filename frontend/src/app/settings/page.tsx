"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function SettingsPage() {
  const [companyName, setCompanyName] = useState("");
  const [companyLogoUrl, setCompanyLogoUrl] = useState("");
  const [consultantName, setConsultantName] = useState("");
  const [footerText, setFooterText] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch("/api/report-config")
      .then((r) => r.json())
      .then((data) => {
        setCompanyName(data.companyName || "");
        setCompanyLogoUrl(data.companyLogoUrl || "");
        setConsultantName(data.consultantName || "");
        setFooterText(data.footerText || "");
      });
  }, []);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    await fetch("/api/report-config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        companyName,
        companyLogoUrl: companyLogoUrl || null,
        consultantName: consultantName || null,
        footerText: footerText || null,
      }),
    });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">보고서 설정</h1>

      <Card>
        <CardHeader>
          <CardTitle>회사/컨설턴트 정보</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>회사명</Label>
            <Input value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="브링 에너지" />
          </div>
          <div>
            <Label>회사 로고 URL</Label>
            <Input value={companyLogoUrl} onChange={(e) => setCompanyLogoUrl(e.target.value)} placeholder="https://..." />
          </div>
          <div>
            <Label>컨설턴트명</Label>
            <Input value={consultantName} onChange={(e) => setConsultantName(e.target.value)} placeholder="홍길동" />
          </div>
          <div>
            <Label>보고서 하단 텍스트</Label>
            <Textarea
              value={footerText}
              onChange={(e) => setFooterText(e.target.value)}
              placeholder="전기요금 기반 예비진단 및 다음 단계 제안 도구"
            />
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "저장 중..." : "저장"}
            </Button>
            {saved && <span className="text-sm text-green-600">저장되었습니다</span>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
