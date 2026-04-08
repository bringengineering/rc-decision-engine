const { createClient } = require("@libsql/client");

const db = createClient({ url: "file:dev.db" });

async function main() {
  // Clean existing data
  await db.execute("DELETE FROM AnalysisSnapshot");
  await db.execute("DELETE FROM MonthlyBillRecord");
  await db.execute("DELETE FROM Project");
  await db.execute("DELETE FROM ReportConfig");

  // Create report config
  await db.execute({
    sql: `INSERT INTO ReportConfig (id, companyName, consultantName, footerText)
          VALUES (?, ?, ?, ?)`,
    args: [
      "cfg_demo",
      "브링 에너지",
      "김에너지",
      "전기요금 기반 예비진단 및 다음 단계 제안 도구",
    ],
  });

  // Create demo project
  const projectId = "proj_sangji_demo";
  const now = new Date().toISOString();
  await db.execute({
    sql: `INSERT INTO Project (
      id, projectName, customerName, contactName, contactPhone, contactEmail,
      buildingType, buildingName, campusOrSiteName, totalAreaM2, numberOfBuildings,
      contractType, operatingHoursWeekday, operatingHoursWeekend,
      vacationPeriods, hvacType, keyFacilities, consultantMemo,
      status, dataSourceType, projectStage, createdAt, updatedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    args: [
      projectId,
      "상지대학교 본관 전력 예비진단",
      "상지대학교",
      "김시설",
      "033-730-0000",
      "facility@sangji.ac.kr",
      "학교",
      "본관",
      "상지대학교 원주캠퍼스",
      12500,
      1,
      "교육용(을) 고압A",
      "08:00~22:00",
      "09:00~18:00",
      "하계방학 7/1~8/31, 동계방학 12/20~2/28",
      "EHP(전기히트펌프) 냉난방",
      "EHP 에어컨 85대, 엘리베이터 3대, 전산실 서버, 조명(LED 일부교체)",
      "본관 건물 노후화로 에너지 효율 저하 의심. 방학 중에도 서버실/연구실 일부 가동.",
      "draft",
      "manual",
      "pre_diagnostic",
      now,
      now,
    ],
  });

  // Insert monthly bills
  const bills = [
    { month: "2024-04", usage: 45200, bill: 6180000, basic: 1250000, energy: 4120000, climate: 315000, fuel: 98000, vat: 397000, note: "신학기 시작" },
    { month: "2024-05", usage: 38500, bill: 5320000, basic: 1250000, energy: 3380000, climate: 268000, fuel: 83000, vat: 339000, note: null },
    { month: "2024-06", usage: 52300, bill: 7450000, basic: 1250000, energy: 5230000, climate: 364000, fuel: 113000, vat: 493000, note: "냉방 시작" },
    { month: "2024-07", usage: 68400, bill: 9820000, basic: 1520000, energy: 7050000, climate: 476000, fuel: 148000, vat: 626000, note: "하절기 + 시험기간" },
    { month: "2024-08", usage: 41200, bill: 5850000, basic: 1250000, energy: 3820000, climate: 287000, fuel: 89000, vat: 404000, note: "하계방학 (서버실/연구실만 가동)" },
    { month: "2024-09", usage: 48600, bill: 6750000, basic: 1250000, energy: 4580000, climate: 338000, fuel: 105000, vat: 477000, note: "2학기 시작" },
    { month: "2024-10", usage: 35200, bill: 4920000, basic: 1050000, energy: 3220000, climate: 245000, fuel: 76000, vat: 329000, note: null },
    { month: "2024-11", usage: 42800, bill: 5980000, basic: 1250000, energy: 3920000, climate: 298000, fuel: 93000, vat: 419000, note: "난방 시작" },
    { month: "2024-12", usage: 58900, bill: 8350000, basic: 1520000, energy: 5750000, climate: 410000, fuel: 128000, vat: 542000, note: "동절기 난방 + 시험기간" },
    { month: "2025-01", usage: 65300, bill: 9380000, basic: 1520000, energy: 6620000, climate: 455000, fuel: 141000, vat: 644000, note: "동절기 피크 (난방 전력 최대)" },
    { month: "2025-02", usage: 47800, bill: 6820000, basic: 1250000, energy: 4620000, climate: 333000, fuel: 103000, vat: 514000, note: "동계방학 (일부 난방 가동)" },
    { month: "2025-03", usage: 43500, bill: 6050000, basic: 1250000, energy: 3990000, climate: 303000, fuel: 94000, vat: 413000, note: "신학기 준비" },
  ];

  for (let i = 0; i < bills.length; i++) {
    const b = bills[i];
    await db.execute({
      sql: `INSERT INTO MonthlyBillRecord (
        id, projectId, billingMonth, usageKwh, totalBillKrw,
        basicChargeKrw, energyChargeKrw, climateChargeKrw, fuelAdjustmentKrw, vatKrw,
        isVerified, note
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        `bill_${i + 1}`,
        projectId,
        b.month,
        b.usage,
        b.bill,
        b.basic,
        b.energy,
        b.climate,
        b.fuel,
        b.vat,
        0,
        b.note,
      ],
    });
  }

  console.log(`Seed completed: project ${projectId} with ${bills.length} monthly bills`);
}

main().catch(console.error);
