# 🧩 Agentic 리포트 생성 시스템 — 개발 To-Do List

## 1️⃣ 기능 개요
**목표**  
사용자의 대화 내용을 기반으로 리포트를 생성하되,  
리포트 생성 조건(데이터 충족 여부 등)을 **파일로 관리**하고,  
조건이 충족되지 않을 경우 **AI가 종합적으로 판단하여 사용자에게 안내**하는  
안정형 Agentic 리포트 생성 기능을 구현한다.

---

## 2️⃣ 시스템 구조 구성

### 🧠 주요 에이전트 및 역할 정의

| 에이전트 | 핵심 역할 | 비고 |
|-----------|------------|------|
| **Conversation Parser Agent** | 사용자–LLM 대화 로그 분석 및 정제 | 발화 유형 분류 (`question`, `data_request`, `insight`) |
| **Context Extractor Agent** | 리포트 주제 및 필요한 데이터 항목 추출 | 리포트 타입(`monthly_sales`, `customer_analysis`) 식별 |
| **Gate Agent** | 리포트 생성 조건 검증 | YAML 파일 기반 규칙 관리 |
| **Data Agent (Genie 연동)** | Databricks 내부 데이터 조회 | Genie Space Tool 기반 NL→SQL 변환 |
| **Insight Agent** | 대화 + 내부 데이터 통합 분석 | LLM 기반 코멘트 생성 |
| **Layout Agent** | PPT 파일 생성 (좌: 그래프 / 우: 코멘트) | 템플릿 기반 자동 배치 |

---

## 3️⃣ 기능 개발 To-Do List

### 📂 A. 리포트 생성 조건 관리 (Gate Agent 중심)

1. **리포트 조건 정의 파일 생성 (`report_conditions.yaml`)**
   - 리포트별 필수 테이블, 컬럼, 최소 행수, 데이터 최신성, 기간 조건 등 정의
   - 예시:
     ```yaml
     report_conditions:
       monthly_sales:
         required_tables: ["sales_summary", "profit_margin"]
         required_columns:
           sales_summary: ["month", "region", "sales"]
           profit_margin: ["region", "margin"]
         min_rows: 10
         freshness_days: 7
         required_period: "month"
       customer_analysis:
         required_tables: ["customer_info", "contracts"]
         required_columns:
           customer_info: ["customer_id", "segment"]
           contracts: ["contract_id", "status"]
         min_rows: 50
         freshness_days: 30
     ```

2. **Gate Agent 로직 설계**
   - 조건 파일(YAML) 로드 및 캐싱 모듈 개발
   - 데이터셋 메타데이터(`columns`, `rows`, `last_updated`)와 비교
   - 상태값 반환:
     - `READY` : 조건 충족 → 리포트 생성 가능
     - `PARTIAL` : 일부 조건 미충족 → 부분 리포트 가능
     - `BLOCKED` : 조건 불충족 → 리포트 생성 차단

3. **결과 구조화 및 사용자 안내**
   - `GateAgent.validate()`의 반환값을 JSON 형식으로 표준화  
     ```json
     {
       "report_type": "monthly_sales",
       "status": "BLOCKED",
       "missing": ["profit_margin"],
       "message": "이익률 데이터가 누락되어 리포트를 생성할 수 없습니다."
     }
     ```
   - 결과 메시지를 LLM Prompt로 전달 → 자연어 안내 생성

---

### 🔄 B. 데이터 검증 및 내부 조회

1. **데이터 메타정보 수집 프로세스**
   - Genie Space Tool을 통해 Databricks 테이블 메타데이터 조회  
     (컬럼, 행수, 최종 업데이트일 등)
   - `datasets_metadata` 구조 예시:
     ```json
     {
       "sales_summary": {
         "columns": ["month", "region", "sales"],
         "rows": 84,
         "last_updated": "2025-10-12T14:00:00Z"
       },
       "profit_margin": {
         "columns": ["region", "margin"],
         "rows": 80,
         "last_updated": "2025-10-11T10:00:00Z"
       }
     }
     ```

