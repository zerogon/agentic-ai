"""
Routing Helper for Intent Analysis and Genie Selection
Uses agentic-ai-route-test01 model to analyze user queries and select appropriate Genie domains
"""

import json
from typing import Dict, List
from openai import OpenAI
import streamlit as st


class RouteHelper:
    def __init__(self):
        """Initialize Router with Databricks LLM endpoint"""
        self.databricks_token = st.secrets["databricks"]["TOKEN"]
        self.databricks_host = st.secrets["databricks"]["HOST"]

        self.client = OpenAI(
            api_key=self.databricks_token,
            base_url=f"{self.databricks_host}/serving-endpoints"
        )

        self.model_name = "databricks-meta-llama-3-3-70b-instruct"

        # System prompt for routing model
        self.system_prompt = """<role>
너는 Databricks 시스템의 **Phase 1 Router Agent**다.
너의 임무는 사용자의 자연어 질의를 받아
어떤 분석을 수행해야 하는지 결정하고,
어떤 Genie(Databricks Tool)를 호출해야 하는지를 명확히 정의하는 것이다.

단, **INSIGHT_REPORT는 여기서 생성하지 않는다.**
그건 결과 데이터가 도출된 후 Phase 2(Post Processor)가 담당한다.
너는 그저 "이 질의의 마지막엔 INSIGHT_REPORT가 필요하다"고 명시할 뿐이다.

만약 잘못 분류하거나 모호하게 답하면,
Genie는 잘못된 SQL을 실행하고, 잘못된 지표가 대시보드에 노출된다.
그건 곧 데이터 신뢰의 붕괴다.
**너는 이 시스템의 심장이다. 실패는 곧 심정지다.**
</role>

<rules>
1. **Router의 역할**
   - 사용자 질의 → Intent 배열 생성
   - Genie Domain 식별
   - `INSIGHT_REPORT` 포함 여부 명시 (항상 true)
   - `REPORT_GENERATION` intent 감지 (리포트 생성 요청 시)
   - rationale에는 사용자의 질문을 어떻게 이해했고, 어떤 분석 흐름으로 처리할지, 자연스러운 문단으로 작성한다.

2. **Router의 한계**
   - Router는 결과를 요약하거나 해석하지 않는다.
   - summary, next_question, insight 문장 생성 절대 금지.
   - 그건 **Phase 2 Insight Agent**의 역할이다.

3. **rationale 작성 규칙**
   - rationale은 단일 문자열로 작성한다 (dict 형태 아님)
   - 사용자의 질문 이해 내용과 실행 계획을 자연스러운 한국어 문단으로 통합
   - 어떤 분석 흐름으로 처리할지 명확히 기술

4. **GENIE_DOMAIN 규칙**
   - 매출, 실적, 판매, 수익 → SALES_GENIE
   - 계약, 고객, 상품 → CONTRACT_GENIE
   - 지역, 지사, 도시, 지도, 위치 → REGION_GENIE
   - 전체, 요약, 한눈에, 대시보드 → SALES_GENIE + CONTRACT_GENIE (통합형)

   **⚠️ 이전 데이터 참조 규칙 (매우 중요)**
   - "이 데이터", "위 결과", "방금", "이전", "앞서", "해당" 등의 지시대명사 포함 시
     → `intents`: ["INSIGHT_REPORT"]
     → `genie_domain`: [] (새 조회 불필요, 이전 데이터 재사용)

   - 새로운 조회 조건이나 필터 추가 시
     → `intents`: ["DATA_RETRIEVAL", "INSIGHT_REPORT"]
     → `genie_domain`: [해당 도메인] (새 데이터 필요)

5. **REPORT_GENERATION 감지 규칙**
   - "리포트 생성", "보고서", "리포트 만들어", "분석 리포트" 등의 키워드 감지 시
     → `intents`: ["REPORT_GENERATION", "DATA_RETRIEVAL"]
     → `report_type`: 리포트 타입 명시 (monthly_sales, customer_analysis, regional_performance, comprehensive_business 중 선택)
     → `genie_domain`: 리포트 타입에 필요한 도메인 명시

   - 리포트 타입 판단 기준:
     * "월간", "매출" → monthly_sales
     * "고객", "계약" → customer_analysis
     * "지역", "성과" → regional_performance
     * "종합", "전체", "비즈니스" → comprehensive_business

6. **REGION_GENIE 예외**
   - REGION_GENIE가 포함된 경우, rationale 문단에
     "이 분석에는 사전에 정의된 K-Prototypes 알고리즘으로 지역별 군집을 구분하는 단계가 포함됩니다."
     라는 문장을 반드시 추가한다.

7. **출력 형식**
   ```json
   {
     "intents": ["DATA_RETRIEVAL", "VISUALIZATION", "INSIGHT_REPORT"],
     "genie_domain": ["REGION_GENIE", "SALES_GENIE"],
     "keywords": ["서울", "지역", "매출"],
     "report_type": null,
     "rationale": "서울 지역의 매출 현황을 살펴보시려는 걸로 이해했습니다. 우선 Databricks GENIE를 통해 지역별 데이터를 조회하고, 사전에 설정된 K-Prototypes 알고리즘으로 지역을 여러 군집으로 나누어 특징을 분석하겠습니다. 그런 다음 매출 데이터를 함께 결합해 시각적으로 보기 쉽게 정리할 예정입니다. 이 분석이 끝나면 후속 단계에서 전체 결과를 요약하고 정리하는 리포트를 생성하겠습니다.",
     "insight_generation_required": true
   }

   ```json
   // 리포트 생성 요청 예시
   {
     "intents": ["REPORT_GENERATION", "DATA_RETRIEVAL"],
     "genie_domain": ["SALES_GENIE", "CONTRACT_GENIE"],
     "keywords": ["월간", "매출", "리포트"],
     "report_type": "monthly_sales",
     "rationale": "월간 매출 리포트 생성 요청으로 이해했습니다. 먼저 데이터 조건 검증을 수행하고, 조건이 충족되면 SALES_GENIE와 CONTRACT_GENIE를 통해 필요한 데이터를 수집하여 리포트를 생성하겠습니다.",
     "insight_generation_required": true
   }"""

    def analyze_query(self, user_query: str, stream: bool = False):
        """
        Analyze user query and determine intent and Genie domain

        Args:
            user_query: User's question/query
            stream: If True, returns generator for streaming response

        Returns:
            Dict with intents, genie_domain, keywords, rationale, success status
            OR Generator[str] if stream=True
        """
        if stream:
            return self._analyze_query_stream(user_query)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent routing
            )

            # Extract response content
            content = response.choices[0].message.content

            # Parse JSON response
            try:
                # Try to extract JSON from markdown code blocks if present
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                routing_result = json.loads(content)

                return {
                    "success": True,
                    "intents": routing_result.get("intents", []),
                    "genie_domain": routing_result.get("genie_domain", []),
                    "keywords": routing_result.get("keywords", []),
                    "report_type": routing_result.get("report_type"),
                    "rationale": routing_result.get("rationale", ""),
                    "raw_response": content
                }

            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": content,
                    "intents": [],
                    "genie_domain": [],
                    "keywords": [],
                    "report_type": None,
                    "rationale": ""
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Routing model error: {str(e)}",
                "intents": [],
                "genie_domain": [],
                "keywords": [],
                "report_type": None,
                "rationale": ""
            }

    def _analyze_query_stream(self, user_query: str):
        """
        Stream the routing analysis response

        Args:
            user_query: User's question/query

        Yields:
            str: Chunks of the response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                max_tokens=1000,
                temperature=0.1,
                stream=True
            )

            collected_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    collected_content += content_chunk
                    yield content_chunk

            # Store the complete response for later parsing
            self._last_stream_content = collected_content

        except Exception as e:
            yield f"\n\n❌ Error: {str(e)}"
            self._last_stream_content = None

    def parse_last_stream_result(self) -> Dict:
        """
        Parse the last streamed response into structured format

        Returns:
            Dict with intents, genie_domain, keywords, rationale, success status
        """
        if not hasattr(self, '_last_stream_content') or not self._last_stream_content:
            return {
                "success": False,
                "error": "No stream content to parse",
                "intents": [],
                "genie_domain": [],
                "keywords": [],
                "report_type": None,
                "rationale": ""
            }

        content = self._last_stream_content

        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()

            routing_result = json.loads(content)

            return {
                "success": True,
                "intents": routing_result.get("intents", []),
                "genie_domain": routing_result.get("genie_domain", []),
                "keywords": routing_result.get("keywords", []),
                "report_type": routing_result.get("report_type"),
                "rationale": routing_result.get("rationale", ""),
                "raw_response": self._last_stream_content
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": self._last_stream_content,
                "intents": [],
                "genie_domain": [],
                "keywords": [],
                "report_type": None,
                "rationale": ""
            }

    def select_primary_genie(self, genie_domains: List[str]) -> str:
        """
        Select primary Genie from list of domains

        Args:
            genie_domains: List of Genie domain names

        Returns:
            Primary Genie domain name (first in list or default)
        """
        if not genie_domains:
            return "SALES_GENIE"  # Default fallback

        return genie_domains[0]
