"""
Follow-up Question Generation Helper

Provides utilities for generating and managing follow-up questions
based on chat responses and data analysis results.
"""
import json
import os
import re
from typing import List, Dict, Optional


class FollowupHelper:
    """Helper class for generating and managing follow-up questions."""

    def __init__(self, hardcoded_config_path: Optional[str] = None):
        """
        Initialize FollowupHelper.

        Args:
            hardcoded_config_path: Path to hardcoded questions JSON file
        """
        self.hardcoded_config_path = hardcoded_config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "config",
            "hardcoded_questions.json"
        )
        self.hardcoded_questions = self._load_hardcoded_questions()

    def _load_hardcoded_questions(self) -> Dict:
        """
        Load hardcoded questions from JSON file.

        Returns:
            Dictionary of hardcoded question patterns
        """
        try:
            if os.path.exists(self.hardcoded_config_path):
                with open(self.hardcoded_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load hardcoded questions: {e}")
            return {}

    def detect_question_pattern(self, user_query: str) -> Optional[str]:
        """
        Detect question pattern from user query.

        Args:
            user_query: User's original question

        Returns:
            Pattern key if matched, None otherwise

        Example:
            >>> helper.detect_question_pattern("상위 5개 지역 알려줘")
            "ranking_top_bottom"
        """
        user_query_lower = user_query.lower()

        # Check each pattern
        for pattern_key, pattern_config in self.hardcoded_questions.items():
            keywords = pattern_config.get("keywords", [])

            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in user_query_lower:
                    return pattern_key

        return None

    def get_hardcoded_questions(self, pattern_key: str) -> List[str]:
        """
        Get hardcoded questions for a specific pattern.

        Args:
            pattern_key: Pattern identifier

        Returns:
            List of hardcoded questions (3 questions)

        Example:
            >>> helper.get_hardcoded_questions("ranking_top_bottom")
            ["중간 범위 지역들의 분포는 어떻게 되나요?", ...]
        """
        if pattern_key in self.hardcoded_questions:
            return self.hardcoded_questions[pattern_key].get("questions", [])[:3]
        return []

    def parse_llm_followup_questions(self, llm_response: str) -> List[str]:
        """
        Parse follow-up questions from LLM response.

        LLM response format expected:
        ```
        [분석 내용]

        ---FOLLOWUP_QUESTIONS---
        1. 질문1
        2. 질문2
        3. 질문3
        ```

        Args:
            llm_response: LLM analysis response text

        Returns:
            List of 3 follow-up questions extracted from response

        Example:
            >>> helper.parse_llm_followup_questions(response)
            ["질문1", "질문2", "질문3"]
        """
        # Split by marker
        if "---FOLLOWUP_QUESTIONS---" in llm_response:
            parts = llm_response.split("---FOLLOWUP_QUESTIONS---")
            if len(parts) >= 2:
                questions_section = parts[1].strip()

                # Parse numbered questions
                questions = []
                lines = questions_section.split('\n')

                for line in lines:
                    line = line.strip()
                    # Match patterns like "1. Question" or "1) Question" or "- Question"
                    match = re.match(r'^[\d\-\*\•]\s*[\.\)]\s*(.+)$', line)
                    if match:
                        questions.append(match.group(1).strip())
                    elif line and not line.startswith('#'):
                        # Also accept lines without numbering
                        questions.append(line)

                # Return first 3 questions
                return questions[:3]

        return []

    def get_followup_questions(
        self,
        user_query: str,
        llm_response: str,
        prefer_hardcoded: bool = True
    ) -> List[str]:
        """
        Get follow-up questions with hardcoded override logic.

        Args:
            user_query: User's original question
            llm_response: LLM analysis response (may contain generated questions)
            prefer_hardcoded: If True, use hardcoded questions when available

        Returns:
            List of 3 follow-up questions (hardcoded if available, else LLM-generated)

        Example:
            >>> helper.get_followup_questions(
            ...     "상위 5개 지역 알려줘",
            ...     llm_response,
            ...     prefer_hardcoded=True
            ... )
            ["하드코딩된 질문1", "하드코딩된 질문2", "하드코딩된 질문3"]
        """
        # Step 1: Check for hardcoded questions
        if prefer_hardcoded:
            pattern = self.detect_question_pattern(user_query)
            if pattern:
                hardcoded = self.get_hardcoded_questions(pattern)
                if hardcoded and len(hardcoded) >= 3:
                    return hardcoded[:3]

        # Step 2: Parse LLM-generated questions
        llm_questions = self.parse_llm_followup_questions(llm_response)
        if llm_questions and len(llm_questions) >= 3:
            return llm_questions[:3]

        # Step 3: Fallback to default questions
        return [
            "이 데이터의 시간별 추이를 보여주세요",
            "다른 지역과 비교해주세요",
            "이 결과에 영향을 미치는 요인은 무엇인가요?"
        ]

    def extract_analysis_without_questions(self, llm_response: str) -> str:
        """
        Extract only the analysis part, removing the questions section.

        Args:
            llm_response: Full LLM response with analysis and questions

        Returns:
            Analysis text only (without questions section)

        Example:
            >>> helper.extract_analysis_without_questions(response)
            "#### 📊 데이터 요약\n..."
        """
        if "---FOLLOWUP_QUESTIONS---" in llm_response:
            return llm_response.split("---FOLLOWUP_QUESTIONS---")[0].strip()
        return llm_response
