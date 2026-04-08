import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { evaluateDataQuality } from "@/lib/utils/data-quality";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const project = await prisma.project.findUnique({
    where: { id },
    include: { monthlyBills: { orderBy: { billingMonth: "asc" } } },
  });

  if (!project) {
    return NextResponse.json({ error: "프로젝트를 찾을 수 없습니다" }, { status: 404 });
  }

  const quality = evaluateDataQuality(
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

  return NextResponse.json({
    bills: project.monthlyBills,
    quality,
  });
}
