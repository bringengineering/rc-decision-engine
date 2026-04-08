export interface BillRecord {
  billingMonth: string;
  usageKwh: number;
  totalBillKrw: number;
  basicChargeKrw?: number | null;
  energyChargeKrw?: number | null;
  climateChargeKrw?: number | null;
  fuelAdjustmentKrw?: number | null;
  vatKrw?: number | null;
}

export interface BasicMetrics {
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
}

export interface MonthlyChange {
  billingMonth: string;
  usageKwh: number;
  totalBillKrw: number;
  costPerKwh: number;
  usageChangePercent: number | null;
  billChangePercent: number | null;
  costPerKwhChangePercent: number | null;
}

export interface SeasonalMetrics {
  seasonalStrengthRatio: number;
  summerAvgUsage: number;
  winterAvgUsage: number;
  shoulderAvgUsage: number;
  summerAvgBill: number;
  winterAvgBill: number;
  shoulderAvgBill: number;
}

type Season = "summer" | "winter" | "shoulder";

function getSeason(month: number): Season {
  if ([6, 7, 8].includes(month)) return "summer";
  if ([12, 1, 2].includes(month)) return "winter";
  return "shoulder";
}

export function getMonthNum(yearMonth: string): number {
  return parseInt(yearMonth.split("-")[1]);
}

export function calculateBasicMetrics(bills: BillRecord[]): BasicMetrics {
  const sorted = [...bills].sort((a, b) => a.billingMonth.localeCompare(b.billingMonth));

  const annualUsageKwh = sorted.reduce((sum, b) => sum + b.usageKwh, 0);
  const annualBillKrw = sorted.reduce((sum, b) => sum + b.totalBillKrw, 0);
  const count = sorted.length;

  const averageMonthlyUsageKwh = annualUsageKwh / count;
  const averageMonthlyBillKrw = annualBillKrw / count;
  const averageCostPerKwh = annualUsageKwh > 0 ? annualBillKrw / annualUsageKwh : 0;

  const maxUsage = sorted.reduce((max, b) => (b.usageKwh > max.usageKwh ? b : max));
  const minUsage = sorted.reduce((min, b) => (b.usageKwh < min.usageKwh ? b : min));
  const maxBill = sorted.reduce((max, b) => (b.totalBillKrw > max.totalBillKrw ? b : max));
  const minBill = sorted.reduce((min, b) => (b.totalBillKrw < min.totalBillKrw ? b : min));

  return {
    annualUsageKwh,
    annualBillKrw,
    averageMonthlyUsageKwh,
    averageMonthlyBillKrw,
    averageCostPerKwh,
    maxUsageMonth: maxUsage.billingMonth,
    maxUsageValue: maxUsage.usageKwh,
    minUsageMonth: minUsage.billingMonth,
    minUsageValue: minUsage.usageKwh,
    maxBillMonth: maxBill.billingMonth,
    maxBillValue: maxBill.totalBillKrw,
    minBillMonth: minBill.billingMonth,
    minBillValue: minBill.totalBillKrw,
  };
}

export function calculateMonthlyChanges(bills: BillRecord[]): MonthlyChange[] {
  const sorted = [...bills].sort((a, b) => a.billingMonth.localeCompare(b.billingMonth));

  return sorted.map((bill, i) => {
    const costPerKwh = bill.usageKwh > 0 ? bill.totalBillKrw / bill.usageKwh : 0;
    if (i === 0) {
      return {
        billingMonth: bill.billingMonth,
        usageKwh: bill.usageKwh,
        totalBillKrw: bill.totalBillKrw,
        costPerKwh,
        usageChangePercent: null,
        billChangePercent: null,
        costPerKwhChangePercent: null,
      };
    }
    const prev = sorted[i - 1];
    const prevCostPerKwh = prev.usageKwh > 0 ? prev.totalBillKrw / prev.usageKwh : 0;

    return {
      billingMonth: bill.billingMonth,
      usageKwh: bill.usageKwh,
      totalBillKrw: bill.totalBillKrw,
      costPerKwh,
      usageChangePercent: prev.usageKwh > 0
        ? ((bill.usageKwh - prev.usageKwh) / prev.usageKwh) * 100
        : null,
      billChangePercent: prev.totalBillKrw > 0
        ? ((bill.totalBillKrw - prev.totalBillKrw) / prev.totalBillKrw) * 100
        : null,
      costPerKwhChangePercent: prevCostPerKwh > 0
        ? ((costPerKwh - prevCostPerKwh) / prevCostPerKwh) * 100
        : null,
    };
  });
}

export function calculateSeasonalMetrics(bills: BillRecord[]): SeasonalMetrics {
  const groups: Record<Season, BillRecord[]> = {
    summer: [],
    winter: [],
    shoulder: [],
  };

  for (const bill of bills) {
    const month = getMonthNum(bill.billingMonth);
    groups[getSeason(month)].push(bill);
  }

  const avg = (arr: BillRecord[], key: "usageKwh" | "totalBillKrw") =>
    arr.length > 0 ? arr.reduce((s, b) => s + b[key], 0) / arr.length : 0;

  const summerAvgUsage = avg(groups.summer, "usageKwh");
  const winterAvgUsage = avg(groups.winter, "usageKwh");
  const shoulderAvgUsage = avg(groups.shoulder, "usageKwh");

  const allUsages = bills.map((b) => b.usageKwh);
  const maxUsage = Math.max(...allUsages);
  const minUsage = Math.min(...allUsages);
  const seasonalStrengthRatio = minUsage > 0 ? maxUsage / minUsage : 0;

  return {
    seasonalStrengthRatio,
    summerAvgUsage,
    winterAvgUsage,
    shoulderAvgUsage,
    summerAvgBill: avg(groups.summer, "totalBillKrw"),
    winterAvgBill: avg(groups.winter, "totalBillKrw"),
    shoulderAvgBill: avg(groups.shoulder, "totalBillKrw"),
  };
}
