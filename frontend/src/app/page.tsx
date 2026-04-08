"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

interface Project {
  id: string;
  projectName: string;
  customerName: string;
  buildingType: string;
  buildingName: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  monthlyBills: { id: string }[];
  analysisSnapshots: { id: string }[];
}

const STATUS_MAP: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  draft: { label: "초안", variant: "secondary" },
  analyzed: { label: "분석완료", variant: "default" },
  exported: { label: "내보내기", variant: "outline" },
};

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  async function fetchProjects(searchTerm?: string) {
    setLoading(true);
    const url = searchTerm ? `/api/projects?search=${encodeURIComponent(searchTerm)}` : "/api/projects";
    const res = await fetch(url);
    const data = await res.json();
    setProjects(data);
    setLoading(false);
  }

  function handleSearch() {
    fetchProjects(search);
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">프로젝트 관리</h1>
          <p className="mt-1 text-sm text-gray-500">전기요금 기반 예비진단 프로젝트</p>
        </div>
        <Link href="/projects/new">
          <Button>새 프로젝트 만들기</Button>
        </Link>
      </div>

      <div className="flex gap-2 mb-6">
        <Input
          placeholder="프로젝트명, 고객사명, 건물명으로 검색"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="max-w-md"
        />
        <Button variant="outline" onClick={handleSearch}>
          검색
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">불러오는 중...</div>
      ) : projects.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500 mb-4">아직 프로젝트가 없습니다</p>
            <Link href="/projects/new">
              <Button>첫 프로젝트 만들기</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {projects.map((project) => {
            const status = STATUS_MAP[project.status] || STATUS_MAP.draft;
            return (
              <Link key={project.id} href={`/projects/${project.id}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{project.projectName}</CardTitle>
                      <Badge variant={status.variant}>{status.label}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-6 text-sm text-gray-600">
                      <span>{project.customerName}</span>
                      <span>{project.buildingType} - {project.buildingName || "미지정"}</span>
                      <span>{project.monthlyBills.length}개월 데이터</span>
                      <span className="ml-auto text-xs text-gray-400">
                        {new Date(project.updatedAt).toLocaleDateString("ko-KR")}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
