# ⚡ BRING 전기요금 절감 진단 시스템 — 완전 설계 명세서 v1.0

> Claude Code 개발용 마스터 스펙 문서
> 작성 기준: 2026년 4월 | BRING Engineering

---

## 0. 시스템 개요

### 한 줄 정의
> 전기 고지서 사진 1장(또는 수치 직접 입력)으로 AI가 절감 가능 금액을 즉시 계산하고,
> 선택적으로 기기 사진을 추가하면 더 정밀한 분석 리포트를 자동 생성하는 유료 SaaS.

### 핵심 가치 흐름
```
고객 유입 → 고지서 입력(필수) → 기기 사진(선택) → 무료 미리보기 →
유료 결제(39,000원) → PDF 리포트 자동 발행 → CT센서 컨설팅 업셀
```

### 기술 스택
| 영역 | 선택 기술 | 이유 |
|------|-----------|------|
| Frontend | React + Vite | 빠른 MVP |
| Styling | Tailwind CSS | 빠른 UI |
| Backend | Supabase (BaaS) | 인프라 최소화 |
| DB | Supabase PostgreSQL | 무료 시작 |
| AI | Claude claude-sonnet-4-20250514 API | 이미지 분석 + 리포트 문구 |
| PDF | html2pdf.js | 브라우저 사이드 생성 |
| 결제 | 토스페이먼츠 | 국내 최적화 |
| 배포 | Vercel | 무료 + 자동 배포 |
| 이메일 | Resend | 리포트 자동 발송 |

---

## 1. 디렉토리 구조

```
bring-energy/
├── src/
│   ├── components/
│   │   ├── ui/                    # 공통 UI 컴포넌트
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── Progress.jsx
│   │   │   └── Modal.jsx
│   │   ├── report/               # 리포트 관련 컴포넌트
│   │   │   ├── ReportCover.jsx
│   │   │   ├── Page1_Status.jsx
│   │   │   ├── Page2_Analysis.jsx
│   │   │   ├── Page3_Simulation.jsx
│   │   │   ├── Page4_Action.jsx
│   │   │   └── ReportFooter.jsx
│   │   ├── input/                # 입력 단계 컴포넌트
│   │   │   ├── BillInputForm.jsx
│   │   │   ├── BillImageUpload.jsx
│   │   │   ├── DeviceInputForm.jsx
│   │   │   └── DeviceImageUpload.jsx
│   │   └── preview/              # 미리보기 컴포넌트
│   │       ├── FreePreview.jsx
│   │       └── PaywallGate.jsx
│   ├── pages/
│   │   ├── Landing.jsx           # 랜딩페이지
│   │   ├── Step1_Bill.jsx        # STEP 1: 고지서 입력
│   │   ├── Step2_Devices.jsx     # STEP 2: 기기 입력 (선택)
│   │   ├── Step3_Preview.jsx     # STEP 3: 무료 미리보기
│   │   ├── Step4_Payment.jsx     # STEP 4: 결제
│   │   ├── Step5_Report.jsx      # STEP 5: 리포트 확인 + 다운로드
│   │   └── Admin.jsx             # 관리자 대시보드
│   ├── hooks/
│   │   ├── useAnalysis.js        # 분석 로직 훅
│   │   ├── usePayment.js         # 결제 훅
│   │   └── useReport.js          # 리포트 생성 훅
│   ├── lib/
│   │   ├── calculator.js         # 핵심 계산 엔진
│   │   ├── kepco-rates.js        # 한전 요금 데이터
│   │   ├── benchmark.js          # 업종 벤치마크 데이터
│   │   ├── claude-api.js         # Claude API 호출
│   │   ├── pdf-generator.js      # PDF 생성
│   │   └── supabase.js           # DB 클라이언트
│   ├── utils/
│   │   ├── formatters.js         # 숫자/날짜 포맷
│   │   └── validators.js         # 입력값 검증
│   └── App.jsx
├── public/
│   └── bring-logo.svg
├── .env
└── package.json
```

---

