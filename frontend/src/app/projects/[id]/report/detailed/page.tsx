"use client";

import { useEffect, useState, use } from "react";
import { formatWon, formatKwh, formatMonth, formatCostPerKwh, formatPercent } from "@/lib/utils/format";
import type { AbnormalMonth } from "@/lib/analysis/analysis-flags";
import type { Recommendation } from "@/lib/analysis/analysis-recommendations";
import type { InsightGroup } from "@/lib/analysis/analysis-insights";
import type { MonthlyChange } from "@/lib/analysis/analysis-metrics";

interface ReportConfig {
  companyName: string;
  consultantName: string | null;
  footerText: string | null;
}

export default function DetailedReportPage({ params }: { params: Promise<{ id: string }> }) {
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
  const monthlyChanges: MonthlyChange[] = JSON.parse(snapshot.monthlyChangesJson);
  const bills = project.monthlyBills.sort((a: any, b: any) => a.billingMonth.localeCompare(b.billingMonth));

  const today = new Date().toLocaleDateString("ko-KR", { year: "numeric", month: "long", day: "numeric" });
  const companyName = config?.companyName || "브링 에너지";
  const consultantName = config?.consultantName || "";

  const strengthLabel =
    snapshot.seasonalStrengthRatio < 1.2 ? "약함" :
    snapshot.seasonalStrengthRatio < 1.5 ? "보통" : "강함";

  const PageFooter = ({ page }: { page: number }) => (
    <div className="mt-auto pt-4 border-t text-xs text-gray-400 flex justify-between">
      <span>{companyName}{consultantName ? ` | ${consultantName}` : ""}</span>
      <span>{page} / 5</span>
    </div>
  );

  return (
    <div className="bg-white min-h-screen">
      {/* Print button */}
      <div className="print:hidden fixed top-4 right-4 flex gap-2 z-50">
        <button onClick={() => window.print()} className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700">
          PDF 내보내기 / 인쇄
        </button>
        <button onClick={() => window.history.back()} className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm hover:bg-gray-300">
          돌아가기
        </button>
      </div>

      {/* PAGE 1: 개요 */}
      <div className="mx-auto max-w-[210mm] min-h-[297mm] p-[20mm] print:p-[15mm] print:max-w-none flex flex-col print:break-after-page">
        <div className="border-b-2 border-blue-600 pb-4 mb-6">
          <h1 className="text-2xl font-bold">전기요금 기반 예비진단 보고서</h1>
          <p className="text-sm text-gray-500 mt-1">12개월 청구서 분석 기반 절감 가능성 예비진단</p>
        </div>

        <h2 className="text-lg font-semibold mb-4">1. 개요</h2>

        <div className="mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">분석 목적</h3>
          <p className="text-sm text-gray-600">
            월별 전기요금 청구서 데이터를 기반으로 전력 사용 패턴을 분석하고, 계절성, 이상 변동, 비용구조를 검토하여 추가 진단 및 절감 기회 확인의 필요성을 판단합니다.
          </p>
        </div>

        <div className="mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">대상 정보</h3>
          <table className="text-sm w-full">
            <tbody>
              <tr className="border-b"><td className="py-1 text-gray-500 w-32">고객사</td><td className="py-1 font-medium">{project.customerName}</td></tr>
              <tr className="border-b"><td className="py-1 text-gray-500">건물유형</td><td className="py-1">{project.buildingType}</td></tr>
              <tr className="border-b"><td className="py-1 text-gray-500">건물명</td><td className="py-1">{project.buildingName}</td></tr>
              {project.totalAreaM2 && <tr className="border-b"><td className="py-1 text-gray-500">연면적</td><td className="py-1">{project.totalAreaM2.toLocaleString()} m²</td></tr>}
              {project.hvacType && <tr className="border-b"><td className="py-1 text-gray-500">냉난방방식</td><td className="py-1">{project.hvacType}</td></tr>}
            </tbody>
          </table>
        </div>

        <div className="mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">사용 데이터 범위</h3>
          <p className="text-sm text-gray-600">
            {bills.length > 0 ? `${formatMonth(bills[0].billingMonth)} ~ ${formatMonth(bills[bills.length - 1].billingMonth)} (${bills.length}개월)` : "데이터 없음"}
          </p>
        </div>

        <div className="mb-4 bg-yellow-50 p-3 rounded-md">
          <h3 className="text-sm font-semibold text-yellow-800 mb-1">분석 한계</h3>
          <p className="text-xs text-yellow-700">{snapshot.limitationsText}</p>
        </div>

        <div className="grid grid-cols-4 gap-3 mb-4">
          {[
            { label: "연간 총 사용량", value: formatKwh(snapshot.annualUsageKwh) },
            { label: "연간 총 요금", value: formatWon(snapshot.annualBillKrw) },
            { label: "월 평균 사용량", value: formatKwh(snapshot.averageMonthlyUsageKwh) },
            { label: "평균 환산 청구단가", value: formatCostPerKwh(snapshot.averageCostPerKwh) },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-gray-50 p-3 rounded-md text-center">
              <div className="text-xs text-gray-500">{kpi.label}</div>
              <div className="text-base font-bold mt-1">{kpi.value}</div>
            </div>
          ))}
        </div>

        <PageFooter page={1} />
      </div>

      {/* PAGE 2: 월별 추이 */}
      <div className="mx-auto max-w-[210mm] min-h-[297mm] p-[20mm] print:p-[15mm] print:max-w-none flex flex-col print:break-after-page">
        <h2 className="text-lg font-semibold mb-4">2. 월별 전력 사용 및 요금 추이</h2>

        <table className="w-full text-xs mb-6">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="p-1.5 text-left">청구월</th>
              <th className="p-1.5 text-right">사용량(kWh)</th>
              <th className="p-1.5 text-right">전월대비</th>
              <th className="p-1.5 text-right">청구금액(원)</th>
              <th className="p-1.5 text-right">전월대비</th>
              <th className="p-1.5 text-right">환산단가</th>
            </tr>
          </thead>
          <tbody>
            {monthlyChanges.map((mc) => (
              <tr key={mc.billingMonth} className="border-b">
                <td className="p-1.5">{formatMonth(mc.billingMonth)}</td>
                <td className="p-1.5 text-right">{formatKwh(mc.usageKwh)}</td>
                <td className={`p-1.5 text-right ${mc.usageChangePercent != null && mc.usageChangePercent > 0 ? "text-red-600" : "text-blue-600"}`}>
                  {mc.usageChangePercent != null ? formatPercent(mc.usageChangePercent) : "-"}
                </td>
                <td className="p-1.5 text-right">{formatWon(mc.totalBillKrw)}</td>
                <td className={`p-1.5 text-right ${mc.billChangePercent != null && mc.billChangePercent > 0 ? "text-red-600" : "text-blue-600"}`}>
                  {mc.billChangePercent != null ? formatPercent(mc.billChangePercent) : "-"}
                </td>
                <td className="p-1.5 text-right">{formatCostPerKwh(mc.costPerKwh)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {insights.slice(0, 2).map((group) => (
          <div key={group.category} className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-1">{group.category}</h3>
            <ul className="text-xs text-gray-600 space-y-1">
              {group.items.map((item, i) => (
                <li key={i}>- {item}</li>
              ))}
            </ul>
          </div>
        ))}

        <PageFooter page={2} />
      </div>

      {/* PAGE 3: 계절성 및 이상월 */}
      <div className="mx-auto max-w-[210mm] min-h-[297mm] p-[20mm] print:p-[15mm] print:max-w-none flex flex-col print:break-after-page">
        <h2 className="text-lg font-semibold mb-4">3. 계절성 및 이상월 분석</h2>

        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">계절별 비교</h3>
          <table className="w-full text-sm mb-4">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="p-2 text-left">구분</th>
                <th className="p-2 text-left">해당 월</th>
                <th className="p-2 text-right">평균 사용량</th>
                <th className="p-2 text-right">평균 요금</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="p-2 font-medium">하절기</td>
                <td className="p-2 text-gray-500">6, 7, 8월</td>
                <td className="p-2 text-right">{formatKwh(snapshot.summerAvgUsage)}</td>
                <td className="p-2 text-right">{formatWon(snapshot.summerAvgBill)}</td>
              </tr>
              <tr className="border-b">
                <td className="p-2 font-medium">동절기</td>
                <td className="p-2 text-gray-500">12, 1, 2월</td>
                <td className="p-2 text-right">{formatKwh(snapshot.winterAvgUsage)}</td>
                <td className="p-2 text-right">{formatWon(snapshot.winterAvgBill)}</td>
              </tr>
              <tr className="border-b">
                <td className="p-2 font-medium">중간기</td>
                <td className="p-2 text-gray-500">3, 4, 5, 9, 10, 11월</td>
                <td className="p-2 text-right">{formatKwh(snapshot.shoulderAvgUsage)}</td>
                <td className="p-2 text-right">{formatWon(snapshot.shoulderAvgBill)}</td>
              </tr>
            </tbody>
          </table>
          <p className="text-xs text-gray-600">
            계절 강도 비율: <strong>{snapshot.seasonalStrengthRatio.toFixed(2)}</strong> ({strengthLabel})
            {snapshot.seasonalStrengthRatio >= 1.5 && " — 계절 변동이 뚜렷하여 냉난방 부하 영향 가능성이 높습니다."}
          </p>
        </div>

        {abnormals.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">특이월 후보</h3>
            <div className="space-y-2">
              {abnormals.map((ab) => (
                <div key={ab.billingMonth} className="bg-yellow-50 p-3 rounded-md text-sm">
                  <div className="flex items-center gap-2 mb-1">
                    <strong>{formatMonth(ab.billingMonth)}</strong>
                    <span className={`text-xs px-2 py-0.5 rounded ${ab.severity === "높음" ? "bg-red-100 text-red-700" : ab.severity === "보통" ? "bg-yellow-100 text-yellow-700" : "bg-gray-100 text-gray-700"}`}>
                      {ab.severity}
                    </span>
                  </div>
                  <ul className="text-xs text-gray-600">
                    {ab.reasons.map((r, i) => (
                      <li key={i}>- {r}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {insights.find((g) => g.category === "특이월 분석") && (
          <div className="mb-4">
            <ul className="text-xs text-gray-600 space-y-1">
              {insights.find((g) => g.category === "특이월 분석")!.items.map((item, i) => (
                <li key={i}>- {item}</li>
              ))}
            </ul>
          </div>
        )}

        <PageFooter page={3} />
      </div>

      {/* PAGE 4: 요금 구조 */}
      <div className="mx-auto max-w-[210mm] min-h-[297mm] p-[20mm] print:p-[15mm] print:max-w-none flex flex-col print:break-after-page">
        <h2 className="text-lg font-semibold mb-4">4. 요금 구조 해석</h2>

        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">월별 환산 청구단가</h3>
          <table className="w-full text-xs mb-4">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="p-1.5 text-left">청구월</th>
                <th className="p-1.5 text-right">사용량</th>
                <th className="p-1.5 text-right">청구금액</th>
                <th className="p-1.5 text-right">환산 청구단가</th>
                <th className="p-1.5 text-right">단가 변동</th>
              </tr>
            </thead>
            <tbody>
              {monthlyChanges.map((mc) => (
                <tr key={mc.billingMonth} className="border-b">
                  <td className="p-1.5">{formatMonth(mc.billingMonth)}</td>
                  <td className="p-1.5 text-right">{formatKwh(mc.usageKwh)}</td>
                  <td className="p-1.5 text-right">{formatWon(mc.totalBillKrw)}</td>
                  <td className="p-1.5 text-right">{formatCostPerKwh(mc.costPerKwh)}</td>
                  <td className={`p-1.5 text-right ${mc.costPerKwhChangePercent != null && mc.costPerKwhChangePercent > 0 ? "text-red-600" : "text-blue-600"}`}>
                    {mc.costPerKwhChangePercent != null ? formatPercent(mc.costPerKwhChangePercent) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Charge breakdown if available */}
        {bills.some((b: any) => b.basicChargeKrw != null) && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">요금 항목 구성</h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="p-1.5 text-left">청구월</th>
                  <th className="p-1.5 text-right">기본요금</th>
                  <th className="p-1.5 text-right">전력량요금</th>
                  <th className="p-1.5 text-right">기후환경</th>
                  <th className="p-1.5 text-right">연료비조정</th>
                  <th className="p-1.5 text-right">부가세</th>
                </tr>
              </thead>
              <tbody>
                {bills.map((b: any) => (
                  <tr key={b.billingMonth} className="border-b">
                    <td className="p-1.5">{formatMonth(b.billingMonth)}</td>
                    <td className="p-1.5 text-right">{b.basicChargeKrw != null ? formatWon(b.basicChargeKrw) : "-"}</td>
                    <td className="p-1.5 text-right">{b.energyChargeKrw != null ? formatWon(b.energyChargeKrw) : "-"}</td>
                    <td className="p-1.5 text-right">{b.climateChargeKrw != null ? formatWon(b.climateChargeKrw) : "-"}</td>
                    <td className="p-1.5 text-right">{b.fuelAdjustmentKrw != null ? formatWon(b.fuelAdjustmentKrw) : "-"}</td>
                    <td className="p-1.5 text-right">{b.vatKrw != null ? formatWon(b.vatKrw) : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="text-xs text-gray-600">
          <p>* 환산 청구단가는 총 청구금액을 총 사용량으로 나눈 참고 지표이며, 실제 적용 요금단가와 다를 수 있습니다.</p>
          <p>* 정확한 요금구조 분석을 위해서는 계약전력, 최대수요전력, 적용 요금제 정보가 필요합니다.</p>
        </div>

        <PageFooter page={4} />
      </div>

      {/* PAGE 5: 다음 단계 */}
      <div className="mx-auto max-w-[210mm] min-h-[297mm] p-[20mm] print:p-[15mm] print:max-w-none flex flex-col">
        <h2 className="text-lg font-semibold mb-4">5. 추가 데이터 요청 및 다음 단계 제안</h2>

        {/* Data needs */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">추가 확보 필요 데이터</h3>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="bg-gray-50 p-3 rounded-md">
              <div className="font-medium mb-1">운영 데이터</div>
              <ul className="text-gray-600 space-y-0.5">
                <li>- 연간 운영 일정 (방학, 시험, 행사)</li>
                <li>- 냉난방 운영 일정 및 설정 온도</li>
                <li>- 주요 설비 가동 일정</li>
                <li>- 최근 시설 변경 이력</li>
              </ul>
            </div>
            <div className="bg-gray-50 p-3 rounded-md">
              <div className="font-medium mb-1">계측 데이터</div>
              <ul className="text-gray-600 space-y-0.5">
                <li>- 전력 계통도 (단선도)</li>
                <li>- 주요 회로 부하 목록</li>
                <li>- CT 설치 가능 위치</li>
                <li>- 계약전력 및 최대수요전력</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">다음 단계 제안</h3>
          <div className="space-y-3">
            {recommendations.map((rec) => (
              <div key={rec.type} className="border rounded-md p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs px-2 py-0.5 rounded ${rec.priority === "높음" ? "bg-red-100 text-red-700" : rec.priority === "중간" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-700"}`}>
                    우선순위: {rec.priority}
                  </span>
                  <strong className="text-sm">{rec.title}</strong>
                </div>
                <p className="text-xs text-gray-600 mb-2">{rec.description}</p>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <div className="font-medium text-gray-700">예상 다음 단계</div>
                    {rec.nextSteps.map((s, i) => (
                      <div key={i} className="text-gray-500">- {s}</div>
                    ))}
                  </div>
                  <div>
                    <div className="font-medium text-gray-700">예상 산출물</div>
                    {rec.expectedDeliverables.map((d, i) => (
                      <div key={i} className="text-gray-500">- {d}</div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Final disclaimer */}
        <div className="mt-auto">
          <div className="bg-gray-50 p-3 rounded-md text-xs text-gray-500 mb-4">
            <p className="font-medium mb-1">면책 조항</p>
            <p>본 보고서는 월별 전기요금 청구서 기반 예비진단 결과이며, 회로별 실측 및 운영정보 확인 전 단계의 참고자료입니다. 보고서의 분석 내용은 제공된 데이터의 정확성에 의존하며, 실제 절감 효과는 현장 상황에 따라 달라질 수 있습니다.</p>
          </div>
          <div className="pt-2 border-t text-xs text-gray-400 flex justify-between">
            <span>{companyName}{consultantName ? ` | 작성자: ${consultantName}` : ""} | {today}</span>
            <span>5 / 5</span>
          </div>
        </div>
      </div>
    </div>
  );
}
