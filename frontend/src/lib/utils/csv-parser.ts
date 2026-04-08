import type { MonthlyBillInput } from "./validation";

const CSV_HEADERS = [
  "billingMonth",
  "usageKwh",
  "totalBillKrw",
  "basicChargeKrw",
  "energyChargeKrw",
  "climateChargeKrw",
  "fuelAdjustmentKrw",
  "vatKrw",
  "note",
];

export function parseCSV(text: string): { data: MonthlyBillInput[]; errors: string[] } {
  const errors: string[] = [];
  const lines = text.trim().split("\n");

  if (lines.length < 2) {
    errors.push("CSV 파일에 데이터가 없습니다");
    return { data: [], errors };
  }

  const header = lines[0].split(",").map((h) => h.trim());
  if (header[0] !== "billingMonth" && header[0] !== "청구월") {
    errors.push("CSV 헤더가 올바르지 않습니다. 첫 번째 열은 billingMonth 또는 청구월이어야 합니다.");
  }

  const data: MonthlyBillInput[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const cols = line.split(",").map((c) => c.trim());

    const parseNum = (val: string): number | null => {
      if (!val || val === "") return null;
      const num = Number(val.replace(/,/g, ""));
      return isNaN(num) ? null : num;
    };

    const usageKwh = parseNum(cols[1]);
    const totalBillKrw = parseNum(cols[2]);

    if (!cols[0]) {
      errors.push(`${i + 1}행: 청구월이 비어 있습니다`);
      continue;
    }
    if (usageKwh === null || usageKwh <= 0) {
      errors.push(`${i + 1}행: 사용전력량이 올바르지 않습니다`);
      continue;
    }
    if (totalBillKrw === null || totalBillKrw <= 0) {
      errors.push(`${i + 1}행: 청구금액이 올바르지 않습니다`);
      continue;
    }

    data.push({
      billingMonth: cols[0],
      usageKwh,
      totalBillKrw,
      basicChargeKrw: parseNum(cols[3]),
      energyChargeKrw: parseNum(cols[4]),
      climateChargeKrw: parseNum(cols[5]),
      fuelAdjustmentKrw: parseNum(cols[6]),
      vatKrw: parseNum(cols[7]),
      note: cols[8] || undefined,
    });
  }

  return { data, errors };
}

export function generateSampleCSV(): string {
  const headers = "billingMonth,usageKwh,totalBillKrw,basicChargeKrw,energyChargeKrw,climateChargeKrw,fuelAdjustmentKrw,vatKrw,note";
  const rows = [
    "2024-04,45200,6180000,1250000,4120000,315000,98000,397000,",
    "2024-05,38500,5320000,1250000,3380000,268000,83000,339000,",
    "2024-06,52300,7450000,1250000,5230000,364000,113000,493000,냉방시작",
    "2024-07,68400,9820000,1520000,7050000,476000,148000,626000,",
    "2024-08,71200,10250000,1520000,7380000,496000,154000,700000,하절기피크",
    "2024-09,48600,6750000,1250000,4580000,338000,105000,477000,",
    "2024-10,35200,4920000,1050000,3220000,245000,76000,329000,",
    "2024-11,42800,5980000,1250000,3920000,298000,93000,419000,난방시작",
    "2024-12,58900,8350000,1520000,5750000,410000,128000,542000,",
    "2025-01,65300,9380000,1520000,6620000,455000,141000,644000,동절기피크",
    "2025-02,61800,8850000,1520000,6180000,430000,134000,586000,",
    "2025-03,43500,6050000,1250000,3990000,303000,94000,413000,",
  ];
  return [headers, ...rows].join("\n");
}

export { CSV_HEADERS };