## 2. 데이터 스키마

### 2-1. Supabase 테이블 설계

#### `diagnoses` (진단 세션)
```sql
CREATE TABLE diagnoses (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    TEXT NOT NULL UNIQUE,        -- 비로그인 세션 식별자
  created_at    TIMESTAMP DEFAULT NOW(),
  updated_at    TIMESTAMP DEFAULT NOW(),
  status        TEXT DEFAULT 'draft',        -- draft | preview | paid | complete

  -- 고지서 기본 정보 (필수)
  contract_type       TEXT,    -- 'general_low' | 'general_high_a' | 'general_high_b' | 'industrial_low' | 'industrial_high'
  contract_kw         NUMERIC, -- 계약전력 (kW)
  usage_kwh           NUMERIC, -- 당월 사용량 (kWh)
  bill_total          NUMERIC, -- 총 청구금액 (원)
  base_charge         NUMERIC, -- 기본요금
  energy_charge       NUMERIC, -- 전력량요금
  climate_charge      NUMERIC, -- 기후환경요금
  fuel_adjustment     NUMERIC, -- 연료비조정액
  prev_usage_kwh      NUMERIC, -- 전월 사용량
  yoy_usage_kwh       NUMERIC, -- 전년동월 사용량

  -- 고압 계약 전용 (선택)
  power_factor        NUMERIC, -- 역률 (%)
  peak_demand_kw      NUMERIC, -- 최대수요전력 (kW)

  -- 고객 직접 입력
  industry_type       TEXT,    -- 업종 (아래 코드 참조)
  building_area_m2    NUMERIC, -- 건물 면적 (m², 선택)
  daily_operation_h   NUMERIC, -- 일평균 영업시간
  night_usage_ratio   NUMERIC, -- 야간 사용 비율 (%) 선택

  -- 기기 정보 (선택, JSONB)
  devices             JSONB DEFAULT '[]',

  -- AI 분석 결과
  analysis_result     JSONB,   -- 계산 엔진 출력값
  ai_narrative        TEXT,    -- Claude 생성 문구

  -- 결제 정보
  payment_id          TEXT,    -- 토스페이먼츠 결제키
  paid_amount         NUMERIC,
  paid_at             TIMESTAMP,
  customer_email      TEXT,

  -- 리포트
  report_url          TEXT     -- Supabase Storage URL
);
```

#### `devices` JSONB 구조 (diagnoses.devices 배열)
```json
[
  {
    "device_id": "uuid",
    "name": "에어컨 (거실)",
    "category": "cooling",
    "rated_power_w": 2000,
    "daily_usage_h": 8,
    "count": 1,
    "image_url": "https://...",
    "ai_extracted": true,
    "monthly_kwh": 480,
    "monthly_cost": 68640
  }
]
```

#### `admin_stats` (일별 집계, 자동 업데이트)
```sql
CREATE TABLE admin_stats (
  date          DATE PRIMARY KEY,
  total_visits  INTEGER DEFAULT 0,
  previews      INTEGER DEFAULT 0,
  payments      INTEGER DEFAULT 0,
  revenue       NUMERIC DEFAULT 0
);
```

---

## 3. 계산 엔진 (`src/lib/calculator.js`)

### 3-1. 한전 요금 테이블 (`kepco-rates.js`)

