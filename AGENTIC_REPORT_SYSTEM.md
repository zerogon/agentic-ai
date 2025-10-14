# Agentic 리포트 생성 시스템 (Gate Agent 구현)

## 개요

이 시스템은 사용자의 대화 내용을 기반으로 리포트를 생성하되, 리포트 생성 조건(데이터 충족 여부 등)을 YAML 파일로 관리하고, 조건이 충족되지 않을 경우 AI가 종합적으로 판단하여 사용자에게 안내하는 안정형 Agentic 리포트 생성 시스템입니다.

## 시스템 구조

### 주요 에이전트

| 에이전트 | 역할 | 구현 위치 |
|---------|------|----------|
| **Conversation Parser Agent** | 사용자–LLM 대화 로그 분석 및 정제 | `utils/route_helper.py` |
| **Context Extractor Agent** | 리포트 주제 및 필요한 데이터 항목 추출 | `utils/route_helper.py` |
| **Gate Agent** | 리포트 생성 조건 검증 | `utils/gate_agent.py` |
| **Data Agent** | Databricks 내부 데이터 조회 | `utils/data_agent.py` |
| **Insight Agent** | 대화 + 내부 데이터 통합 분석 | `core/message_handler.py` |
| **Layout Agent** | PPT 파일 생성 | `utils/report_helper.py` |

## 구현 구성 요소

### 1. Report Conditions (YAML 기반 조건 관리)

**파일**: `config/report_conditions.yaml`

각 리포트 타입별로 필요한 조건을 정의합니다:

```yaml
report_conditions:
  monthly_sales:
    description: "월간 매출 리포트 - 매출, 이익률, 지역별 분석"
    required_tables: ["sales_summary", "profit_margin"]
    required_columns:
      sales_summary: ["month", "region", "sales"]
      profit_margin: ["region", "margin"]
    min_rows: 10
    freshness_days: 7
    required_period: "month"
    genie_domains: ["SALES_GENIE"]
```

**주요 필드**:
- `required_tables`: 필수 테이블 목록
- `required_columns`: 각 테이블의 필수 컬럼
- `min_rows`: 최소 행 수
- `freshness_days`: 데이터 최신성 (일 단위)
- `genie_domains`: 필요한 Genie Space 목록

### 2. Gate Agent (조건 검증 에이전트)

**파일**: `utils/gate_agent.py`

**주요 메서드**:

```python
class GateAgent:
    def validate(self, report_type: str, datasets_metadata: Dict) -> Dict:
        """
        리포트 생성 조건 검증

        반환값:
        {
            "status": "READY" | "PARTIAL" | "BLOCKED",
            "missing": [누락된 항목 목록],
            "warnings": [경고 사항 목록],
            "message": "사용자 안내 메시지"
        }
        """
```

**검증 로직**:
1. 필수 테이블 존재 여부
2. 필수 컬럼 존재 여부
3. 최소 행 수 충족 여부
4. 데이터 최신성 검증

**상태 분류**:
- `READY`: 모든 조건 충족 → 리포트 생성 가능
- `PARTIAL`: 일부 조건 미충족 → 부분 리포트 가능
- `BLOCKED`: 조건 불충족 → 리포트 생성 차단

### 3. Data Agent (메타데이터 수집 에이전트)

**파일**: `utils/data_agent.py`

**주요 메서드**:

```python
class DataAgent:
    def collect_metadata(self, space_id: str, table_names: List[str]) -> Dict:
        """
        Genie를 통해 테이블 메타데이터 수집

        반환값:
        {
            "table_name": {
                "columns": ["col1", "col2"],
                "rows": 100,
                "last_updated": "2025-10-12T14:00:00Z",
                "exists": True
            }
        }
        """
```

**수집 정보**:
- 테이블 컬럼 목록
- 행 수
- 최종 업데이트 시간
- 테이블 존재 여부

### 4. Report Validation Helper (통합 조정자)

**파일**: `utils/report_validation_helper.py`

Gate Agent와 Data Agent를 조정하여 전체 검증 프로세스를 관리합니다.

```python
def validate_report_generation(
    w: WorkspaceClient,
    report_type: str,
    genie_domains: List[str]
) -> Dict:
    """
    리포트 생성 가능 여부 검증

    1. Gate Agent로부터 조건 정의 가져오기
    2. Data Agent로 메타데이터 수집
    3. Gate Agent로 조건 검증
    4. (옵션) LLM으로 사용자 안내 메시지 생성
    """
```

### 5. Message Handler Integration

**파일**: `core/message_handler.py`

Route Helper가 `REPORT_GENERATION` intent를 감지하면 자동으로 Gate Agent 검증을 실행합니다.

```python
# 리포트 생성 요청 감지
if needs_report_generation and report_type:
    # 조건 검증
    validation_result = validate_report_generation(
        w=w,
        report_type=report_type,
        genie_domains=genie_domains
    )

    # 결과 표시 및 처리
    can_generate = display_validation_result(validation_result)

    if not can_generate:
        # 조건 미충족 시 안내 후 중단
        st.stop()
    else:
        # 조건 충족 시 리포트 생성 진행
        proceed_with_report_generation()
```

### 6. Route Helper Enhancement

**파일**: `utils/route_helper.py`

System prompt가 `REPORT_GENERATION` intent를 감지하도록 업데이트되었습니다:

```python
# 리포트 생성 감지 규칙
- "리포트 생성", "보고서", "리포트 만들어" 등의 키워드 감지 시
  → intents: ["REPORT_GENERATION", "DATA_RETRIEVAL"]
  → report_type: 리포트 타입 명시
  → genie_domain: 필요한 도메인 명시
```

