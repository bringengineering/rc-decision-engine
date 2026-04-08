import type { MonthlyBillInput } from "./validation";

export interface DataQualityResult {
  completenessScore: number;
  status: "분석 가능" | "주의 필요" | "보완 필요";
  warnings: string[];
  missingMonths: number;
  duplicateMonths: string[];
  hasChargeBreakdown: boolean;
}

export function evaluateDataQuality(bills: MonthlyBillInput[]): DataQualityResult {
  const warnings: string[] = [];
  let score = 0;

  // Check 12 months present
  if (bills.length === 12) {
    score += 30;
  } else if (bills.length >= 10) {
    score += 20;
    warnings.push(`${12 - bills.length}개월 데이터가 부족합니다 (${bills.length}/12개월)`);
  } else {
    score += Math.max(0, bills.length * 2);
    warnings.push(`데이터가 크게 부족합니다 (${bills.length}/12개월)`);
  }

  // Check duplicates
  const months = bills.map((b) => b.billingMonth);
  const duplicates = months.filter((m, i) => months.indexOf(m) !== i);
  if (duplicates.length > 0) {
    warnings.push(`중복된 청구월: ${duplicates.join(", ")}`);
  } else {
    score += 10;
  }

  // Check core fields present
  const coreComplete = bills.every((b) => b.usageKwh > 0 && b.totalBillKrw > 0);
  if (coreComplete) {
    score += 25;
  } else {
    const incomplete = bills.filter((b) => !b.usageKwh || !b.totalBillKrw);
    warnings.push(`${incomplete.length}개월의 핵심 데이터(사용량/요금)가 불완전합니다`);
    score += 10;
  }

  // Check charge breakdown completeness
  const withBreakdown = bills.filter(
    (b) => b.basicChargeKrw != null && b.energyChargeKrw != null
  );
  const hasChargeBreakdown = withBreakdown.length >= bills.length * 0.8;
  if (hasChargeBreakdown) {
    score += 15;
  } else if (withBreakdown.length > 0) {
    score += 8;
    warnings.push("요금 내역(기본요금, 전력량요금 등)이 일부 누락되어 요금구조 분석이 제한됩니다");
  } else {
    warnings.push("요금 내역이 없어 요금구조 분석을 수행할 수 없습니다");
  }

  // Check chronological order
  const sorted = [...months].sort();
  const isChronological = months.every((m, i) => i === 0 || m >= months[i - 1]);
  if (isChronological) {
    score += 10;
  } else {
    warnings.push("청구월이 시간순으로 정렬되어 있지 않습니다");
  }

  // Check for suspicious outliers
  if (bills.length >= 3) {
    const usages = bills.map((b) => b.usageKwh);
    const avg = usages.reduce((a, b) => a + b, 0) / usages.length;
    const extremeOutliers = bills.filter(
      (b) => b.usageKwh > avg * 3 || b.usageKwh < avg * 0.1
    );
    if (extremeOutliers.length > 0) {
      warnings.push(
        `극단적 이상값이 의심되는 월이 있습니다: ${extremeOutliers.map((b) => b.billingMonth).join(", ")}`
      );
    } else {
      score += 10;
    }
  }

  score = Math.min(100, score);

  let status: DataQualityResult["status"];
  if (score >= 70) {
    status = "분석 가능";
  } else if (score >= 40) {
    status = "주의 필요";
  } else {
    status = "보완 필요";
  }

  return {
    completenessScore: score,
    status,
    warnings,
    missingMonths: Math.max(0, 12 - bills.length),
    duplicateMonths: duplicates,
    hasChargeBreakdown,
  };
}
