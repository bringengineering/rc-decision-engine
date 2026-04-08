import { NextResponse } from "next/server";
import { generateSampleCSV } from "@/lib/utils/csv-parser";

export async function GET() {
  const csv = generateSampleCSV();
  return new NextResponse(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": "attachment; filename=sample_billing_data.csv",
    },
  });
}
