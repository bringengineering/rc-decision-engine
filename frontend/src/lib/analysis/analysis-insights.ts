import type { BasicMetrics, SeasonalMetrics } from "./analysis-metrics";
import type { AbnormalMonth } from "./analysis-flags";
import { formatMonth, formatKwh, formatWon } from "../utils/format";

export interface InsightGroup {
  category: string;
  items: string[];
}

export function generateInsights(
  metrics: BasicMetrics,
  seasonal: SeasonalMetrics,
  abnormals: AbnormalMonth[],
  billCount: number,
  hasChargeBreakdown: boolean
): InsightGroup[] {
  const groups: InsightGroup[] = [];

  // 1. Overall Summary
  const overallItems: string[] = [];
  const strengthLabel =
    seasonal.seasonalStrengthRatio < 1.2
      ? "약한"
      : seasonal.seasonalStrengthRatio < 1.5
      ? "보통 수준의"
      : "뚜렷한";
  overallItems.push(
    `최근 ${billCount}개월 기준 전력 사용량의 계절성 변동이 ${strengthLabel} 수준으로 확인됩니다.`
  );

  if (seasonal.winterAvgUsage > seasonal.shoulderAvgUsage * 1.2) {
    overallItems.push(
      "동절기 사용량이 중간기 대비 높아 난방 또는 관련 부하 영향 가능성이 있습니다."
    );
  }
  if (seasonal.summerAvgUsage > seasonal.shoulderAvgUsage * 1.2) {
    overallItems.push(
      "하절기 사용량이 중간기 대비 높아 냉방 부하 영향 가능성이 있습니다."
    );
  }

  groups.push({ category: "전체 요약", items: overallItems });

  // 2. Peak/Trough Summary
  const peakItems: string[] = [];
  peakItems.push(
    `최고 사용월은 ${formatMonth(metrics.maxUsageMonth)}(${formatKwh(metrics.maxUsageValue)}), 최저 사용월은 ${formatMonth(metrics.minUsageMonth)}(${formatKwh(metrics.minUsageValue)})으로 확인됩니다.`
  );
  if (seasonal.seasonalStrengthRatio > 1.5) {
    peakItems.push(
      "피크월과 저부하월의 차이가 커 운영 패턴 변화 또는 냉난방 영향 검토가 필요합니다."
    );
  }
  peakItems.push(
    `최고 요금월은 ${formatMonth(metrics.maxBillMonth)}(${formatWon(metrics.maxBillValue)}), 최저 요금월은 ${formatMonth(metrics.minBillMonth)}(${formatWon(metrics.minBillValue)})입니다.`
  );
  groups.push({ category: "피크/저점 요약", items: peakItems });

  // 3. Abnormality Summary
  if (abnormals.length > 0) {
    const abnormalItems: string[] = [];
    for (const ab of abnormals.slice(0, 3)) {
      const reasonText = ab.reasons.slice(0, 2).join(", ");
      abnormalItems.push(
        `${formatMonth(ab.billingMonth)}은 특이월 후보로 확인됩니다 (${reasonText}). 운영 일정 또는 설비 운전 여부 확인이 필요합니다.`
      );
    }
    if (abnormals.length > 3) {
      abnormalItems.push(`외 ${abnormals.length - 3}개월 추가 확인 필요`);
    }
    groups.push({ category: "특이월 분석", items: abnormalItems });
  }

  // 4. Data Limitation
  const limitItems: string[] = [];
  limitItems.push(
    "현재 분석은 월별 청구서 기준 예비진단 수준이며, 회로별 원인 분석은 포함하지 않습니다."
  );
  limitItems.push(
    "시간대별 데이터가 없어 야간 기저부하 또는 피크 시간 원인 분석은 제한적입니다."
  );
  if (!hasChargeBreakdown) {
    limitItems.push("요금 내역(기본요금, 전력량요금 등)이 없어 요금구조 상세 분석이 제한됩니다.");
  }
  groups.push({ category: "현재 데이터 기준 분석 한계", items: limitItems });

  // 5. Next-Step Recommendation
  const nextItems: string[] = [];
  nextItems.push(
    "운영시간, 방학/시험기간, 냉난방 일정 확보 시 분석 정확도를 높일 수 있습니다."
  );
  if (seasonal.seasonalStrengthRatio > 1.3 || abnormals.length >= 2) {
    nextItems.push(
      "대표 회로 CT 계측을 통해 야간 기저부하 및 피크 발생 구간을 확인할 필요가 있습니다."
    );
  }
  nextItems.push(
    "월별 청구서 기반 분석 결과, 현장 인터뷰 및 단기 파일럿 진행 우선순위가 높습니다."
  );
  groups.push({ category: "추가 데이터 확보 및 다음 단계 제안", items: nextItems });

  return groups;
}

export function generateLimitationsText(
  hasChargeBreakdown: boolean,
  billCount: number,
  hasContractDemand: boolean
): string {
  const items: string[] = [];
  items.push("본 분석은 월별 전기요금 청구서 기반 예비진단 결과입니다.");

  if (billCount < 12) {
    items.push(`분석 대상 기간이 ${billCount}개월로 12개월 미만입니다.`);
  }
  if (!hasChargeBreakdown) {
    items.push("요금 내역 미제공으로 요금구조 상세 분석이 제한됩니다.");
  }
  if (!hasContractDemand) {
    items.push("계약전력 정보 미제공으로 환산 청구단가는 참고 수준입니다.");
  }
  items.push("회로별 실측 및 운영정보 확인 전 단계의 참고자료로 활용해주세요.");

  return items.join(" ");
}
