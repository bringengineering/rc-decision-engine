"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { formatWon, formatKwh, formatMonth, formatCostPerKwh, formatPercent } from "@/lib/utils/format";
import { AnalysisCharts } from "@/components/analysis/analysis-charts";
import type { AbnormalMonth } from "@/lib/analysis/analysis-flags";
import type { Recommendation } from "@/lib/analysis/analysis-recommendations";
import type { InsightGroup } from "@/lib/analysis/analysis-insights";
import type { MonthlyChange } from "@/lib/analysis/analysis-metrics";

interface AnalysisSnapshot {
  annualUsageKwh: number;
  annualBillKrw: number;
  averageMonthlyUsageKwh: number;
  averageMonthlyBillKrw: number;
  averageCostPerKwh: number;
  maxUsageMonth: string;
  maxUsageValue: number;
  minUsageMonth: string;
  minUsageValue: number;
  maxBillMonth: string;
  maxBillValue: number;
  minBillMonth: string;
  minBillValue: number;
  seasonalStrengthRatio: number;
  summerAvgUsage: number;
  winterAvgUsage: number;
  shoulderAvgUsage: number;
  abnormalMonthsJson: string;
  insightsJson: string;
  recommendationJson: string;
  monthlyChangesJson: string;
  inputCompletenessScore: number;
  confidenceScore: number;
  limitationsText: string;
}

interface MonthlyBill {
  billingMonth: string;
  usageKwh: number;
  totalBillKrw: number;
  basicChargeKrw: number | null;
  energyChargeKrw: number | null;
  climateChargeKrw: number | null;
  fuelAdjustmentKrw: number | null;
  vatKrw: number | null;
}

interface Project {
  id: string;
  projectName: string;
  customerName: string;
  buildingType: string;
  buildingName: string;
  consultantManualSummary: string | null;
  monthlyBills: MonthlyBill[];
  analysisSnapshots: AnalysisSnapshot[];
}

