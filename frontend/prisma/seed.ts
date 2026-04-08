import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaLibSql } from "@prisma/adapter-libsql";
import { createClient } from "@libsql/client";

const libsql = createClient({ url: "file:dev.db" });
const adapter = new PrismaLibSql(libsql);
const prisma = new PrismaClient({ adapter });

async function main() {
  // Clean existing data
  await prisma.analysisSnapshot.deleteMany();
  await prisma.monthlyBillRecord.deleteMany();
  await prisma.project.deleteMany();
  await prisma.reportConfig.deleteMany();

  // Create report config
  await prisma.reportConfig.create({
    data: {
      companyName: "브링 에너지",
      consultantName: "김에너지",
      footerText: "전기요금 기반 예비진단 및 다음 단계 제안 도구",
    },
  });

  // Create demo project: Sangji University
  const project = await prisma.project.create({
    data: {
      projectName: "상지대학교 본관 전력 예비진단",
      customerName: "상지대학교",
      contactName: "김시설",
      contactPhone: "033-730-0000",
      contactEmail: "facility@sangji.ac.kr",
      buildingType: "학교",
      buildingName: "본관",
      campusOrSiteName: "상지대학교 원주캠퍼스",
      totalAreaM2: 12500,
      numberOfBuildings: 1,
      contractType: "교육용(을) 고압A",
      operatingHoursWeekday: "08:00~22:00",
      operatingHoursWeekend: "09:00~18:00",
      vacationPeriods: "하계방학 7/1~8/31, 동계방학 12/20~2/28",
      hvacType: "EHP(전기히트펌프) 냉난방",
      keyFacilities: "EHP 에어컨 85대, 엘리베이터 3대, 전산실 서버, 조명(LED 일부교체)",
      consultantMemo: "본관 건물 노후화로 에너지 효율 저하 의심. 방학 중에도 서버실/연구실 일부 가동.",
      status: "draft",
      dataSourceType: "manual",
      projectStage: "pre_diagnostic",
      monthlyBills: {
        create: [
          {
            billingMonth: "2024-04",
            usageKwh: 45200,
            totalBillKrw: 6180000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 4120000,
            climateChargeKrw: 315000,
            fuelAdjustmentKrw: 98000,
            vatKrw: 397000,
            note: "신학기 시작",
          },
          {
            billingMonth: "2024-05",
            usageKwh: 38500,
            totalBillKrw: 5320000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 3380000,
            climateChargeKrw: 268000,
            fuelAdjustmentKrw: 83000,
            vatKrw: 339000,
          },
          {
            billingMonth: "2024-06",
            usageKwh: 52300,
            totalBillKrw: 7450000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 5230000,
            climateChargeKrw: 364000,
            fuelAdjustmentKrw: 113000,
            vatKrw: 493000,
            note: "냉방 시작",
          },
          {
            billingMonth: "2024-07",
            usageKwh: 68400,
            totalBillKrw: 9820000,
            basicChargeKrw: 1520000,
            energyChargeKrw: 7050000,
            climateChargeKrw: 476000,
            fuelAdjustmentKrw: 148000,
            vatKrw: 626000,
            note: "하절기 + 시험기간",
          },
          {
            billingMonth: "2024-08",
            usageKwh: 41200,
            totalBillKrw: 5850000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 3820000,
            climateChargeKrw: 287000,
            fuelAdjustmentKrw: 89000,
            vatKrw: 404000,
            note: "하계방학 (서버실/연구실만 가동)",
          },
          {
            billingMonth: "2024-09",
            usageKwh: 48600,
            totalBillKrw: 6750000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 4580000,
            climateChargeKrw: 338000,
            fuelAdjustmentKrw: 105000,
            vatKrw: 477000,
            note: "2학기 시작",
          },
          {
            billingMonth: "2024-10",
            usageKwh: 35200,
            totalBillKrw: 4920000,
            basicChargeKrw: 1050000,
            energyChargeKrw: 3220000,
            climateChargeKrw: 245000,
            fuelAdjustmentKrw: 76000,
            vatKrw: 329000,
          },
          {
            billingMonth: "2024-11",
            usageKwh: 42800,
            totalBillKrw: 5980000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 3920000,
            climateChargeKrw: 298000,
            fuelAdjustmentKrw: 93000,
            vatKrw: 419000,
            note: "난방 시작",
          },
          {
            billingMonth: "2024-12",
            usageKwh: 58900,
            totalBillKrw: 8350000,
            basicChargeKrw: 1520000,
            energyChargeKrw: 5750000,
            climateChargeKrw: 410000,
            fuelAdjustmentKrw: 128000,
            vatKrw: 542000,
            note: "동절기 난방 + 시험기간",
          },
          {
            billingMonth: "2025-01",
            usageKwh: 65300,
            totalBillKrw: 9380000,
            basicChargeKrw: 1520000,
            energyChargeKrw: 6620000,
            climateChargeKrw: 455000,
            fuelAdjustmentKrw: 141000,
            vatKrw: 644000,
            note: "동절기 피크 (난방 전력 최대)",
          },
          {
            billingMonth: "2025-02",
            usageKwh: 47800,
            totalBillKrw: 6820000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 4620000,
            climateChargeKrw: 333000,
            fuelAdjustmentKrw: 103000,
            vatKrw: 514000,
            note: "동계방학 (일부 난방 가동)",
          },
          {
            billingMonth: "2025-03",
            usageKwh: 43500,
            totalBillKrw: 6050000,
            basicChargeKrw: 1250000,
            energyChargeKrw: 3990000,
            climateChargeKrw: 303000,
            fuelAdjustmentKrw: 94000,
            vatKrw: 413000,
            note: "신학기 준비",
          },
        ],
      },
    },
  });

  console.log(`Seed data created: project ${project.id} (${project.projectName})`);
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
