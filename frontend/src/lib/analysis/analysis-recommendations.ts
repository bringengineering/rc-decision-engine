import type { SeasonalMetrics } from "./analysis-metrics";
import type { AbnormalMonth } from "./analysis-flags";

export interface Recommendation {
  type: "A" | "B" | "C";
  title: string;
  priority: "높음" | "중간" | "낮음";
  description: string;
  requiredData: string[];
  nextSteps: string[];
  expectedDeliverables: string[];
}

export function generateRecommendations(
  seasonal: SeasonalMetrics,
  abnormals: AbnormalMonth[],
  billCount: number,
  hasOperationalInfo: boolean
): Recommendation[] {
  const recommendations: Recommendation[] = [];

  const hasStrongSeasonality = seasonal.seasonalStrengthRatio > 1.3;
  const hasManyAbnormals = abnormals.length >= 2;
  const hasHighSeverity = abnormals.some((a) => a.severity === "높음");

  // Type A: Operational Interview
  if (!hasOperationalInfo || billCount >= 10) {
    recommendations.push({
      type: "A",
      title: "운영 인터뷰 우선 진행 권장",
      priority: hasOperationalInfo ? "중간" : "높음",
      description:
        "청구서 기반 예비진단 완료 후, 운영 인터뷰를 통해 실제 운영 패턴과 분석 결과를 대조 검증할 필요가 있습니다.",
      requiredData: [
        "연간 운영 일정 (방학, 시험기간, 행사 등)",
        "냉난방 운영 일정 및 설정온도",
        "주요 설비 가동 일정",
        "최근 시설 변경 이력",
      ],
      nextSteps: [
        "시설 담당자 인터뷰 일정 조율",
        "운영 일정표 확보",
        "방학/운영일정 확보 후 재분석",
      ],
      expectedDeliverables: [
        "운영 패턴 기반 보정 분석 보고서",
        "에너지 절감 가능 영역 도출",
      ],
    });
  }

  // Type B: CT Sensor Pilot
  if (hasStrongSeasonality || hasManyAbnormals || hasHighSeverity) {
    recommendations.push({
      type: "B",
      title: "대표 회로 CT 단기 계측 권장",
      priority: hasHighSeverity ? "높음" : "중간",
      description:
        "계절성 변동 및 특이월이 확인되어, 대표 회로에 대한 CT 센서 단기 파일럿을 통해 야간 기저부하 및 피크 발생 원인을 확인할 필요가 있습니다.",
      requiredData: [
        "전력 계통도 (단선도)",
        "대표 회로 선정 (냉난방, 조명, 동력 등)",
        "CT 설치 가능 위치 확인",
      ],
      nextSteps: [
        "대표 회로 선정 협의",
        "CT 센서 2~4주 단기 설치",
        "시간대별 부하 패턴 분석",
      ],
      expectedDeliverables: [
        "회로별 부하 프로파일",
        "야간 기저부하 분석",
        "피크 발생 원인 분석",
        "절감 가능량 산정",
      ],
    });
  }

  // Type C: Cost Structure Review
  if (!hasStrongSeasonality && !hasManyAbnormals) {
    recommendations.push({
      type: "C",
      title: "비용구조 검토 및 계약전력 검토 권장",
      priority: "낮음",
      description:
        "월별 변동성이 낮아 운영 패턴은 안정적으로 판단됩니다. 비용구조 검토 및 계약전력 적정성을 확인하여 요금 최적화 가능성을 검토할 필요가 있습니다.",
      requiredData: [
        "현재 전력 계약 조건",
        "계약전력 (kW)",
        "최대수요전력 이력",
      ],
      nextSteps: [
        "계약전력 적정성 분석",
        "요금제 변경 검토",
        "추가 현장 방문은 선택 사항",
      ],
      expectedDeliverables: [
        "계약전력 적정성 분석 보고서",
        "요금제 비교 분석",
      ],
    });
  }

  return recommendations;
}
