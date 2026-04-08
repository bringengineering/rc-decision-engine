-- CreateTable
CREATE TABLE "Project" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "projectName" TEXT NOT NULL,
    "customerName" TEXT NOT NULL,
    "contactName" TEXT NOT NULL DEFAULT '',
    "contactEmail" TEXT,
    "contactPhone" TEXT,
    "buildingType" TEXT NOT NULL DEFAULT '학교',
    "buildingName" TEXT NOT NULL DEFAULT '',
    "campusOrSiteName" TEXT,
    "totalAreaM2" REAL,
    "numberOfBuildings" INTEGER,
    "contractType" TEXT,
    "operatingHoursWeekday" TEXT,
    "operatingHoursWeekend" TEXT,
    "vacationPeriods" TEXT,
    "hvacType" TEXT,
    "keyFacilities" TEXT,
    "consultantMemo" TEXT,
    "status" TEXT NOT NULL DEFAULT 'draft',
    "analysisVersion" TEXT,
    "dataSourceType" TEXT NOT NULL DEFAULT 'manual',
    "projectStage" TEXT NOT NULL DEFAULT 'pre_diagnostic',
    "contractDemandKw" REAL,
    "consultantManualSummary" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "MonthlyBillRecord" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "projectId" TEXT NOT NULL,
    "billingMonth" TEXT NOT NULL,
    "usageKwh" REAL NOT NULL,
    "totalBillKrw" REAL NOT NULL,
    "basicChargeKrw" REAL,
    "energyChargeKrw" REAL,
    "climateChargeKrw" REAL,
    "fuelAdjustmentKrw" REAL,
    "vatKrw" REAL,
    "fundKrw" REAL,
    "supplyAmountKrw" REAL,
    "sourceFileName" TEXT,
    "isVerified" BOOLEAN NOT NULL DEFAULT false,
    "dataQualityNote" TEXT,
    "note" TEXT,
    CONSTRAINT "MonthlyBillRecord_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "AnalysisSnapshot" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "projectId" TEXT NOT NULL,
    "annualUsageKwh" REAL NOT NULL,
    "annualBillKrw" REAL NOT NULL,
    "averageMonthlyUsageKwh" REAL NOT NULL,
    "averageMonthlyBillKrw" REAL NOT NULL,
    "averageCostPerKwh" REAL NOT NULL,
    "maxUsageMonth" TEXT NOT NULL,
    "maxUsageValue" REAL NOT NULL,
    "minUsageMonth" TEXT NOT NULL,
    "minUsageValue" REAL NOT NULL,
    "maxBillMonth" TEXT NOT NULL,
    "maxBillValue" REAL NOT NULL,
    "minBillMonth" TEXT NOT NULL,
    "minBillValue" REAL NOT NULL,
    "seasonalStrengthRatio" REAL NOT NULL,
    "summerAvgUsage" REAL NOT NULL,
    "winterAvgUsage" REAL NOT NULL,
    "shoulderAvgUsage" REAL NOT NULL,
    "summerAvgBill" REAL NOT NULL,
    "winterAvgBill" REAL NOT NULL,
    "shoulderAvgBill" REAL NOT NULL,
    "abnormalMonthsJson" TEXT NOT NULL,
    "insightsJson" TEXT NOT NULL,
    "recommendationJson" TEXT NOT NULL,
    "monthlyChangesJson" TEXT NOT NULL,
    "analysisVersion" TEXT NOT NULL DEFAULT '1.0',
    "inputCompletenessScore" REAL NOT NULL DEFAULT 0,
    "confidenceScore" REAL NOT NULL DEFAULT 0,
    "limitationsText" TEXT NOT NULL DEFAULT '',
    "consultantOverrideSummary" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "AnalysisSnapshot_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "ReportConfig" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "companyName" TEXT NOT NULL DEFAULT '브링 에너지',
    "companyLogoUrl" TEXT,
    "consultantName" TEXT,
    "footerText" TEXT
);

-- CreateIndex
CREATE UNIQUE INDEX "MonthlyBillRecord_projectId_billingMonth_key" ON "MonthlyBillRecord"("projectId", "billingMonth");
