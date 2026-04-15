# bring-energy — 임시 거주지 폴더

> ⚠️ **이 폴더는 임시 거주지입니다.**
> 본 폴더의 내용은 향후 별도 GitHub 리포지토리 `bringengineering/bring-energy`로 이관될 예정입니다.
> 현재 위치한 `rc-decision-engine` 리포지토리와는 **코드·제품적으로 무관**합니다.
> (rc-decision-engine: 염해/부식 physics 시뮬레이션 시스템 / bring-energy: 전기요금 절감 진단 SaaS)

---

## 📦 폴더 목적

브링엔지니어링이 새로 시작하는 **전기요금 절감 진단 SaaS 제품**의 개발 배경 문서와 마스터 스펙을 보관합니다.
다음 Claude Code 세션에서 즉시 개발에 진입할 수 있도록 컨텍스트를 모아둔 곳입니다.

---

## 📂 문서 구성

```
bring-energy/
└── docs/
    ├── 00_BACKGROUND.md         ← 사업·제품 배경 (큐레이션됨)
    └── 01_BRING_SPEC_v1.0.md    ← 마스터 스펙 v1.0 (원본 보존)
```

| 문서 | 역할 | 누가 읽나 |
|------|------|-----------|
| `00_BACKGROUND.md` | 왜 이 제품을 만드는가 — 사업적 맥락, 타깃 고객, 신뢰도 원칙, 사업 확장 로드맵 | 처음 합류하는 개발자, 의사결정자, 미래의 자기 자신 |
| `01_BRING_SPEC_v1.0.md` | 어떻게 만드는가 — 디렉토리, DB 스키마, 계산 엔진, API 연동, Sprint 플랜 | Claude Code, 구현 담당자 |

---

## 🚀 다음 Claude Code 세션 시작 가이드

새 세션에서 이렇게 시작하세요:

1. **먼저 읽기**: `docs/00_BACKGROUND.md` → "왜"를 이해
2. **그다음 읽기**: `docs/01_BRING_SPEC_v1.0.md` → "어떻게"를 이해
3. **Sprint 1부터 착수**: `src/lib/kepco-rates.js` → `benchmark.js` → `calculator.js` 순서로 구현
4. **검증**: 콘솔에서 단위 테스트 후 UI 작업으로 진행

스펙 문서 마지막에 있는 "Claude Code 실행 프롬프트"를 그대로 복붙해서 시작해도 됩니다.

---

## 🛠 향후 이관 절차 (참고)

대표님이 `bringengineering/bring-energy` repo를 새로 만든 후:

```bash
# 새 repo 클론
git clone git@github.com:bringengineering/bring-energy.git
cd bring-energy

# rc-decision-engine의 bring-energy 폴더 내용 복사
cp -r ../rc-decision-engine/bring-energy/* .
git add .
git commit -m "chore: import development background from rc-decision-engine"
git push -u origin main
```

이관 후에는 이 폴더(`rc-decision-engine/bring-energy/`)를 삭제해도 됩니다.

---

*BRING Engineering · 본 폴더는 차세대 전기요금 절감 진단 SaaS의 출발점입니다.*