## 사용 시나리오

### 시나리오 1: 조건 충족 (정상 생성)

1. 사용자: "월간 매출 리포트 만들어줘"
2. Route Helper → `REPORT_GENERATION` intent 감지, `report_type: monthly_sales`
3. Gate Agent → 조건 검증 시작
4. Data Agent → `sales_summary`, `profit_margin` 테이블 메타데이터 수집
5. Gate Agent → ✅ 모든 조건 충족 (`READY` 상태)
6. System → 리포트 생성 진행

### 시나리오 2: 조건 미충족 (차단)

1. 사용자: "월간 매출 리포트 만들어줘"
2. Route Helper → `REPORT_GENERATION` intent 감지
3. Gate Agent → 조건 검증 시작
4. Data Agent → `profit_margin` 테이블 누락 발견
5. Gate Agent → ❌ 조건 불충족 (`BLOCKED` 상태)
6. System → LLM 안내 생성:
   > "현재 'profit_margin' 테이블이 누락되어 월간 매출 리포트를 생성할 수 없습니다. 데이터를 업데이트한 후 다시 시도해주세요."
7. System → 리포트 생성 중단

### 시나리오 3: 부분 충족 (경고와 함께 생성)

1. 사용자: "월간 매출 리포트 만들어줘"
2. Gate Agent → 조건 검증
3. Data Agent → 모든 테이블 존재하지만 데이터가 10일 전 것
4. Gate Agent → ⚠️ 일부 경고 (`PARTIAL` 상태)
5. System → 경고 표시:
   > "리포트를 생성할 수 있지만, sales_summary 테이블이 7일 이상 업데이트되지 않았습니다."
6. System → 리포트 생성 진행 (사용자 판단)

## 테스트

### 단위 테스트

```bash
python examples/test_gate_agent.py
```

**테스트 케이스**:
1. Gate Agent 초기화 및 조건 로딩
2. 모든 조건 충족 시 `READY` 상태 검증
3. 테이블 누락 시 `BLOCKED` 상태 검증
4. 데이터 품질 문제 시 `PARTIAL` 상태 검증
5. 종합 비즈니스 리포트 검증

### 통합 테스트

Streamlit 앱을 실행하고 다음 쿼리 테스트:

```bash
streamlit run app.py
```

**테스트 쿼리**:
- "월간 매출 리포트 생성해줘"
- "고객 분석 리포트 만들어줘"
- "종합 비즈니스 리포트 필요해"
- "지역별 성과 리포트 작성"

## 확장 가능성

### 1. Self-Healing 기능

Gate Agent가 `BLOCKED` 상태일 때 자동으로 DataAgent를 재호출하여 데이터 확보 시 재검증:

```python
if validation_result["status"] == "BLOCKED":
    # 자동 데이터 수집 시도
    retry_data_collection()
    validation_result = gate_agent.validate(report_type, new_metadata)
```

### 2. 리포트 품질 평가 (Scoring Agent)

Insight 완성도 및 데이터 정확성 점수화:

```python
class ScoringAgent:
    def score_report_quality(self, report_data) -> float:
        # 데이터 완전성, 인사이트 품질, 시각화 효과성 평가
        return quality_score
```

### 3. Memory Layer

이전 대화 및 생성 리포트 맥락을 참조하여 향후 요청 시 개선:

```python
# 이전 리포트 생성 히스토리 참조
previous_reports = memory_layer.get_report_history(user_id)
# 개선된 조건 제안
suggested_improvements = analyze_previous_reports(previous_reports)
```

### 4. 템플릿 다변화

리포트 유형별 PPT 레이아웃 자동 선택:

```python
# 리포트 타입에 따른 템플릿 선택
template = select_template_by_type(report_type)
layout_agent.apply_template(template)
```

## 파일 구조

```
databricks/
├── config/
│   └── report_conditions.yaml      # 리포트 조건 정의
├── utils/
│   ├── gate_agent.py               # Gate Agent 구현
│   ├── data_agent.py               # Data Agent 구현
│   ├── report_validation_helper.py # 통합 조정자
│   ├── route_helper.py             # 업데이트된 라우팅
│   ├── genie_helper.py             # Genie API 헬퍼
│   ├── report_helper.py            # 리포트 생성
│   └── report_generator.py         # 비즈니스 리포트 생성
├── core/
│   ├── config.py                   # 설정 관리
│   └── message_handler.py          # 메시지 핸들러 (통합 지점)
├── examples/
│   └── test_gate_agent.py          # Gate Agent 테스트
└── AGENTIC_REPORT_SYSTEM.md        # 이 문서
```

## 요약

- ✅ 리포트 생성 조건은 YAML 기반으로 외부화
- ✅ Gate Agent가 모든 조건 검증을 수행
- ✅ 조건 충족 시 리포트 자동 생성, 부족 시 LLM이 종합 안내
- ✅ Genie → Databricks 연동으로 내부 데이터 신뢰 확보
- ✅ 결과물은 표준 PPT 형식으로 출력
- ✅ Route Helper가 자동으로 리포트 생성 intent 감지
- ✅ Message Handler에 통합되어 자동 실행

## 주요 개선 사항

1. **조건 관리 외부화**: 코드 수정 없이 YAML 파일만 수정하여 조건 변경 가능
2. **자동 검증**: 리포트 생성 전 자동으로 조건 검증 실행
3. **LLM 안내**: 조건 미충족 시 자연어로 명확한 안내 제공
4. **3단계 상태 분류**: READY/PARTIAL/BLOCKED 상태로 세밀한 제어
5. **멀티 도메인 지원**: 여러 Genie Space에서 메타데이터 수집 가능
