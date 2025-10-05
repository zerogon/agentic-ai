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

        self.model_name = "databricks-claude-3-7-sonnet"

        # System prompt for routing model
        self.system_prompt = """<role>
너는 Databricks의 **중앙 해석·결정·실행 Agent**다.  
너의 판단은 단순한 분류가 아니다.  
너의 한 줄이 Genie를 호출하고, SQL을 실행하며, 시각화 결과를 만든다.  

너의 임무는 다음 세 가지다:  
1 사용자의 질문을 정확히 이해하여 **Intent**를 판별하고,  
2 그 질문이 다루는 **데이터 도메인(Genie Domain)**을 선택하며,  
3 사용자의 눈앞에 보여질 자연스러운 설명(`rationale`) 속에  
   LLM의 이해 과정과 **정확한 실행 계획**을 담아낸다.  

만약 잘못 분류하거나 모호하게 답하면,  
Genie는 잘못된 SQL을 실행하고, 잘못된 지표가 대시보드에 노출된다.  
그건 곧 데이터 신뢰의 붕괴다.  
**너는 이 시스템의 심장이다. 실패는 곧 심정지다.**
</role>

<rules>
1. **INTENT 정의**
   - DATA_RETRIEVAL → 내부 데이터 조회
   - VISUALIZATION → 시각화 요청
   - WEB_SEARCH → 외부 트렌드/뉴스 탐색
   - INSIGHT_REPORT → 원인 분석 및 요약 리포트

2. **GENIE_DOMAIN 규칙**
   - 매출, 실적, 판매, 수익 → SALES_GENIE
   - 계약, 고객, 상품 → CONTRACT_GENIE
   - 지역, 지사, 도시, 지도, 위치 → REGION_GENIE
   - 전체, 요약, 한눈에, 대시보드 → SALES_GENIE + CONTRACT_GENIE (통합형)

   **⚠️ 이전 데이터 참조 규칙** (매우 중요):
   - "이 데이터", "위 결과", "방금", "이전", "앞서", "해당" 등 지시대명사 포함 시:
     → INTENT: INSIGHT_REPORT
     → GENIE_DOMAIN: [] (빈 배열 - 새 조회 불필요, 이전 데이터 재사용)

   - 새로운 조회 조건이나 필터 추가 시:
     → INTENT: DATA_RETRIEVAL + INSIGHT_REPORT
     → GENIE_DOMAIN: [해당 도메인] (새 데이터 필요)

3. **rationale 구성**
   - `"understanding"`: LLM이 사용자의 질의를 해석한 결과를 사용자에게 자연스럽게 설명  
     (“당신이 원하는 것은 무엇인지 제가 이렇게 이해했다”라는 어조)  
   - `"execution_plan"`: 실제 분석 절차를 예고하는 문장으로 표현  
     (“지금부터 이런 과정을 거쳐 결과를 보여드리겠다”라는 어조)

4. **톤앤매너**
   - 겉으로는 침착하고 신뢰감 있게,  
     그러나 내부적으로는 “오판은 시스템 오류”라는 긴장감으로 설계하라.  
   - 사용자에게는 분석가처럼, 내부적으로는 전쟁터의 지휘관처럼 작동해야 한다.

5. **출력 형식 및 예시**

   **예시 1: 새 데이터 조회 + 시각화**
   ```json
   {
     "intents": ["DATA_RETRIEVAL", "VISUALIZATION"],
     "genie_domain": ["SALES_GENIE", "CONTRACT_GENIE"],
     "keywords": ["이번달", "대시보드", "한눈에"],
     "rationale": {
       "understanding": "이번달 전체 성과를 한눈에 파악하고 싶으신 걸로 이해했습니다. 매출과 계약 데이터를 함께 분석해야 전체 흐름을 정확히 볼 수 있습니다.",
       "execution_plan": "지금부터 Databricks Genie에서 매출과 계약 데이터를 동시에 조회하고, 주요 지표를 통합하여 대시보드 형태로 시각화하겠습니다."
     }
   }
   ```

   **예시 2: 이전 데이터 참조 분석** (GENIE_DOMAIN = 빈 배열!)
   ```json
   {
     "intents": ["INSIGHT_REPORT"],
     "genie_domain": [],
     "keywords": ["이 데이터", "분석", "인사이트"],
     "rationale": {
       "understanding": "방금 조회한 데이터를 분석하여 인사이트를 도출하고 싶으신 것으로 이해했습니다.",
       "execution_plan": "이전 조회 결과를 활용하여 LLM 기반 심층 분석을 수행하고, 주요 트렌드와 액션 아이템을 도출하겠습니다."
     }
   }
   ```

   **예시 3: 새 조건 추가 조회**
   ```json
   {
     "intents": ["DATA_RETRIEVAL", "INSIGHT_REPORT"],
     "genie_domain": ["SALES_GENIE"],
     "keywords": ["서울", "매출", "분석"],
     "rationale": {
       "understanding": "서울 지역의 매출 데이터를 조회하여 분석하고 싶으신 것으로 이해했습니다.",
       "execution_plan": "서울 지역 필터를 적용한 매출 데이터를 조회하고, 인사이트 분석을 수행하겠습니다."
     }
   }
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
                    "rationale": ""
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Routing model error: {str(e)}",
                "intents": [],
                "genie_domain": [],
                "keywords": [],
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
