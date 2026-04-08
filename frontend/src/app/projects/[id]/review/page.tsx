"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { formatWon, formatKwh, formatMonth } from "@/lib/utils/format";
import type { DataQualityResult } from "@/lib/utils/data-quality";

interface BillRecord {
  id: string;
  billingMonth: string;
  usageKwh: number;
  totalBillKrw: number;
  basicChargeKrw: number | null;
  energyChargeKrw: number | null;
  climateChargeKrw: number | null;
  fuelAdjustmentKrw: number | null;
  vatKrw: number | null;
}

interface ReviewData {
  bills: BillRecord[];
  quality: DataQualityResult;
}

const STATUS_COLORS: Record<string, string> = {
  "분석 가능": "bg-green-100 text-green-800",
  "주의 필요": "bg-yellow-100 text-yellow-800",
  "보완 필요": "bg-red-100 text-red-800",
};

export default function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [data, setData] = useState<ReviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`/api/projects/${id}/review`)
      .then((res) => res.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleAnalyze() {
    setAnalyzing(true);
    setError("");
    try {
      const res = await fetch(`/api/projects/${id}/analyze`, { method: "POST" });
      if (!res.ok) {
        const err = await res.json();
        setError(err.error || "분석 중 오류가 발생했습니다");
        return;
      }
      router.push(`/projects/${id}/analysis`);
    } catch {
      setError("네트워크 오류가 발생했습니다");
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) return <div className="text-center py-12 text-gray-500">불러오는 중...</div>;
  if (!data) return <div className="text-center py-12 text-gray-500">데이터를 찾을 수 없습니다</div>;

  const { bills, quality } = data;

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">입력 데이터 검토</h1>
      <p className="text-sm text-gray-500 mb-6">분석 실행 전 데이터 완성도와 품질을 확인합니다</p>

      {error && (
        <Alert className="mb-4" variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Quality Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-sm text-gray-500 mb-1">데이터 완성도</div>
            <div className="text-4xl font-bold">{quality.completenessScore}</div>
            <div className="text-sm text-gray-400">/100</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-sm text-gray-500 mb-1">분석 가능 여부</div>
            <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-2 ${STATUS_COLORS[quality.status]}`}>
              {quality.status}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-sm text-gray-500 mb-1">입력 월수</div>
            <div className="text-4xl font-bold">{bills.length}</div>
            <div className="text-sm text-gray-400">/12개월</div>
          </CardContent>
        </Card>
      </div>

      {/* Warnings */}
      {quality.warnings.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">경고 및 확인 사항</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {quality.warnings.map((warning, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-yellow-500 mt-0.5">&#9888;</span>
                  <span className="text-gray-700">{warning}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Data Table */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">월별 데이터 상세</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="p-2 text-left">청구월</th>
                  <th className="p-2 text-right">사용량(kWh)</th>
                  <th className="p-2 text-right">청구금액(원)</th>
                  <th className="p-2 text-right">기본요금</th>
                  <th className="p-2 text-right">전력량요금</th>
                  <th className="p-2 text-right">기후환경요금</th>
                  <th className="p-2 text-right">연료비조정액</th>
                  <th className="p-2 text-right">부가세</th>
                  <th className="p-2 text-center">상태</th>
                </tr>
              </thead>
              <tbody>
                {bills.map((bill) => {
                  const hasCore = bill.usageKwh > 0 && bill.totalBillKrw > 0;
                  const hasBreakdown = bill.basicChargeKrw != null;
                  return (
                    <tr key={bill.id} className={`border-b ${!hasCore ? "bg-red-50" : ""}`}>
                      <td className="p-2">{formatMonth(bill.billingMonth)}</td>
                      <td className="p-2 text-right">{formatKwh(bill.usageKwh)}</td>
                      <td className="p-2 text-right">{formatWon(bill.totalBillKrw)}</td>
                      <td className="p-2 text-right text-gray-500">
                        {bill.basicChargeKrw != null ? formatWon(bill.basicChargeKrw) : "-"}
                      </td>
                      <td className="p-2 text-right text-gray-500">
                        {bill.energyChargeKrw != null ? formatWon(bill.energyChargeKrw) : "-"}
                      </td>
                      <td className="p-2 text-right text-gray-500">
                        {bill.climateChargeKrw != null ? formatWon(bill.climateChargeKrw) : "-"}
                      </td>
                      <td className="p-2 text-right text-gray-500">
                        {bill.fuelAdjustmentKrw != null ? formatWon(bill.fuelAdjustmentKrw) : "-"}
                      </td>
                      <td className="p-2 text-right text-gray-500">
                        {bill.vatKrw != null ? formatWon(bill.vatKrw) : "-"}
                      </td>
                      <td className="p-2 text-center">
                        {hasCore && hasBreakdown ? (
                          <Badge variant="outline" className="text-green-600">완전</Badge>
                        ) : hasCore ? (
                          <Badge variant="outline" className="text-yellow-600">부분</Badge>
                        ) : (
                          <Badge variant="outline" className="text-red-600">미완</Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => router.push(`/projects/${id}`)}>
          돌아가기
        </Button>
        <Button
          onClick={handleAnalyze}
          disabled={analyzing || quality.status === "보완 필요"}
        >
          {analyzing ? "분석 중..." : "분석 실행"}
        </Button>
      </div>
    </div>
  );
}