```javascript
// 산업통상자원부 고시 제2024-1호 기준
export const KEPCO_RATES = {
  general_low: {
    name: '일반용 저압',
    base_rate_per_kw: 6160, // 원/kW
    energy_rates: {
      // 시간대별 단가 (원/kWh)
      summer: { peak: 109.0, mid: 68.5, off: 54.8 },    // 7~8월
      spring_fall: { peak: 99.0, mid: 62.5, off: 54.8 }, // 3~6, 9~10월
      winter: { peak: 111.9, mid: 72.0, off: 58.0 }      // 11~2월
    }
  },
  general_high_a: {
    name: '일반용 고압A',
    base_rate_per_kw: 8190,
    energy_rates: {
      summer: { peak: 154.0, mid: 101.8, off: 57.0 },
      spring_fall: { peak: 115.0, mid: 80.5, off: 57.0 },
      winter: { peak: 156.0, mid: 103.7, off: 68.5 }
    }
  },
  industrial_low: {
    name: '산업용 저압',
    base_rate_per_kw: 7220,
    energy_rates: {
      summer: { peak: 148.0, mid: 99.0, off: 57.3 },
      spring_fall: { peak: 109.0, mid: 73.3, off: 57.3 },
      winter: { peak: 148.8, mid: 99.8, off: 63.6 }
    }
  }
  // ... 추가 계약종별
};

export const POWER_FACTOR_RATES = {
  // 역률별 기본요금 조정률
  // 90% 기준: 미달 시 1%당 +0.2%, 초과 시 1%당 -0.2%
  calculate: (base_charge, power_factor) => {
    if (!power_factor) return { adjustment: 0, adjusted_charge: base_charge };
    const diff = power_factor - 90;
    const adjustment_rate = diff * 0.002; // 양수=할인, 음수=할증
    const adjustment = base_charge * adjustment_rate;
    return {
      adjustment,
      adjusted_charge: base_charge - adjustment,
      is_penalty: diff < 0,
      is_discount: diff > 0
    };
  }
};
```

### 3-2. 업종 벤치마크 (`benchmark.js`)

```javascript
// 한국에너지공단 에너지통계연보 2024 기준
export const INDUSTRY_BENCHMARKS = {
  restaurant: {
    name: '음식점',
    avg_kwh_per_m2_year: 380,
    avg_cost_per_kwh: 142,
    avg_base_ratio: 0.32,
    avg_utilization: 0.68
  },
  retail: {
    name: '소매업',
    avg_kwh_per_m2_year: 290,
    avg_cost_per_kwh: 138,
    avg_base_ratio: 0.35,
    avg_utilization: 0.72
  },
  manufacturing: {
    name: '제조업',
    avg_kwh_per_m2_year: 520,
    avg_cost_per_kwh: 128,
    avg_base_ratio: 0.28,
    avg_utilization: 0.78
  },
  office: {
    name: '사무실',
    avg_kwh_per_m2_year: 220,
    avg_cost_per_kwh: 145,
    avg_base_ratio: 0.40,
    avg_utilization: 0.65
  },
  warehouse: {
    name: '창고·물류',
    avg_kwh_per_m2_year: 180,
    avg_cost_per_kwh: 125,
    avg_base_ratio: 0.38,
    avg_utilization: 0.70
  }
};
```

### 3-3. 핵심 계산 함수 (`calculator.js`)

