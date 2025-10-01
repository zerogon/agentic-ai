"""
AWS Bedrock Helper Functions
Provides utilities for interacting with AWS Bedrock Claude models
"""

import json
from typing import List, Dict, Optional
import os


class BedrockHelper:
    """Helper class for AWS Bedrock integration"""

    def __init__(
        self,
        region_name: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None
    ):
        """
        Initialize Bedrock Helper

        Args:
            region_name: AWS region name
            aws_access_key_id: AWS access key (optional, uses env vars if not provided)
            aws_secret_access_key: AWS secret key (optional, uses env vars if not provided)
            aws_session_token: AWS session token (optional, for temporary credentials)
        """
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for AWS Bedrock. Install with: pip install boto3")

        # Initialize boto3 client
        session_params = {
            'region_name': region_name
        }

        if aws_access_key_id:
            session_params['aws_access_key_id'] = aws_access_key_id
        if aws_secret_access_key:
            session_params['aws_secret_access_key'] = aws_secret_access_key
        if aws_session_token:
            session_params['aws_session_token'] = aws_session_token

        self.bedrock_runtime = boto3.client('bedrock-runtime', **session_params)
        self.region_name = region_name

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """
        Call Claude via AWS Bedrock with chat messages

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_id: Bedrock model ID
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Returns:
            Response dictionary with success status and content
        """
        try:
            # Prepare messages for Claude format
            claude_messages = []
            for msg in messages:
                if msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # Build request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": claude_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt
            # Check if first message is system message
            elif messages and messages[0]["role"] == "system":
                request_body["system"] = messages[0]["content"]

            # Call Bedrock API
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())

            # Extract content
            content = ""
            if "content" in response_body and len(response_body["content"]) > 0:
                content = response_body["content"][0]["text"]

            return {
                "success": True,
                "content": content,
                "response": response_body,
                "model_id": model_id,
                "usage": response_body.get("usage", {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

    def text_completion(
        self,
        prompt: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict:
        """
        Call Claude via AWS Bedrock with a simple prompt

        Args:
            prompt: Input prompt
            model_id: Bedrock model ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary
        """
        # Convert to chat format
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            messages=messages,
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None
    ):
        """
        Stream chat completion from Claude via AWS Bedrock

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_id: Bedrock model ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Yields:
            Content chunks as they arrive
        """
        try:
            # Prepare messages
            claude_messages = []
            for msg in messages:
                if msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # Build request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": claude_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Add system prompt
            if system_prompt:
                request_body["system"] = system_prompt
            elif messages and messages[0]["role"] == "system":
                request_body["system"] = messages[0]["content"]

            # Call streaming API
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps(request_body)
            )

            # Stream response
            stream = response['body']
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_data = json.loads(chunk['bytes'].decode())

                    if chunk_data.get('type') == 'content_block_delta':
                        delta = chunk_data.get('delta', {})
                        if 'text' in delta:
                            yield delta['text']

        except Exception as e:
            yield f"Error: {str(e)}"

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available Claude models on Bedrock

        Returns:
            List of model information dicts
        """
        models = [
            {
                "model_id": "anthropic.claude-3-opus-20240229-v1:0",
                "name": "Claude 3 Opus",
                "description": "Most capable model, best for complex tasks",
                "max_tokens": 4096
            },
            {
                "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
                "name": "Claude 3 Sonnet",
                "description": "Balanced performance and speed",
                "max_tokens": 4096
            },
            {
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "name": "Claude 3 Haiku",
                "description": "Fastest model, good for simple tasks",
                "max_tokens": 4096
            },
            {
                "model_id": "anthropic.claude-v2:1",
                "name": "Claude 2.1",
                "description": "Previous generation, 200K context",
                "max_tokens": 4096
            },
            {
                "model_id": "anthropic.claude-v2",
                "name": "Claude 2.0",
                "description": "Previous generation",
                "max_tokens": 4096
            }
        ]

        return models

    def analyze_data(
        self,
        data_summary: str,
        question: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ) -> Dict:
        """
        Use Claude to analyze data and answer questions

        Args:
            data_summary: Summary or sample of the data
            question: Question to answer about the data
            model_id: Bedrock model ID

        Returns:
            Analysis response
        """
        system_prompt = """You are a data analyst assistant. Analyze the provided data
        and answer questions with clear insights, patterns, and recommendations.
        Provide actionable insights when possible."""

        messages = [
            {
                "role": "user",
                "content": f"""Here is a summary of the data:

{data_summary}

Question: {question}

Please provide a detailed analysis."""
            }
        ]

        return self.chat_completion(
            messages=messages,
            model_id=model_id,
            system_prompt=system_prompt
        )

    def generate_sql_explanation(
        self,
        sql_query: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ) -> Dict:
        """
        Generate explanation for SQL query

        Args:
            sql_query: SQL query to explain
            model_id: Bedrock model ID

        Returns:
            Explanation response
        """
        messages = [
            {
                "role": "user",
                "content": f"""Please explain this SQL query in simple terms:

```sql
{sql_query}
```

Provide:
1. What the query does
2. Key operations (joins, aggregations, etc.)
3. Expected output"""
            }
        ]

        return self.chat_completion(
            messages=messages,
            model_id=model_id
        )