2. **Data Agent (Genie)**
   - 내부 데이터 조회용 NL→SQL 프롬프트 정의
   - 조건 충족 시 DataFrame 형태로 리포트 작성 단계로 전달

---

### 🧠 C. 리포트 생성 및 사용자 안내 로직

1. **리포트 생성 트리거**
   - GateAgent의 `status == "READY"`일 때만 리포트 파이프라인 실행

2. **조건 미충족 시 사용자 안내**
   - GateAgent 결과를 LLM Prompt로 전달
   - LLM이 자연어 형태로 종합 피드백 생성
   - 예시 응답:
     > “현재 ‘profit_margin’ 테이블이 최신 상태가 아니어서 월간 매출 리포트를 생성할 수 없습니다.  
     > 데이터를 업데이트한 후 다시 시도해주세요.”

3. **Insight & Layout Agent 파이프라인**
   - Insight Agent: 데이터 요약 + 인사이트 문장 생성  
   - Layout Agent: PPT 자동 생성 (좌측 그래프 / 우측 코멘트 배치)

---

### 🧩 D. 구조 및 연동 구성

1. **Databricks 통합**
   - Genie Space Tool API 연결  
   - 내부 데이터 접근용 토큰 관리 (`DATABRICKS_HOST`, `GENIE_SPACE_ID`, `TOKEN` 등)

2. **YAML Condition Store 업데이트 프로세스**
   - 신규 리포트 추가 시 YAML에만 정의 추가  
   - 운영 중 조건 수정 시 코드 변경 없이 반영 가능

3. **PPT 템플릿 관리**
   - 표준 템플릿 파일(`slide_template.pptx`) 지정  
   - 슬라이드 구조: 좌측 그래프, 우측 텍스트 박스 고정 레이아웃

---

## 4️⃣ 예시 시나리오

1️⃣ 사용자가 챗봇에게 “9월 매출 리포트 만들어줘” 요청  
2️⃣ Conversation Parser → “monthly_sales” 타입 인식  
3️⃣ Context Extractor → 필요한 데이터 항목(`sales_summary`, `profit_margin`) 식별  
4️⃣ Data Agent → Genie 통해 데이터 메타정보 수집  
5️⃣ Gate Agent → YAML 조건 검사  
   - ✅ 조건 충족 → 리포트 생성  
   - ❌ 조건 부족 → LLM이 부족 항목 종합 안내  
6️⃣ Insight & Layout Agent → PPT 생성 및 반환  

---

## 5️⃣ 예상 산출물

| 산출물 | 설명 |
|--------|------|
| `report_conditions.yaml` | 리포트 생성 조건 정의 파일 |
| `gate_agent.py` | 조건 검증 및 상태 반환 모듈 |
| `datasets_metadata.json` | Databricks 테이블 메타정보 |
| `final_report.pptx` | 생성된 리포트 파일 |
| 사용자 안내 메시지 | 조건 미충족 시 AI가 자연어로 전달하는 피드백 |

---

## 6️⃣ 향후 확장 고려사항

- **Self-Healing 옵션 추가:**  
  GateAgent가 BLOCKED 상태일 때 자동으로 DataAgent를 재호출하여 데이터 확보 시 재검증  
- **리포트 품질 평가(Scoring Agent):**  
  Insight 완성도 및 데이터 정확성 점수화  
- **Memory Layer:**  
  이전 대화 및 생성 리포트 맥락을 참조하여 향후 요청 시 개선  
- **템플릿 다변화:**  
  리포트 유형별 PPT 레이아웃 자동 선택 기능 추가

---

📍**요약**
- 리포트 생성 조건은 YAML 기반으로 외부화  
- Gate Agent가 모든 조건 검증을 수행  
- 조건 충족 시 리포트 자동 생성, 부족 시 LLM이 종합 안내  
- Genie → Databricks 연동으로 내부 데이터 신뢰 확보  
- 결과물은 표준 PPT 형식으로 출력