```javascript
export function runFullAnalysis(input) {
  const {
    contract_type, contract_kw, usage_kwh, bill_total,
    base_charge, energy_charge, power_factor, peak_demand_kw,
    industry_type, building_area_m2, devices = []
  } = input;

  const rate = KEPCO_RATES[contract_type];
  const benchmark = INDUSTRY_BENCHMARKS[industry_type] || null;

  // ── 1. 파생 지표 계산
  const derived = {
    cost_per_kwh: bill_total / usage_kwh,
    base_charge_ratio: base_charge / bill_total,
    utilization_rate: peak_demand_kw ? peak_demand_kw / contract_kw : null,
    energy_intensity: building_area_m2 ? (usage_kwh * 12) / building_area_m2 : null
  };

  // ── 2. 진단 항목 판정
  const diagnoses = [];

  // 진단 A: 계약전력 과잉
  const CONTRACT_OVER_THRESHOLD = 0.65;
  const BASE_RATIO_THRESHOLD = 0.45;
  if (derived.base_charge_ratio > BASE_RATIO_THRESHOLD ||
     (derived.utilization_rate && derived.utilization_rate < CONTRACT_OVER_THRESHOLD)) {
    const estimated_actual_kw = peak_demand_kw
      ? peak_demand_kw * 1.1
      : contract_kw * 0.6; // 추정값
    const optimal_kw = Math.ceil(estimated_actual_kw / 5) * 5; // 5kW 단위 올림
    const monthly_saving = (contract_kw - optimal_kw) * rate.base_rate_per_kw;
    diagnoses.push({
      id: 'contract_power_excess',
      severity: 'critical',
      title: '계약전력 과잉',
      current: `${contract_kw}kW`,
      optimal: `${optimal_kw}kW`,
      monthly_saving,
      annual_saving: monthly_saving * 12,
      basis: '한전 전기공급약관 제43조',
      action: `계약전력 ${contract_kw}kW → ${optimal_kw}kW 변경 신청`,
      how_to: '한전 고객센터 123 또는 한전 ON 앱 → 계약전력 변경 신청'
    });
  }

  // 진단 B: 역률 불량 (고압만)
  if (power_factor && power_factor < 90) {
    const penalty_rate = (90 - power_factor) * 0.002;
    const monthly_penalty = base_charge * penalty_rate;
    const target_pf = 95;
    const discount_rate = (target_pf - 90) * 0.002;
    const monthly_discount = base_charge * discount_rate;
    diagnoses.push({
      id: 'power_factor_penalty',
      severity: 'warning',
      title: '역률 불량으로 인한 할증요금',
      current: `역률 ${power_factor}%`,
      optimal: '역률 95% 이상',
      monthly_saving: monthly_penalty + monthly_discount,
      annual_saving: (monthly_penalty + monthly_discount) * 12,
      basis: '한전 전기공급약관 제72조',
      action: '진상 콘덴서 설치로 역률 개선',
      roi_months: 500000 / (monthly_penalty + monthly_discount) // 콘덴서 50만원 가정
    });
  }

  // 진단 C: 고단가 계약종 (사용량 기준 전환 타당성)
  if (contract_type === 'general_low' && usage_kwh > 2000) {
    const current_energy_rate = energy_charge / usage_kwh;
    const high_a_rate = KEPCO_RATES.general_high_a;
    const estimated_high_a_cost = usage_kwh * (high_a_rate.energy_rates.spring_fall.mid);
    const monthly_diff = energy_charge - estimated_high_a_cost;
    if (monthly_diff > 30000) {
      diagnoses.push({
        id: 'contract_type_upgrade',
        severity: 'info',
        title: '계약종별 변경 검토',
        current: '일반용 저압',
        optimal: '일반용 고압A',
        monthly_saving: monthly_diff,
        annual_saving: monthly_diff * 12,
        basis: '산업통상자원부 고시 제2024-1호',
        action: '일반용 고압A 전환 신청',
        caveat: '수전설비 공사비 약 300~500만원 발생. 월 절감액 기준 ROI 계산 필수.'
      });
    }
  }

  // ── 3. 기기 분석 (선택 입력 시)
  let device_analysis = null;
  if (devices.length > 0) {
    const device_total_kwh = devices.reduce((sum, d) => {
      return sum + (d.rated_power_w * d.daily_usage_h * 30 / 1000) * d.count;
    }, 0);
    const device_total_cost = device_total_kwh * (bill_total / usage_kwh);
    const unknown_kwh = usage_kwh - device_total_kwh;
    const unknown_cost = unknown_kwh * (bill_total / usage_kwh);

    device_analysis = {
      device_total_kwh: Math.round(device_total_kwh),
      device_total_cost: Math.round(device_total_cost),
      unknown_kwh: Math.max(0, Math.round(unknown_kwh)),
      unknown_cost: Math.max(0, Math.round(unknown_cost)),
      unknown_ratio: Math.max(0, unknown_kwh / usage_kwh),
      devices_breakdown: devices.map(d => ({
        ...d,
        monthly_kwh: Math.round(d.rated_power_w * d.daily_usage_h * 30 / 1000),
        monthly_cost: Math.round(d.rated_power_w * d.daily_usage_h * 30 / 1000 * (bill_total / usage_kwh))
      }))
    };
  }

  // ── 4. 벤치마크 비교
  let benchmark_result = null;
  if (benchmark) {
    benchmark_result = {
      cost_per_kwh_percentile: calcPercentile(derived.cost_per_kwh, benchmark.avg_cost_per_kwh),
      base_ratio_vs_avg: derived.base_charge_ratio - benchmark.avg_base_ratio,
      utilization_vs_avg: derived.utilization_rate
        ? derived.utilization_rate - benchmark.avg_utilization
        : null
    };
  }

  // ── 5. 절감 시나리오 3가지
  const total_monthly_saving = diagnoses.reduce((sum, d) => sum + d.monthly_saving, 0);
  const scenarios = {
    conservative: {
      label: 'A. 보수적 (즉시 실행)',
      actions: diagnoses.filter(d => d.severity === 'critical').map(d => d.action),
      monthly_saving: diagnoses
        .filter(d => d.severity === 'critical')
        .reduce((sum, d) => sum + d.monthly_saving, 0),
      annual_saving: diagnoses
        .filter(d => d.severity === 'critical')
        .reduce((sum, d) => sum + d.annual_saving, 0)
    },
    moderate: {
      label: 'B. 중간 (+현장 CT 측정)',
      actions: [...diagnoses.filter(d => d.severity !== 'info').map(d => d.action), 'CT센서 2주 현장 측정'],
      monthly_saving: total_monthly_saving * 0.75,
      annual_saving: total_monthly_saving * 0.75 * 12
    },
    aggressive: {
      label: 'C. 적극적 (종합 최적화)',
      actions: [...diagnoses.map(d => d.action), 'CT센서 정밀 측정 + 스마트 자동제어'],
      monthly_saving: total_monthly_saving,
      annual_saving: total_monthly_saving * 12
    }
  };

  return {
    derived,
    diagnoses,
    device_analysis,
    benchmark_result,
    scenarios,
    total_annual_saving: scenarios.aggressive.annual_saving
  };
}

function calcPercentile(value, avg) {
  // 단순 상대 위치 계산 (0~100%)
  const ratio = value / avg;
  if (ratio < 0.8) return { label: '상위 20% (매우 효율적)', percentile: 20, color: 'green' };
  if (ratio < 1.0) return { label: '상위 40% (양호)', percentile: 40, color: 'blue' };
  if (ratio < 1.2) return { label: '하위 40% (개선 필요)', percentile: 60, color: 'yellow' };
  return { label: '하위 20% (즉시 개선 필요)', percentile: 80, color: 'red' };
}
```

