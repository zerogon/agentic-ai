"""
Routing Helper for Intent Analysis and Genie Selection
Uses agentic-ai-route-test01 model to analyze user queries and select appropriate Genie domains
"""

import json
from typing import Dict, List
from openai import OpenAI
import streamlit as st
from prompts.manager import load_prompt


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

        # Load system prompt from prompts management system
        self.system_prompt = load_prompt("router_agent")

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
