import { prisma } from "../db";
import type { ProjectInput, MonthlyBillInput } from "../utils/validation";

export async function listProjects(search?: string) {
  const where = search
    ? {
        OR: [
          { projectName: { contains: search } },
          { customerName: { contains: search } },
          { buildingName: { contains: search } },
        ],
      }
    : {};

  return prisma.project.findMany({
    where,
    include: {
      monthlyBills: { select: { id: true } },
      analysisSnapshots: { select: { id: true }, take: 1, orderBy: { createdAt: "desc" as const } },
    },
    orderBy: { updatedAt: "desc" },
  });
}

export async function getProject(id: string) {
  return prisma.project.findUnique({
    where: { id },
    include: {
      monthlyBills: { orderBy: { billingMonth: "asc" } },
      analysisSnapshots: { orderBy: { createdAt: "desc" }, take: 1 },
    },
  });
}

export async function createProject(
  data: ProjectInput,
  bills: MonthlyBillInput[]
) {
  return prisma.project.create({
    data: {
      ...data,
      totalAreaM2: data.totalAreaM2 ?? undefined,
      numberOfBuildings: data.numberOfBuildings ?? undefined,
      monthlyBills: {
        create: bills.map((bill) => ({
          billingMonth: bill.billingMonth,
          usageKwh: bill.usageKwh,
          totalBillKrw: bill.totalBillKrw,
          basicChargeKrw: bill.basicChargeKrw ?? undefined,
          energyChargeKrw: bill.energyChargeKrw ?? undefined,
          climateChargeKrw: bill.climateChargeKrw ?? undefined,
          fuelAdjustmentKrw: bill.fuelAdjustmentKrw ?? undefined,
          vatKrw: bill.vatKrw ?? undefined,
          note: bill.note ?? undefined,
        })),
      },
    },
    include: { monthlyBills: true },
  });
}

export async function updateProject(
  id: string,
  data: Partial<ProjectInput>,
  bills?: MonthlyBillInput[]
) {
  if (bills) {
    await prisma.monthlyBillRecord.deleteMany({ where: { projectId: id } });
    await prisma.project.update({
      where: { id },
      data: {
        ...data,
        monthlyBills: {
          create: bills.map((bill) => ({
            billingMonth: bill.billingMonth,
            usageKwh: bill.usageKwh,
            totalBillKrw: bill.totalBillKrw,
            basicChargeKrw: bill.basicChargeKrw ?? undefined,
            energyChargeKrw: bill.energyChargeKrw ?? undefined,
            climateChargeKrw: bill.climateChargeKrw ?? undefined,
            fuelAdjustmentKrw: bill.fuelAdjustmentKrw ?? undefined,
            vatKrw: bill.vatKrw ?? undefined,
            note: bill.note ?? undefined,
          })),
        },
      },
    });
  } else {
    await prisma.project.update({ where: { id }, data });
  }

  return getProject(id);
}

export async function deleteProject(id: string) {
  return prisma.project.delete({ where: { id } });
}