---

## 4. Claude API 연동 (`src/lib/claude-api.js`)

### 4-1. 고지서 이미지 파싱

```javascript
export async function parseBillImage(imageBase64) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: { type: 'base64', media_type: 'image/jpeg', data: imageBase64 }
          },
          {
            type: 'text',
            text: `이 한국전력공사(KEPCO) 전기요금 고지서에서 다음 항목을 JSON으로 추출해주세요.
반드시 JSON만 출력하고 다른 텍스트는 절대 포함하지 마세요.

{
  "contract_type": "general_low | general_high_a | general_high_b | industrial_low | industrial_high | 알수없음",
  "contract_kw": 숫자 또는 null,
  "usage_kwh": 숫자 또는 null,
  "bill_total": 숫자 또는 null,
  "base_charge": 숫자 또는 null,
  "energy_charge": 숫자 또는 null,
  "climate_charge": 숫자 또는 null,
  "power_factor": 숫자 또는 null,
  "peak_demand_kw": 숫자 또는 null,
  "prev_usage_kwh": 숫자 또는 null,
  "yoy_usage_kwh": 숫자 또는 null,
  "confidence": "high | medium | low"
}`
          }
        ]
      }]
    })
  });
  const data = await response.json();
  const text = data.content[0].text;
  return JSON.parse(text.replace(/```json|```/g, '').trim());
}
```

### 4-2. 기기 이미지 파싱

