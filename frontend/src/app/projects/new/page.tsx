"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { parseCSV } from "@/lib/utils/csv-parser";
import { formatWon, formatKwh } from "@/lib/utils/format";

const BUILDING_TYPES = ["학교", "공장", "오피스", "상가", "병원", "기타"];

const EMPTY_MONTHS = Array.from({ length: 12 }, (_, i) => {
  const now = new Date();
  const d = new Date(now.getFullYear(), now.getMonth() - 11 + i, 1);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  return {
    billingMonth: `${yyyy}-${mm}`,
    usageKwh: "",
    totalBillKrw: "",
    basicChargeKrw: "",
    energyChargeKrw: "",
    climateChargeKrw: "",
    fuelAdjustmentKrw: "",
    vatKrw: "",
    note: "",
  };
});

type BillRow = (typeof EMPTY_MONTHS)[number];

export default function NewProjectPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // Project fields
  const [projectName, setProjectName] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [buildingType, setBuildingType] = useState("학교");
  const [buildingName, setBuildingName] = useState("");
  const [campusOrSiteName, setCampusOrSiteName] = useState("");
  const [totalAreaM2, setTotalAreaM2] = useState("");
  const [numberOfBuildings, setNumberOfBuildings] = useState("");
  const [contractType, setContractType] = useState("");
  const [operatingHoursWeekday, setOperatingHoursWeekday] = useState("");
  const [operatingHoursWeekend, setOperatingHoursWeekend] = useState("");
  const [vacationPeriods, setVacationPeriods] = useState("");
  const [hvacType, setHvacType] = useState("");
  const [keyFacilities, setKeyFacilities] = useState("");
  const [consultantMemo, setConsultantMemo] = useState("");

  // Billing data
  const [bills, setBills] = useState<BillRow[]>(EMPTY_MONTHS);
  const [csvErrors, setCsvErrors] = useState<string[]>([]);

  function updateBill(index: number, field: keyof BillRow, value: string) {
    const updated = [...bills];
    updated[index] = { ...updated[index], [field]: value };
    setBills(updated);
  }

  function handleCSVUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      const { data, errors } = parseCSV(text);
      setCsvErrors(errors);
      if (data.length > 0) {
        setBills(
          data.map((d) => ({
            billingMonth: d.billingMonth,
            usageKwh: String(d.usageKwh),
            totalBillKrw: String(d.totalBillKrw),
            basicChargeKrw: d.basicChargeKrw != null ? String(d.basicChargeKrw) : "",
            energyChargeKrw: d.energyChargeKrw != null ? String(d.energyChargeKrw) : "",
            climateChargeKrw: d.climateChargeKrw != null ? String(d.climateChargeKrw) : "",
            fuelAdjustmentKrw: d.fuelAdjustmentKrw != null ? String(d.fuelAdjustmentKrw) : "",
            vatKrw: d.vatKrw != null ? String(d.vatKrw) : "",
            note: d.note || "",
          }))
        );
      }
    };
    reader.readAsText(file);
  }

  async function handleSave() {
    setError("");
    if (!projectName.trim()) {
      setError("프로젝트명을 입력해주세요");
      return;
    }
    if (!customerName.trim()) {
      setError("고객사명을 입력해주세요");
      return;
    }

    const validBills = bills
      .filter((b) => b.usageKwh && b.totalBillKrw)
      .map((b) => ({
        billingMonth: b.billingMonth,
        usageKwh: Number(b.usageKwh),
        totalBillKrw: Number(b.totalBillKrw),
        basicChargeKrw: b.basicChargeKrw ? Number(b.basicChargeKrw) : null,
        energyChargeKrw: b.energyChargeKrw ? Number(b.energyChargeKrw) : null,
        climateChargeKrw: b.climateChargeKrw ? Number(b.climateChargeKrw) : null,
        fuelAdjustmentKrw: b.fuelAdjustmentKrw ? Number(b.fuelAdjustmentKrw) : null,
        vatKrw: b.vatKrw ? Number(b.vatKrw) : null,
        note: b.note || undefined,
      }));

    if (validBills.length === 0) {
      setError("최소 1개월 이상의 요금 데이터를 입력해주세요");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project: {
            projectName,
            customerName,
            contactName,
            contactEmail: contactEmail || undefined,
            contactPhone: contactPhone || undefined,
            buildingType,
            buildingName,
            campusOrSiteName: campusOrSiteName || undefined,
            totalAreaM2: totalAreaM2 ? Number(totalAreaM2) : undefined,
            numberOfBuildings: numberOfBuildings ? Number(numberOfBuildings) : undefined,
            contractType: contractType || undefined,
            operatingHoursWeekday: operatingHoursWeekday || undefined,
            operatingHoursWeekend: operatingHoursWeekend || undefined,
            vacationPeriods: vacationPeriods || undefined,
            hvacType: hvacType || undefined,
            keyFacilities: keyFacilities || undefined,
            consultantMemo: consultantMemo || undefined,
          },
          bills: validBills,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.error || "저장 중 오류가 발생했습니다");
        return;
      }

      const project = await res.json();
      router.push(`/projects/${project.id}/review`);
    } catch {
      setError("네트워크 오류가 발생했습니다");
    } finally {
      setSaving(false);
    }
  }

  // Totals for preview
  const totalUsage = bills.reduce((s, b) => s + (Number(b.usageKwh) || 0), 0);
  const totalBill = bills.reduce((s, b) => s + (Number(b.totalBillKrw) || 0), 0);
  const filledCount = bills.filter((b) => b.usageKwh && b.totalBillKrw).length;

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">새 프로젝트 만들기</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
          {error}
        </div>
      )}

      <Tabs defaultValue="customer">
        <TabsList className="mb-6">
          <TabsTrigger value="customer">고객/프로젝트 정보</TabsTrigger>
          <TabsTrigger value="building">건물/사업장 정보</TabsTrigger>
          <TabsTrigger value="operation">운영 정보</TabsTrigger>
          <TabsTrigger value="billing">월별 요금 데이터</TabsTrigger>
        </TabsList>

        <TabsContent value="customer">
          <Card>
            <CardHeader>
              <CardTitle>고객/프로젝트 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>프로젝트명 *</Label>
                  <Input value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="예: 상지대학교 본관 전력 예비진단" />
                </div>
                <div>
                  <Label>고객사명 *</Label>
                  <Input value={customerName} onChange={(e) => setCustomerName(e.target.value)} placeholder="예: 상지대학교" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>담당자명</Label>
                  <Input value={contactName} onChange={(e) => setContactName(e.target.value)} />
                </div>
                <div>
                  <Label>연락처</Label>
                  <Input value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} />
                </div>
                <div>
                  <Label>이메일</Label>
                  <Input value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} type="email" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="building">
          <Card>
            <CardHeader>
              <CardTitle>건물/사업장 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>건물 유형</Label>
                  <select
                    value={buildingType}
                    onChange={(e) => setBuildingType(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  >
                    {BUILDING_TYPES.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label>건물명</Label>
                  <Input value={buildingName} onChange={(e) => setBuildingName(e.target.value)} placeholder="예: 본관" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>캠퍼스/사업장명</Label>
                  <Input value={campusOrSiteName} onChange={(e) => setCampusOrSiteName(e.target.value)} />
                </div>
                <div>
                  <Label>연면적 (m²)</Label>
                  <Input value={totalAreaM2} onChange={(e) => setTotalAreaM2(e.target.value)} type="number" />
                </div>
                <div>
                  <Label>건물 수</Label>
                  <Input value={numberOfBuildings} onChange={(e) => setNumberOfBuildings(e.target.value)} type="number" />
                </div>
              </div>
              <div>
                <Label>계약종별/용도</Label>
                <Input value={contractType} onChange={(e) => setContractType(e.target.value)} placeholder="예: 교육용(을) 고압A" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="operation">
          <Card>
            <CardHeader>
              <CardTitle>운영 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>평일 운영시간</Label>
                  <Input value={operatingHoursWeekday} onChange={(e) => setOperatingHoursWeekday(e.target.value)} placeholder="예: 08:00~22:00" />
                </div>
                <div>
                  <Label>주말 운영시간</Label>
                  <Input value={operatingHoursWeekend} onChange={(e) => setOperatingHoursWeekend(e.target.value)} placeholder="예: 09:00~18:00" />
                </div>
              </div>
              <div>
                <Label>방학/휴무/시험기간</Label>
                <Textarea value={vacationPeriods} onChange={(e) => setVacationPeriods(e.target.value)} placeholder="예: 하계방학 7/1~8/31, 동계방학 12/20~2/28" />
              </div>
              <div>
                <Label>냉난방 방식</Label>
                <Input value={hvacType} onChange={(e) => setHvacType(e.target.value)} placeholder="예: EHP(전기히트펌프) 냉난방" />
              </div>
              <div>
                <Label>주요 설비</Label>
                <Textarea value={keyFacilities} onChange={(e) => setKeyFacilities(e.target.value)} placeholder="예: EHP 에어컨 120대, 전기보일러, 엘리베이터 4대" />
              </div>
              <div>
                <Label>현장 특이사항 / 컨설턴트 메모</Label>
                <Textarea value={consultantMemo} onChange={(e) => setConsultantMemo(e.target.value)} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>월별 요금 데이터</CardTitle>
                <div className="flex gap-2">
                  <a href="/api/csv/sample" download className="text-sm text-blue-600 hover:underline">
                    샘플 CSV 다운로드
                  </a>
                  <label className="cursor-pointer text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-md">
                    CSV 업로드
                    <input type="file" accept=".csv" className="hidden" onChange={handleCSVUpload} />
                  </label>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {csvErrors.length > 0 && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-md text-sm">
                  {csvErrors.map((err, i) => (
                    <div key={i}>{err}</div>
                  ))}
                </div>
              )}

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="p-2 text-left font-medium">청구월</th>
                      <th className="p-2 text-right font-medium">사용전력량(kWh)</th>
                      <th className="p-2 text-right font-medium">청구금액(원)</th>
                      <th className="p-2 text-right font-medium">기본요금</th>
                      <th className="p-2 text-right font-medium">전력량요금</th>
                      <th className="p-2 text-right font-medium">기후환경요금</th>
                      <th className="p-2 text-right font-medium">연료비조정액</th>
                      <th className="p-2 text-right font-medium">부가세</th>
                      <th className="p-2 text-left font-medium">비고</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bills.map((bill, i) => (
                      <tr key={i} className="border-b hover:bg-gray-50">
                        <td className="p-1">
                          <Input
                            value={bill.billingMonth}
                            onChange={(e) => updateBill(i, "billingMonth", e.target.value)}
                            className="w-28 text-sm h-8"
                            placeholder="YYYY-MM"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.usageKwh}
                            onChange={(e) => updateBill(i, "usageKwh", e.target.value)}
                            className="w-24 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.totalBillKrw}
                            onChange={(e) => updateBill(i, "totalBillKrw", e.target.value)}
                            className="w-28 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.basicChargeKrw}
                            onChange={(e) => updateBill(i, "basicChargeKrw", e.target.value)}
                            className="w-24 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.energyChargeKrw}
                            onChange={(e) => updateBill(i, "energyChargeKrw", e.target.value)}
                            className="w-24 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.climateChargeKrw}
                            onChange={(e) => updateBill(i, "climateChargeKrw", e.target.value)}
                            className="w-24 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.fuelAdjustmentKrw}
                            onChange={(e) => updateBill(i, "fuelAdjustmentKrw", e.target.value)}
                            className="w-24 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.vatKrw}
                            onChange={(e) => updateBill(i, "vatKrw", e.target.value)}
                            className="w-24 text-right text-sm h-8"
                            type="number"
                          />
                        </td>
                        <td className="p-1">
                          <Input
                            value={bill.note}
                            onChange={(e) => updateBill(i, "note", e.target.value)}
                            className="w-24 text-sm h-8"
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex items-center gap-6 text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
                <span>입력된 월: <strong>{filledCount}</strong>/12</span>
                <span>총 사용량: <strong>{formatKwh(totalUsage)}</strong></span>
                <span>총 요금: <strong>{formatWon(totalBill)}</strong></span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="mt-6 flex justify-end gap-3">
        <Button variant="outline" onClick={() => router.push("/")}>
          취소
        </Button>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? "저장 중..." : "저장 및 데이터 검토"}
        </Button>
      </div>
    </div>
  );
}
