import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  let config = await prisma.reportConfig.findFirst();
  if (!config) {
    config = await prisma.reportConfig.create({
      data: { companyName: "브링 에너지" },
    });
  }
  return NextResponse.json(config);
}

export async function PUT(request: NextRequest) {
  const body = await request.json();
  let config = await prisma.reportConfig.findFirst();
  if (config) {
    config = await prisma.reportConfig.update({
      where: { id: config.id },
      data: body,
    });
  } else {
    config = await prisma.reportConfig.create({ data: body });
  }
  return NextResponse.json(config);
}