```javascript
export async function parseDeviceImage(imageBase64, deviceHint = '') {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: { type: 'base64', media_type: 'image/jpeg', data: imageBase64 }
          },
          {
            type: 'text',
            text: `이 전자기기의 스펙 라벨 또는 제품에서 전력 정보를 JSON으로 추출해주세요.
추가 힌트: ${deviceHint || '없음'}
JSON만 출력하세요.

{
  "device_name": "기기명 (예: 에어컨, 냉장고, 전자레인지)",
  "category": "cooling | heating | refrigeration | cooking | lighting | other",
  "rated_power_w": 숫자 또는 null,
  "model_name": "모델명 또는 null",
  "confidence": "high | medium | low",
  "note": "특이사항 또는 null"
}`
          }
        ]
      }]
    })
  });
  const data = await response.json();
  return JSON.parse(data.content[0].text.replace(/```json|```/g, '').trim());
}
```

### 4-3. 리포트 AI 해설 문구 생성

```javascript
export async function generateNarrative(analysisResult) {
  const { diagnoses, scenarios, derived, device_analysis } = analysisResult;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{
        role: 'user',
        content: `당신은 에너지 절감 전문 컨설턴트입니다.
아래 분석 데이터를 바탕으로 고객에게 전달할 전문적이고 신뢰감 있는 해설 문구를 작성해주세요.
JSON 형식으로만 출력하세요. 한국어로 작성.

분석 데이터:
${JSON.stringify({ diagnoses, scenarios, derived }, null, 2)}

출력 형식:
{
  "executive_summary": "2~3줄 종합 요약 (숫자 포함, 전문적 톤)",
  "key_finding": "가장 중요한 발견 1가지를 1줄로",
  "diagnosis_comments": {
    "contract_power_excess": "계약전력 관련 설명 (있을 때만)",
    "power_factor_penalty": "역률 관련 설명 (있을 때만)",
    "contract_type_upgrade": "계약종별 관련 설명 (있을 때만)"
  },
  "cta_message": "현장 컨설팅으로 연결하는 자연스러운 1줄 문구"
}`
      }]
    })
  });
  const data = await response.json();
  return JSON.parse(data.content[0].text.replace(/```json|```/g, '').trim());
}
```

---

## 5. 사용자 플로우 상세 설계

### STEP 1 — 고지서 입력 (`Step1_Bill.jsx`)

```
입력 방식 선택 (탭 UI):
  ┌─────────────────────┬────────────────────────┐
  │  📸 고지서 사진 업로드  │  ✏️ 수치 직접 입력      │
  └─────────────────────┴────────────────────────┘

[사진 업로드 탭]
  - 드래그&드롭 또는 파일 선택
  - 업로드 후 Claude API로 자동 파싱
  - 파싱된 값 편집 가능하게 표시 (확인 UX)
  - confidence: low인 항목은 노란색으로 표시 + 직접 입력 유도

[직접 입력 탭]
  필수 항목:
    - 계약종별 (드롭다운)
      └ 일반용 저압 / 일반용 고압A / 일반용 고압B
        산업용 저압 / 산업용 고압 / 교육용
    - 계약전력 (숫자, kW)
    - 당월 사용량 (숫자, kWh)
    - 총 청구금액 (숫자, 원)
    - 기본요금 (숫자, 원)
    - 전력량요금 (숫자, 원)

  선택 항목 (펼치기 버튼):
    - 전월 사용량 (kWh)
    - 전년동월 사용량 (kWh)
    - 역률 (%, 고압 계약 시 표시)
    - 최대수요전력 (kW, 고압 계약 시 표시)

  고객 추가 입력:
    - 업종 선택 (드롭다운)
      └ 음식점/카페 / 소매업/편의점 / 제조업 / 사무실
        창고/물류 / 숙박업 / 기타
    - 건물 면적 (m², 선택)
    - 일평균 영업시간 (선택)
```

### STEP 2 — 기기 입력 (`Step2_Devices.jsx`)

