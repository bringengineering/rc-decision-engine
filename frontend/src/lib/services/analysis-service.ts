import { prisma } from "../db";
import {
  calculateBasicMetrics,
  calculateMonthlyChanges,
  calculateSeasonalMetrics,
  type BillRecord,
} from "../analysis/analysis-metrics";
import { detectAbnormalMonths, findBaselineCandidates } from "../analysis/analysis-flags";
import { generateInsights, generateLimitationsText } from "../analysis/analysis-insights";
import { generateRecommendations } from "../analysis/analysis-recommendations";
import { evaluateDataQuality } from "../utils/data-quality";

export async function runAnalysis(projectId: string) {
  const project = await prisma.project.findUnique({
    where: { id: projectId },
    include: { monthlyBills: true },
  });

  if (!project) throw new Error("프로젝트를 찾을 수 없습니다");
  if (project.monthlyBills.length < 3) {
    throw new Error("최소 3개월 이상의 데이터가 필요합니다");
  }

  const bills: BillRecord[] = project.monthlyBills.map((b) => ({
    billingMonth: b.billingMonth,
    usageKwh: b.usageKwh,
    totalBillKrw: b.totalBillKrw,
    basicChargeKrw: b.basicChargeKrw,
    energyChargeKrw: b.energyChargeKrw,
    climateChargeKrw: b.climateChargeKrw,
    fuelAdjustmentKrw: b.fuelAdjustmentKrw,
    vatKrw: b.vatKrw,
  }));

  const basicMetrics = calculateBasicMetrics(bills);
  const monthlyChanges = calculateMonthlyChanges(bills);
  const seasonalMetrics = calculateSeasonalMetrics(bills);
  const abnormalMonths = detectAbnormalMonths(bills);
  const baselineCandidates = findBaselineCandidates(bills);

  const dataQuality = evaluateDataQuality(
    project.monthlyBills.map((b) => ({
      billingMonth: b.billingMonth,
      usageKwh: b.usageKwh,
      totalBillKrw: b.totalBillKrw,
      basicChargeKrw: b.basicChargeKrw,
      energyChargeKrw: b.energyChargeKrw,
      climateChargeKrw: b.climateChargeKrw,
      fuelAdjustmentKrw: b.fuelAdjustmentKrw,
      vatKrw: b.vatKrw,
    }))
  );

  const hasOperationalInfo = !!(
    project.operatingHoursWeekday || project.vacationPeriods || project.hvacType
  );
  const hasChargeBreakdown = dataQuality.hasChargeBreakdown;
  const hasContractDemand = !!project.contractDemandKw;

  const insights = generateInsights(
    basicMetrics,
    seasonalMetrics,
    abnormalMonths,
    bills.length,
    hasChargeBreakdown
  );

  const recommendations = generateRecommendations(
    seasonalMetrics,
    abnormalMonths,
    bills.length,
    hasOperationalInfo
  );

  const limitationsText = generateLimitationsText(
    hasChargeBreakdown,
    bills.length,
    hasContractDemand
  );

  // Confidence score based on data quality and completeness
  const confidenceScore = Math.min(
    100,
    dataQuality.completenessScore * 0.6 +
      (bills.length >= 12 ? 25 : bills.length * 2) +
      (hasOperationalInfo ? 15 : 0)
  );

  const snapshot = await prisma.analysisSnapshot.create({
    data: {
      projectId,
      ...basicMetrics,
      ...seasonalMetrics,
      abnormalMonthsJson: JSON.stringify(abnormalMonths),
      insightsJson: JSON.stringify(insights),
      recommendationJson: JSON.stringify(recommendations),
      monthlyChangesJson: JSON.stringify(monthlyChanges),
      analysisVersion: "1.0",
      inputCompletenessScore: dataQuality.completenessScore,
      confidenceScore,
      limitationsText,
    },
  });

  await prisma.project.update({
    where: { id: projectId },
    data: {
      status: "analyzed",
      analysisVersion: "1.0",
    },
  });

  return {
    snapshot,
    abnormalMonths,
    baselineCandidates,
    insights,
    recommendations,
    dataQuality,
    monthlyChanges,
  };
}
