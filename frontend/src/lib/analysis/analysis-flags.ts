import type { BillRecord } from "./analysis-metrics";
import { getMonthNum } from "./analysis-metrics";

export interface AbnormalMonth {
  billingMonth: string;
  reasons: string[];
  severity: "높음" | "보통" | "낮음";
}

export interface BaselineCandidate {
  billingMonth: string;
  usageKwh: number;
  reason: string;
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function getSeason(month: number): string {
  if ([6, 7, 8].includes(month)) return "summer";
  if ([12, 1, 2].includes(month)) return "winter";
  return "shoulder";
}

export function detectAbnormalMonths(bills: BillRecord[]): AbnormalMonth[] {
  if (bills.length < 3) return [];

  const abnormals: AbnormalMonth[] = [];

  const avgUsage = bills.reduce((s, b) => s + b.usageKwh, 0) / bills.length;
  const avgBill = bills.reduce((s, b) => s + b.totalBillKrw, 0) / bills.length;
  const costPerKwhs = bills.map((b) => (b.usageKwh > 0 ? b.totalBillKrw / b.usageKwh : 0));
  const medianCost = median(costPerKwhs);

  // Group by season for seasonal deviation
  const seasonGroups: Record<string, BillRecord[]> = {};
  for (const bill of bills) {
    const season = getSeason(getMonthNum(bill.billingMonth));
    if (!seasonGroups[season]) seasonGroups[season] = [];
    seasonGroups[season].push(bill);
  }

  const seasonAvg: Record<string, number> = {};
  for (const [season, group] of Object.entries(seasonGroups)) {
    seasonAvg[season] = group.reduce((s, b) => s + b.usageKwh, 0) / group.length;
  }

  for (const bill of bills) {
    const reasons: string[] = [];
    const costPerKwh = bill.usageKwh > 0 ? bill.totalBillKrw / bill.usageKwh : 0;
    const monthNum = getMonthNum(bill.billingMonth);
    const season = getSeason(monthNum);

    // 1. Annual average deviation > 30%
    const usageDeviation = Math.abs(bill.usageKwh - avgUsage) / avgUsage;
    if (usageDeviation > 0.3) {
      const direction = bill.usageKwh > avgUsage ? "증가" : "감소";
      reasons.push(`연평균 대비 사용량 ${(usageDeviation * 100).toFixed(0)}% ${direction}`);
    }

    // 2. Seasonal group internal deviation > 25%
    const sAvg = seasonAvg[season];
    if (sAvg > 0) {
      const seasonalDeviation = Math.abs(bill.usageKwh - sAvg) / sAvg;
      if (seasonalDeviation > 0.25) {
        reasons.push(`동일 계절군 내 사용량 편차 ${(seasonalDeviation * 100).toFixed(0)}%`);
      }
    }

    // 3. Bill-vs-usage divergence
    const billDeviation = Math.abs(bill.totalBillKrw - avgBill) / avgBill;
    if (usageDeviation > 0.05 && billDeviation > 0.05) {
      const divergence = Math.abs(billDeviation - usageDeviation);
      if (divergence > 0.15) {
        reasons.push("사용량 변동 대비 요금 변동폭 불일치");
      }
    }

    // 4. Cost per kWh deviation from median > 10%
    if (medianCost > 0) {
      const costDeviation = Math.abs(costPerKwh - medianCost) / medianCost;
      if (costDeviation > 0.10) {
        const direction = costPerKwh > medianCost ? "높음" : "낮음";
        reasons.push(`환산 청구단가 중앙값 대비 ${(costDeviation * 100).toFixed(0)}% ${direction}`);
      }
    }

    if (reasons.length > 0) {
      const severity = reasons.length >= 3 ? "높음" : reasons.length >= 2 ? "보통" : "낮음";
      abnormals.push({
        billingMonth: bill.billingMonth,
        reasons,
        severity,
      });
    }
  }

  return abnormals;
}

export function findBaselineCandidates(bills: BillRecord[]): BaselineCandidate[] {
  if (bills.length < 3) return [];

  const avgUsage = bills.reduce((s, b) => s + b.usageKwh, 0) / bills.length;
  const candidates: BaselineCandidate[] = [];

  // Prefer shoulder season months with low, stable usage
  const shoulderMonths = bills.filter((b) => {
    const m = getMonthNum(b.billingMonth);
    return [3, 4, 5, 9, 10, 11].includes(m);
  });

  const targetBills = shoulderMonths.length >= 2 ? shoulderMonths : bills;

  for (const bill of targetBills) {
    const deviation = Math.abs(bill.usageKwh - avgUsage) / avgUsage;

    if (bill.usageKwh <= avgUsage * 1.05 && deviation < 0.25) {
      const reasons: string[] = [];
      const m = getMonthNum(bill.billingMonth);

      if ([3, 4, 5, 9, 10, 11].includes(m)) {
        reasons.push("중간기(계절전환기) 해당");
      }
      if (bill.usageKwh <= avgUsage * 0.9) {
        reasons.push("평균 이하 사용량");
      }
      reasons.push("상대적으로 안정적인 사용 패턴");

      candidates.push({
        billingMonth: bill.billingMonth,
        usageKwh: bill.usageKwh,
        reason: reasons.join(", "),
      });
    }
  }

  return candidates.sort((a, b) => a.usageKwh - b.usageKwh).slice(0, 3);
}