export default function AnalysisPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [consultantNotes, setConsultantNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    fetch(`/api/projects/${id}`)
      .then((res) => res.json())
      .then((data: Project) => {
        setProject(data);
        setConsultantNotes(data.consultantManualSummary ?? "");
      })
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSaveNotes() {
    setSaving(true);
    setSaveSuccess(false);
    try {
      await fetch(`/api/projects/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consultantManualSummary: consultantNotes }),
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="text-center py-12 text-gray-500">불러오는 중...</div>;
  if (!project) return <div className="text-center py-12 text-gray-500">프로젝트를 찾을 수 없습니다</div>;

  const snapshot = project.analysisSnapshots[0];
  if (!snapshot) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 text-center">
        <p className="text-gray-500 mb-4">분석 결과가 없습니다. 먼저 분석을 실행해주세요.</p>
        <Link href={`/projects/${id}/review`}>
          <Button>데이터 검토 및 분석</Button>
        </Link>
      </div>
    );
  }

  const abnormals: AbnormalMonth[] = JSON.parse(snapshot.abnormalMonthsJson);
  const insights: InsightGroup[] = JSON.parse(snapshot.insightsJson);
  const recommendations: Recommendation[] = JSON.parse(snapshot.recommendationJson);
  const monthlyChanges: MonthlyChange[] = JSON.parse(snapshot.monthlyChangesJson);

  const bills = project.monthlyBills.sort((a, b) => a.billingMonth.localeCompare(b.billingMonth));

  const strengthLabel =
    snapshot.seasonalStrengthRatio < 1.2 ? "약함" :
    snapshot.seasonalStrengthRatio < 1.5 ? "보통" : "강함";

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">분석 결과</h1>
          <p className="text-sm text-gray-500">{project.projectName} - {project.customerName}</p>
        </div>
        <div className="flex gap-2">
          <Link href={`/projects/${id}/report`}>
            <Button variant="outline">1페이지 요약 보고서</Button>
          </Link>
          <Link href={`/projects/${id}/report/detailed`}>
            <Button>상세 보고서</Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs text-gray-500">연간 총 사용량</div>
            <div className="text-xl font-bold mt-1">{formatKwh(snapshot.annualUsageKwh)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs text-gray-500">연간 총 요금</div>
            <div className="text-xl font-bold mt-1">{formatWon(snapshot.annualBillKrw)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs text-gray-500">월 평균 사용량</div>
            <div className="text-xl font-bold mt-1">{formatKwh(snapshot.averageMonthlyUsageKwh)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs text-gray-500">평균 환산 청구단가</div>
            <div className="text-xl font-bold mt-1">{formatCostPerKwh(snapshot.averageCostPerKwh)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <AnalysisCharts bills={bills} />

      {/* Seasonal Summary */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">계절별 요약</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-500">계절 강도 비율</div>
              <div className="font-semibold">{snapshot.seasonalStrengthRatio.toFixed(2)} ({strengthLabel})</div>
            </div>
            <div>
              <div className="text-gray-500">하절기 평균</div>
              <div className="font-semibold">{formatKwh(snapshot.summerAvgUsage)}</div>
            </div>
            <div>
              <div className="text-gray-500">동절기 평균</div>
              <div className="font-semibold">{formatKwh(snapshot.winterAvgUsage)}</div>
            </div>
            <div>
              <div className="text-gray-500">중간기 평균</div>
              <div className="font-semibold">{formatKwh(snapshot.shoulderAvgUsage)}</div>
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">최고 사용월: </span>
              <span className="font-semibold">{formatMonth(snapshot.maxUsageMonth)} ({formatKwh(snapshot.maxUsageValue)})</span>
            </div>
            <div>
              <span className="text-gray-500">최저 사용월: </span>
              <span className="font-semibold">{formatMonth(snapshot.minUsageMonth)} ({formatKwh(snapshot.minUsageValue)})</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Abnormal Months */}
      {abnormals.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">특이월 후보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {abnormals.map((ab) => (
                <div key={ab.billingMonth} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-md">
                  <Badge variant={ab.severity === "높음" ? "destructive" : ab.severity === "보통" ? "default" : "secondary"}>
                    {ab.severity}
                  </Badge>
                  <div>
                    <div className="font-medium text-sm">{formatMonth(ab.billingMonth)}</div>
                    <ul className="text-sm text-gray-600 mt-1">
                      {ab.reasons.map((r, i) => (
                        <li key={i}>- {r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Insights */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">분석 인사이트</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {insights.map((group) => (
              <div key={group.category}>
                <h4 className="text-sm font-semibold text-gray-800 mb-1">{group.category}</h4>
                <ul className="space-y-1">
                  {group.items.map((item, i) => (
                    <li key={i} className="text-sm text-gray-600">- {item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Month-over-Month Changes */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">전월대비 변동</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="p-2 text-left">월</th>
                <th className="p-2 text-right">사용량</th>
                <th className="p-2 text-right">사용량 변동</th>
                <th className="p-2 text-right">요금</th>
                <th className="p-2 text-right">요금 변동</th>
                <th className="p-2 text-right">단가 변동</th>
              </tr>
            </thead>
            <tbody>
              {monthlyChanges.map((mc) => (
                <tr key={mc.billingMonth} className="border-b">
                  <td className="p-2">{formatMonth(mc.billingMonth)}</td>
                  <td className="p-2 text-right">{formatKwh(mc.usageKwh)}</td>
                  <td className={`p-2 text-right ${mc.usageChangePercent != null && mc.usageChangePercent > 0 ? "text-red-600" : "text-blue-600"}`}>
                    {mc.usageChangePercent != null ? formatPercent(mc.usageChangePercent) : "-"}
                  </td>
                  <td className="p-2 text-right">{formatWon(mc.totalBillKrw)}</td>
                  <td className={`p-2 text-right ${mc.billChangePercent != null && mc.billChangePercent > 0 ? "text-red-600" : "text-blue-600"}`}>
                    {mc.billChangePercent != null ? formatPercent(mc.billChangePercent) : "-"}
                  </td>
                  <td className={`p-2 text-right ${mc.costPerKwhChangePercent != null && mc.costPerKwhChangePercent > 0 ? "text-red-600" : "text-blue-600"}`}>
                    {mc.costPerKwhChangePercent != null ? formatPercent(mc.costPerKwhChangePercent) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">추천 다음 단계</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {recommendations.map((rec) => (
              <div key={rec.type} className="border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={rec.priority === "높음" ? "destructive" : rec.priority === "중간" ? "default" : "secondary"}>
                    우선순위: {rec.priority}
                  </Badge>
                  <h4 className="font-semibold text-sm">{rec.title}</h4>
                </div>
                <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div>
                    <div className="font-medium text-gray-700 mb-1">필요 데이터</div>
                    {rec.requiredData.map((d, i) => (
                      <div key={i} className="text-gray-500">- {d}</div>
                    ))}
                  </div>
                  <div>
                    <div className="font-medium text-gray-700 mb-1">예상 다음 단계</div>
                    {rec.nextSteps.map((s, i) => (
                      <div key={i} className="text-gray-500">- {s}</div>
                    ))}
                  </div>
                  <div>
                    <div className="font-medium text-gray-700 mb-1">예상 산출물</div>
                    {rec.expectedDeliverables.map((d, i) => (
                      <div key={i} className="text-gray-500">- {d}</div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Limitations */}
      <Card className="mb-6 border-gray-300">
        <CardContent className="pt-6">
          <div className="text-xs text-gray-500 font-medium mb-2">예비진단 한계</div>
          <p className="text-sm text-gray-600">{snapshot.limitationsText}</p>
          <div className="mt-2 flex gap-4 text-xs text-gray-400">
            <span>데이터 완성도: {snapshot.inputCompletenessScore}/100</span>
            <span>분석 신뢰도: {snapshot.confidenceScore.toFixed(0)}/100</span>
          </div>
        </CardContent>
      </Card>

      {/* Consultant Notes */}
      <Card className="mb-6 border-blue-200 bg-blue-50/30">
        <CardHeader>
          <CardTitle className="text-base text-blue-800">컨설턴트 메모 / 보완 의견</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-gray-500 mb-3">
            이 내용은 보고서의 &ldquo;컨설턴트 종합 의견&rdquo; 항목에 포함됩니다.
          </p>
          <Textarea
            value={consultantNotes}
            onChange={(e) => setConsultantNotes(e.target.value)}
            placeholder="고객사 현장 특이사항, 분석 보완 의견, 제안 방향 등을 자유롭게 입력하세요..."
            className="min-h-[120px] text-sm bg-white"
          />
          <div className="flex items-center gap-3 mt-3">
            <Button onClick={handleSaveNotes} disabled={saving} size="sm">
              {saving ? "저장 중..." : "저장"}
            </Button>
            {saveSuccess && (
              <span className="text-sm text-green-600">저장되었습니다.</span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Report Buttons */}
      <div className="flex justify-end gap-2 mb-8">
        <Link href={`/projects/${id}/report`}>
          <Button variant="outline">1페이지 요약 보고서</Button>
        </Link>
        <Link href={`/projects/${id}/report/detailed`}>
          <Button>상세 보고서</Button>
        </Link>
      </div>
    </div>
  );
}
