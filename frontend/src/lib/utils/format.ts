export function formatWon(amount: number): string {
  return new Intl.NumberFormat("ko-KR").format(Math.round(amount)) + "원";
}

export function formatKwh(usage: number): string {
  return new Intl.NumberFormat("ko-KR").format(Math.round(usage)) + " kWh";
}

export function formatPercent(value: number): string {
  return value.toFixed(1) + "%";
}

export function formatCostPerKwh(cost: number): string {
  return cost.toFixed(1) + " 원/kWh";
}

export function formatMonth(yearMonth: string): string {
  const [year, month] = yearMonth.split("-");
  return `${year}년 ${parseInt(month)}월`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("ko-KR").format(Math.round(value));
}

export function getMonthNumber(yearMonth: string): number {
  return parseInt(yearMonth.split("-")[1]);
}

export function sortByMonth(a: string, b: string): number {
  return a.localeCompare(b);
}