```
[헤더]
"기기 정보를 추가하면 더 정밀한 분석이 가능합니다 (선택사항)"
"추가하지 않아도 기본 리포트는 받을 수 있습니다"

[건너뛰기 버튼] → STEP 3으로 이동

[기기 추가 UI]
  기기 카테고리 선택 버튼:
  [ ❄️ 냉방기기 ] [ 🔥 난방기기 ] [ 🧊 냉장/냉동 ]
  [ 🍳 조리기기 ] [ 💡 조명 ] [ 🏭 기계/설비 ] [ 기타 ]

  기기 입력 카드 (카테고리 선택 후):
    ┌──────────────────────────────────────────┐
    │ 📸 사진으로 자동 인식   OR  ✏️ 직접 입력  │
    ├──────────────────────────────────────────┤
    │ 기기명: [에어컨 (거실)              ]   │
    │ 소비전력: [2000] W                      │
    │ 하루 사용시간: [8] 시간                  │
    │ 수량: [1] 대                            │
    ├──────────────────────────────────────────┤
    │ 예상 월 전기요금: 약 68,640원           │
    └──────────────────────────────────────────┘

  [+ 기기 추가] 버튼

  하단 실시간 합산:
  "현재 입력된 기기 합계: 월 예상 XXX,XXX원 / XXXkWh"
```

### STEP 3 — 무료 미리보기 (`Step3_Preview.jsx`)

```
[무료 공개 영역]
  ┌─────────────────────────────────────────┐
  │  ⚡ 분석 완료                            │
  │                                         │
  │  귀사의 연간 절감 가능 금액              │
  │  ┌───────────────────────────────────┐  │
  │  │     최대 2,340,000원              │  │
  │  └───────────────────────────────────┘  │
  │                                         │
  │  🔴 계약전력 과잉 감지                  │
  │  🟡 고단가 계약종 유지                  │
  │  🟢 사용량 패턴 양호                    │
  └─────────────────────────────────────────┘

[페이월 — 블러 처리 영역]
  ╔═════════════════════════════════════════╗
  ║  🔒  정밀 분석 리포트 확인하기          ║
  ║                                         ║
  ║  • 계약전력 최적값 계산 (한전 약관 기준) ║
  ║  • 업종 평균 대비 정확한 위치           ║
  ║  • 3가지 절감 시나리오 및 ROI           ║
  ║  • 즉시 실행 가능한 단계별 행동 지침    ║
  ║  • PDF 다운로드 + 이메일 발송           ║
  ║                                         ║
  ║  ┌─────────────────────────────────┐   ║
  ║  │   정밀 리포트 받기 — 39,000원   │   ║
  ║  └─────────────────────────────────┘   ║
  ╚═════════════════════════════════════════╝
```

### STEP 4 — 결제 (`Step4_Payment.jsx`)

```
토스페이먼츠 위젯 임베드
  - 금액: 39,000원
  - 상품명: "BRING 전기요금 절감 진단 리포트"
  - 이메일 입력 (리포트 발송용, 필수)
  - 결제 수단: 카드 / 계좌이체 / 카카오페이 / 네이버페이

결제 성공 시:
  → Supabase diagnoses.status = 'paid'
  → Resend로 이메일 발송 (PDF 첨부)
  → STEP 5로 리다이렉트
```

### STEP 5 — 리포트 (`Step5_Report.jsx`)

```
[전체 리포트 표시]
  - ReportCover + Page1~4 + ReportFooter 순서로 렌더링
  - Chart.js 차트 포함

[액션 버튼]
  [ 📥 PDF 다운로드 ] [ 📧 이메일로 받기 ] [ 📞 현장 상담 신청 ]
```

---

## 6. PDF 생성 (`src/lib/pdf-generator.js`)

```javascript
import html2pdf from 'html2pdf.js';

export async function generatePDF(reportElement, filename) {
  const options = {
    margin: 0,
    filename: filename || 'BRING_전기요금절감_진단리포트.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      logging: false
    },
    jsPDF: {
      unit: 'mm',
      format: 'a4',
      orientation: 'portrait'
    },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
  };

  return html2pdf().set(options).from(reportElement).save();
}
```

