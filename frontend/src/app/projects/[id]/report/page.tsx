"use client";

import { useEffect, useState, use } from "react";
import { formatWon, formatKwh, formatMonth, formatCostPerKwh } from "@/lib/utils/format";
import type { AbnormalMonth } from "@/lib/analysis/analysis-flags";
import type { Recommendation } from "@/lib/analysis/analysis-recommendations";
import type { InsightGroup } from "@/lib/analysis/analysis-insights";

interface ReportConfig {
  companyName: string;
  consultantName: string | null;
  footerText: string | null;
}

export default function ReportSummaryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [project, setProject] = useState<any>(null);
  const [config, setConfig] = useState<ReportConfig | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`/api/projects/${id}`).then((r) => r.json()),
      fetch("/api/report-config").then((r) => r.json()),
    ]).then(([proj, cfg]) => {
      setProject(proj);
      setConfig(cfg);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <div className="text-center py-12">불러오는 중...</div>;
  if (!project) return <div className="text-center py-12">프로젝트를 찾을 수 없습니다</div>;

  const snapshot = project.analysisSnapshots?.[0];
  if (!snapshot) return <div className="text-center py-12">분석 결과가 없습니다</div>;

  const insights: InsightGroup[] = JSON.parse(snapshot.insightsJson);
  const recommendations: Recommendation[] = JSON.parse(snapshot.recommendationJson);
  const abnormals: AbnormalMonth[] = JSON.parse(snapshot.abnormalMonthsJson);

  const keyFindings = insights.flatMap((g) => g.items).slice(0, 3);
  const topRec = recommendations[0];
  const today = new Date().toLocaleDateString("ko-KR", { year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="bg-white min-h-screen">
      {/* Print button - hidden on print */}
      <div className="print:hidden fixed top-4 right-4 flex gap-2 z-50">
        <button
          onClick={() => window.print()}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
        >
          PDF 내보내기 / 인쇄
        </button>
        <button
          onClick={() => window.history.back()}
          className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm hover:bg-gray-300"
        >
          돌아가기
        </button>
      </div>

      {/* A4 Page */}
      <div className="mx-auto max-w-[210mm] min-h-[297mm] p-[20mm] print:p-[15mm] print:max-w-none">
        {/* Header */}
        <div className="border-b-2 border-blue-600 pb-4 mb-6">
          <h1 className="text-2xl font-bold text-gray-900">전기요금 기반 예비진단 보고서</h1>
          <p className="text-sm text-gray-500 mt-1">12개월 청구서 분석 기반 절감 가능성 예비진단</p>
        </div>

        {/* Project Info */}
        <div className="grid grid-cols-2 gap-x-8 gap-y-2 mb-6 text-sm">
          <div><span className="text-gray-500">고객사:</span> <strong>{project.customerName}</strong></div>
          <div><span className="text-gray-500">건물:</span> <strong>{project.buildingType} - {project.buildingName}</strong></div>
          <div><span className="text-gray-500">프로젝트:</span> {project.projectName}</div>
          <div><span className="text-gray-500">보고서 일자:</span> {today}</div>
        </div>

        {/* KPI Summary */}
        <div className="grid grid-cols-4 gap-3 mb-6">
          {[
            { label: "연간 총 사용량", value: formatKwh(snapshot.annualUsageKwh) },
            { label: "연간 총 요금", value: formatWon(snapshot.annualBillKrw) },
            { label: "월 평균 사용량", value: formatKwh(snapshot.averageMonthlyUsageKwh) },
            { label: "평균 환산 청구단가", value: formatCostPerKwh(snapshot.averageCostPerKwh) },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-gray-50 p-3 rounded-md text-center">
              <div className="text-xs text-gray-500">{kpi.label}</div>
              <div className="text-lg font-bold mt-1">{kpi.value}</div>
            </div>
          ))}
        </div>

        {/* Peak/Min Summary */}
        <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
          <div className="bg-blue-50 p-3 rounded-md">
            <div className="text-xs text-gray-500">최고 사용월</div>
            <div className="font-semibold">{formatMonth(snapshot.maxUsageMonth)} - {formatKwh(snapshot.maxUsageValue)}</div>
          </div>
          <div className="bg-green-50 p-3 rounded-md">
            <div className="text-xs text-gray-500">최저 사용월</div>
            <div className="font-semibold">{formatMonth(snapshot.minUsageMonth)} - {formatKwh(snapshot.minUsageValue)}</div>
          </div>
        </div>

        {/* Key Findings */}
        <div className="mb-6">
          <h2 className="text-base font-semibold text-gray-900 mb-3 border-b pb-1">핵심 발견사항</h2>
          <ol className="space-y-2 text-sm text-gray-700">
            {keyFindings.map((finding, i) => (
              <li key={i} className="flex gap-2">
                <span className="flex-shrink-0 w-5 h-5 bg-blue-600 text-white rounded-full text-xs flex items-center justify-center">{i + 1}</span>
                <span>{finding}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Abnormal Months */}
        {abnormals.length > 0 && (
          <div className="mb-6">
            <h2 className="text-base font-semibold text-gray-900 mb-3 border-b pb-1">특이월 후보</h2>
            <div className="text-sm space-y-1 text-gray-700">
              {abnormals.slice(0, 3).map((ab) => (
                <div key={ab.billingMonth}>
                  <strong>{formatMonth(ab.billingMonth)}</strong>: {ab.reasons.slice(0, 2).join(", ")}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Next Step */}
        {topRec && (
          <div className="mb-6">
            <h2 className="text-base font-semibold text-gray-900 mb-3 border-b pb-1">추천 다음 단계</h2>
            <div className="bg-blue-50 p-4 rounded-md text-sm">
              <div className="font-semibold mb-1">{topRec.title} (우선순위: {topRec.priority})</div>
              <p className="text-gray-600">{topRec.description}</p>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-8 pt-4 border-t text-xs text-gray-400">
          <p className="mb-1">
            본 보고서는 월별 전기요금 청구서 기반 예비진단 결과이며, 회로별 실측 및 운영정보 확인 전 단계의 참고자료입니다.
          </p>
          <p>데이터 완성도: {snapshot.inputCompletenessScore}/100 | 분석 신뢰도: {snapshot.confidenceScore.toFixed(0)}/100</p>
        </div>

        {/* Footer */}
        <div className="mt-4 pt-2 border-t text-xs text-gray-400 flex justify-between">
          <span>{config?.companyName || "브링 에너지"}{config?.consultantName ? ` | ${config.consultantName}` : ""}</span>
          <span>{config?.footerText || "전기요금 기반 예비진단 및 다음 단계 제안 도구"}</span>
        </div>
      </div>
    </div>
  );
}
