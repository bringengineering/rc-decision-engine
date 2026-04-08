import { z } from "zod";

export const projectSchema = z.object({
  projectName: z.string().min(1, "프로젝트명을 입력해주세요"),
  customerName: z.string().min(1, "고객사명을 입력해주세요"),
  contactName: z.string().default(""),
  contactEmail: z.string().email("올바른 이메일 형식이 아닙니다").optional().or(z.literal("")),
  contactPhone: z.string().optional(),
  buildingType: z.string().default("학교"),
  buildingName: z.string().default(""),
  campusOrSiteName: z.string().optional(),
  totalAreaM2: z.number().positive("면적은 0보다 커야 합니다").optional().nullable(),
  numberOfBuildings: z.number().int().positive().optional().nullable(),
  contractType: z.string().optional(),
  operatingHoursWeekday: z.string().optional(),
  operatingHoursWeekend: z.string().optional(),
  vacationPeriods: z.string().optional(),
  hvacType: z.string().optional(),
  keyFacilities: z.string().optional(),
  consultantMemo: z.string().optional(),
});

export const monthlyBillSchema = z.object({
  billingMonth: z.string().regex(/^\d{4}-\d{2}$/, "YYYY-MM 형식이어야 합니다"),
  usageKwh: z.number().positive("사용전력량은 0보다 커야 합니다"),
  totalBillKrw: z.number().positive("청구금액은 0보다 커야 합니다"),
  basicChargeKrw: z.number().optional().nullable(),
  energyChargeKrw: z.number().optional().nullable(),
  climateChargeKrw: z.number().optional().nullable(),
  fuelAdjustmentKrw: z.number().optional().nullable(),
  vatKrw: z.number().optional().nullable(),
  fundKrw: z.number().optional().nullable(),
  note: z.string().optional(),
});

export const monthlyBillsArraySchema = z.array(monthlyBillSchema).refine(
  (bills) => {
    const months = bills.map((b) => b.billingMonth);
    return new Set(months).size === months.length;
  },
  { message: "중복된 청구월이 있습니다" }
);

export type ProjectInput = z.infer<typeof projectSchema>;
export type MonthlyBillInput = z.infer<typeof monthlyBillSchema>;
