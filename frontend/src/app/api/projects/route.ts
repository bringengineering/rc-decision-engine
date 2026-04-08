import { NextRequest, NextResponse } from "next/server";
import { listProjects, createProject } from "@/lib/services/project-service";
import { projectSchema, monthlyBillsArraySchema } from "@/lib/utils/validation";

export async function GET(request: NextRequest) {
  const search = request.nextUrl.searchParams.get("search") || undefined;
  const projects = await listProjects(search);
  return NextResponse.json(projects);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const projectData = projectSchema.parse(body.project);
    const bills = monthlyBillsArraySchema.parse(body.bills || []);
    const project = await createProject(projectData, bills);
    return NextResponse.json(project, { status: 201 });
  } catch (error) {
    if (error instanceof Error) {
      return NextResponse.json({ error: error.message }, { status: 400 });
    }
    return NextResponse.json({ error: "알 수 없는 오류" }, { status: 500 });
  }
}
