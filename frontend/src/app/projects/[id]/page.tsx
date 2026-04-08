"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatWon, formatKwh, formatMonth } from "@/lib/utils/format";

interface MonthlyBill {
  id: string;
  billingMonth: string;
  usageKwh: number;
  totalBillKrw: number;
}

interface Project {
  id: string;
  projectName: string;
  customerName: string;
  contactName: string;
  buildingType: string;
  buildingName: string;
  campusOrSiteName: string | null;
  totalAreaM2: number | null;
  status: string;
  operatingHoursWeekday: string | null;
  hvacType: string | null;
  createdAt: string;
  monthlyBills: MonthlyBill[];
  analysisSnapshots: { id: string }[];
}

const STATUS_MAP: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  draft: { label: "초안", variant: "secondary" },
  analyzed: { label: "분석완료", variant: "default" },
  exported: { label: "내보내기", variant: "outline" },
};

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetch(`/api/projects/${id}`)
      .then((res) => res.json())
      .then(setProject)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleDelete() {
    if (!confirm("이 프로젝트를 삭제하시겠습니까?")) return;
    setDeleting(true);
    await fetch(`/api/projects/${id}`, { method: "DELETE" });
    router.push("/");
  }

  if (loading) return <div className="text-center py-12 text-gray-500">불러오는 중...</div>;
  if (!project) return <div className="text-center py-12 text-gray-500">프로젝트를 찾을 수 없습니다</div>;

  const status = STATUS_MAP[project.status] || STATUS_MAP.draft;
  const totalUsage = project.monthlyBills.reduce((s, b) => s + b.usageKwh, 0);
  const totalBill = project.monthlyBills.reduce((s, b) => s + b.totalBillKrw, 0);
  const hasAnalysis = project.analysisSnapshots.length > 0;

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{project.projectName}</h1>
            <Badge variant={status.variant}>{status.label}</Badge>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            {project.customerName} / {project.buildingType} - {project.buildingName}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleDelete} disabled={deleting}>
            삭제
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500">입력 데이터</div>
            <div className="text-2xl font-bold">{project.monthlyBills.length}개월</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500">총 사용량</div>
            <div className="text-2xl font-bold">{formatKwh(totalUsage)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500">총 요금</div>
            <div className="text-2xl font-bold">{formatWon(totalBill)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Bills Table */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>월별 요금 데이터</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="p-2 text-left">청구월</th>
                <th className="p-2 text-right">사용전력량</th>
                <th className="p-2 text-right">청구금액</th>
                <th className="p-2 text-right">환산 청구단가</th>
              </tr>
            </thead>
            <tbody>
              {project.monthlyBills.map((bill) => (
                <tr key={bill.id} className="border-b">
                  <td className="p-2">{formatMonth(bill.billingMonth)}</td>
                  <td className="p-2 text-right">{formatKwh(bill.usageKwh)}</td>
                  <td className="p-2 text-right">{formatWon(bill.totalBillKrw)}</td>
                  <td className="p-2 text-right">
                    {bill.usageKwh > 0
                      ? (bill.totalBillKrw / bill.usageKwh).toFixed(1) + " 원/kWh"
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Link href={`/projects/${id}/review`}>
          <Button variant="outline">데이터 검토</Button>
        </Link>
        {hasAnalysis ? (
          <>
            <Link href={`/projects/${id}/analysis`}>
              <Button>분석 결과 보기</Button>
            </Link>
            <Link href={`/projects/${id}/report`}>
              <Button variant="outline">보고서 보기</Button>
            </Link>
          </>
        ) : (
          <Link href={`/projects/${id}/review`}>
            <Button>분석 시작</Button>
          </Link>
        )}
      </div>
    </div>
  );
}