---

## 7. 결제 연동 (`src/hooks/usePayment.js`)

```javascript
// 토스페이먼츠 v2 SDK 기준
import { loadTossPayments } from '@tosspayments/payment-sdk';

export function usePayment() {
  const initiatePayment = async ({ diagnosisId, customerEmail }) => {
    const tossPayments = await loadTossPayments(import.meta.env.VITE_TOSS_CLIENT_KEY);

    await tossPayments.requestPayment('카드', {
      amount: 39000,
      orderId: `bring-${diagnosisId}-${Date.now()}`,
      orderName: 'BRING 전기요금 절감 진단 리포트',
      customerEmail,
      successUrl: `${window.location.origin}/report/${diagnosisId}?payment=success`,
      failUrl: `${window.location.origin}/payment/fail`,
    });
  };

  return { initiatePayment };
}
```

---

## 8. 환경 변수 (`.env`)

```bash
# Anthropic
VITE_ANTHROPIC_API_KEY=sk-ant-...

# Supabase
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...

# 토스페이먼츠
VITE_TOSS_CLIENT_KEY=test_ck_...

# Resend (이메일)
VITE_RESEND_API_KEY=re_...

# 관리자
VITE_ADMIN_PASSWORD=bring2026
```

---

## 9. 관리자 대시보드 (`pages/Admin.jsx`)

```
접속: /admin?pw=bring2026

표시 항목:
  ┌─────────┬─────────┬──────────┬──────────────┐
  │ 오늘 방문 │ 미리보기 │ 결제 건수 │  오늘 매출   │
  │   142   │   38   │    7    │  273,000원   │
  └─────────┴─────────┴──────────┴──────────────┘

  전환율 표시: 방문→미리보기 26.8% / 미리보기→결제 18.4%

  최근 진단 목록 테이블:
  | 시간 | 계약종별 | 절감예측 | 결제여부 | 이메일 |
```

---

## 10. 개발 우선순위 (스프린트 플랜)

```
Sprint 1 (1주): 핵심 계산 엔진
  ✅ kepco-rates.js 완성
  ✅ benchmark.js 완성
  ✅ calculator.js 완성
  ✅ 계산 결과 콘솔 검증

Sprint 2 (1주): 입력 + 미리보기 UI
  ✅ Step1_Bill.jsx (직접 입력 탭 먼저)
  ✅ Step3_Preview.jsx (무료 미리보기)
  ✅ 페이월 UI

Sprint 3 (1주): 리포트 + PDF
  ✅ Page1~4 컴포넌트
  ✅ Chart.js 차트
  ✅ pdf-generator.js

Sprint 4 (1주): 결제 + 배포
  ✅ 토스페이먼츠 연동
  ✅ Supabase DB 연동
  ✅ Resend 이메일 발송
  ✅ Vercel 배포

Sprint 5 (추가): AI 이미지 기능
  ✅ 고지서 사진 → Claude API 파싱
  ✅ 기기 사진 → Claude API 파싱
  ✅ AI 해설 문구 생성
```

---

## 11. Claude Code 실행 프롬프트

```
이 BRING_SPEC.md 파일을 읽고 전기요금 절감 진단 SaaS를 개발해줘.

기술 스택:
- React + Vite + Tailwind CSS
- Supabase (DB + Storage)
- Claude API (이미지 파싱 + 문구 생성)
- 토스페이먼츠 v2
- Vercel 배포

개발 순서:
1. package.json 생성 및 의존성 설치
2. src/lib/kepco-rates.js, benchmark.js, calculator.js 구현
3. calculator.js 단위 테스트 (콘솔 출력으로 검증)
4. Step1, Step3 페이지 UI 구현
5. 리포트 컴포넌트 4페이지 구현
6. 결제 연동

.env 파일은 내가 직접 채울게. 일단 placeholder로 만들어줘.
Sprint 1부터 순서대로 진행해줘.
```

---

*BRING Engineering · 본 문서는 Claude Code 개발 전용 마스터 스펙입니다*

