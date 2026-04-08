"use client";

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface MonthlyBill {
  billingMonth: string;
  usageKwh: number;
  totalBillKrw: number;
  basicChargeKrw: number | null;
  energyChargeKrw: number | null;
  climateChargeKrw: number | null;
  fuelAdjustmentKrw: number | null;
  vatKrw: number | null;
}

function shortMonth(ym: string): string {
  const [, m] = ym.split("-");
  return `${parseInt(m)}월`;
}

function formatTooltipValue(value: number, name: string): string {
  if (name.includes("사용량") || name.includes("kWh")) {
    return `${value.toLocaleString("ko-KR")} kWh`;
  }
  if (name.includes("단가")) {
    return `${value.toFixed(1)} 원/kWh`;
  }
  return `${value.toLocaleString("ko-KR")}원`;
}

export function AnalysisCharts({ bills }: { bills: MonthlyBill[] }) {
  const data = bills.map((b) => ({
    month: shortMonth(b.billingMonth),
    사용량: b.usageKwh,
    요금: b.totalBillKrw,
    환산단가: b.usageKwh > 0 ? Math.round((b.totalBillKrw / b.usageKwh) * 10) / 10 : 0,
    기본요금: b.basicChargeKrw || 0,
    전력량요금: b.energyChargeKrw || 0,
    기후환경요금: b.climateChargeKrw || 0,
    연료비조정액: b.fuelAdjustmentKrw || 0,
    부가세: b.vatKrw || 0,
  }));

  const hasBreakdown = bills.some((b) => b.basicChargeKrw != null);

  return (
    <div className="space-y-6 mb-6">
      {/* Combined Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">월별 전력사용량 및 청구금액 추이</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                label={{ value: "kWh", angle: -90, position: "insideLeft", style: { fontSize: 11 } }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`}
                label={{ value: "원", angle: 90, position: "insideRight", style: { fontSize: 11 } }}
              />
              <Tooltip formatter={(value, name) => [formatTooltipValue(Number(value), String(name)), String(name)]} />
              <Legend />
              <Bar yAxisId="left" dataKey="사용량" fill="#3b82f6" name="사용량(kWh)" opacity={0.8} />
              <Line yAxisId="right" type="monotone" dataKey="요금" stroke="#ef4444" name="청구금액(원)" strokeWidth={2} dot={{ r: 3 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        {/* Usage Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">월별 전력사용량</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(value, name) => [formatTooltipValue(Number(value), String(name)), String(name)]} />
                <Bar dataKey="사용량" fill="#3b82f6" name="사용량(kWh)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Cost per kWh Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">환산 청구단가 추이</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={["dataMin - 5", "dataMax + 5"]} />
                <Tooltip formatter={(value, name) => [formatTooltipValue(Number(value), String(name)), String(name)]} />
                <Line type="monotone" dataKey="환산단가" stroke="#8b5cf6" name="환산 청구단가(원/kWh)" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charge Composition */}
      {hasBreakdown && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">요금 구성 내역</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`} />
                <Tooltip formatter={(value, name) => [formatTooltipValue(Number(value), String(name)), String(name)]} />
                <Legend />
                <Bar dataKey="기본요금" stackId="a" fill="#6366f1" />
                <Bar dataKey="전력량요금" stackId="a" fill="#3b82f6" />
                <Bar dataKey="기후환경요금" stackId="a" fill="#10b981" />
                <Bar dataKey="연료비조정액" stackId="a" fill="#f59e0b" />
                <Bar dataKey="부가세" stackId="a" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
