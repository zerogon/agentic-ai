"""
LLM Helper Functions
Provides utilities for interacting with Databricks Model Serving endpoints and AWS Bedrock
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from typing import List, Dict, Optional, Union
from .bedrock_helper import BedrockHelper


class LLMHelper:
    def __init__(
        self,
        workspace_client: Optional[WorkspaceClient] = None,
        provider: str = "databricks",
        bedrock_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize LLM Helper - supports both Databricks and AWS Bedrock

        Args:
            workspace_client: Databricks WorkspaceClient instance (required for Databricks provider)
            provider: LLM provider - "databricks" or "bedrock"
            bedrock_region: AWS region for Bedrock (default: us-east-1)
            aws_access_key_id: AWS access key for Bedrock
            aws_secret_access_key: AWS secret key for Bedrock
        """
        self.provider = provider.lower()
        self.w = workspace_client
        self.bedrock = None

        if self.provider == "bedrock":
            self.bedrock = BedrockHelper(
                region_name=bedrock_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        elif self.provider == "databricks" and not workspace_client:
            raise ValueError("workspace_client is required for Databricks provider")

    def chat_completion(
        self,
        endpoint_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Call chat completion endpoint (works with both Databricks and Bedrock)

        Args:
            endpoint_name: Name of the serving endpoint (Databricks) or model ID (Bedrock)
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary
        """
        if self.provider == "bedrock":
            # Use Bedrock
            return self.bedrock.chat_completion(
                messages=messages,
                model_id=endpoint_name,
                temperature=temperature,
                max_tokens=max_tokens or 4096
            )
        else:
            # Use Databricks
            try:
                chat_messages = [
                    ChatMessage(
                        role=ChatMessageRole.SYSTEM if msg["role"] == "system" else ChatMessageRole.USER,
                        content=msg["content"]
                    )
                    for msg in messages
                ]

                response = self.w.serving_endpoints.query(
                    name=endpoint_name,
                    messages=chat_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return {
                    "success": True,
                    "response": response.as_dict(),
                    "content": self._extract_content(response.as_dict()),
                    "provider": "databricks"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "content": None,
                    "provider": "databricks"
                }

    def text_completion(
        self,
        endpoint_name: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Call text completion endpoint (works with both Databricks and Bedrock)

        Args:
            endpoint_name: Name of the serving endpoint (Databricks) or model ID (Bedrock)
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary
        """
        if self.provider == "bedrock":
            # Use Bedrock
            return self.bedrock.text_completion(
                prompt=prompt,
                model_id=endpoint_name,
                temperature=temperature,
                max_tokens=max_tokens or 4096
            )
        else:
            # Use Databricks
            try:
                response = self.w.serving_endpoints.query(
                    name=endpoint_name,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return {
                    "success": True,
                    "response": response.as_dict(),
                    "content": self._extract_content(response.as_dict()),
                    "provider": "databricks"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "content": None,
                    "provider": "databricks"
                }

    def get_embeddings(
        self,
        endpoint_name: str,
        text: str
    ) -> Dict:
        """
        Get embeddings for text (Databricks only)

        Args:
            endpoint_name: Name of the embedding endpoint
            text: Input text

        Returns:
            Response dictionary with embeddings
        """
        if self.provider == "bedrock":
            return {
                "success": False,
                "error": "Embeddings not supported via Bedrock helper. Use Databricks or direct Bedrock embedding models.",
                "embeddings": None
            }

        try:
            response = self.w.serving_endpoints.query(
                name=endpoint_name,
                input=text
            )

            return {
                "success": True,
                "embeddings": response.as_dict().get("data", [{}])[0].get("embedding"),
                "response": response.as_dict(),
                "provider": "databricks"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "embeddings": None,
                "provider": "databricks"
            }

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available models based on provider

        Returns:
            List of model information
        """
        if self.provider == "bedrock":
            return self.bedrock.get_available_models()
        else:
            return [
                {
                    "model_id": "custom-endpoint",
                    "name": "Databricks Serving Endpoint",
                    "description": "Custom model deployed on Databricks Model Serving"
                }
            ]

    def _extract_content(self, response: Dict) -> Optional[str]:
        """
        Extract text content from various response formats

        Args:
            response: API response dictionary

        Returns:
            Extracted text content
        """
        # Try different response formats
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice:
                return choice["message"].get("content")
            if "text" in choice:
                return choice["text"]

        if "predictions" in response and len(response["predictions"]) > 0:
            return response["predictions"][0]

        if "text" in response:
            return response["text"]

        return str(response)
