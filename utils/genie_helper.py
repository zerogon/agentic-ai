"""
Genie API Helper Functions
Provides utilities for interacting with Databricks Genie API
"""

import pandas as pd
from databricks.sdk import WorkspaceClient
from typing import Dict, List, Optional


class GenieHelper:
    def __init__(self, workspace_client: WorkspaceClient, genie_space_id: str):
        """
        Initialize Genie Helper

        Args:
            workspace_client: Databricks WorkspaceClient instance
            genie_space_id: ID of the Genie Space to use
        """
        self.w = workspace_client
        self.genie_space_id = genie_space_id

    def start_conversation(self, prompt: str) -> Dict:
        """
        Start a new conversation with Genie

        Args:
            prompt: User's question/prompt

        Returns:
            Conversation response object
        """
        try:
            conversation = self.w.genie.start_conversation_and_wait(
                self.genie_space_id,
                prompt
            )
            return {
                "conversation_id": conversation.conversation_id,
                "response": conversation,
                "success": True
            }
        except Exception as e:
            return {
                "conversation_id": None,
                "response": None,
                "success": False,
                "error": str(e)
            }

    def continue_conversation(self, conversation_id: str, prompt: str) -> Dict:
        """
        Continue an existing conversation with Genie

        Args:
            conversation_id: ID of the existing conversation
            prompt: Follow-up question/prompt

        Returns:
            Conversation response object
        """
        try:
            conversation = self.w.genie.create_message_and_wait(
                self.genie_space_id,
                conversation_id,
                prompt
            )
            return {
                "conversation_id": conversation_id,
                "response": conversation,
                "success": True
            }
        except Exception as e:
            return {
                "conversation_id": conversation_id,
                "response": None,
                "success": False,
                "error": str(e)
            }

    def get_query_result(self, statement_id: str) -> pd.DataFrame:
        """
        Get query result as DataFrame

        Args:
            statement_id: SQL statement ID from Genie response

        Returns:
            Pandas DataFrame with query results
        """
        try:
            result = self.w.statement_execution.get_statement(statement_id)
            if result.result and result.result.data_array:
                columns = [col.name for col in result.manifest.schema.columns]
                return pd.DataFrame(result.result.data_array, columns=columns)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting query result: {e}")
            return pd.DataFrame()

    def process_response(self, response) -> List[Dict]:
        """
        Process Genie response and extract text, data, and code

        Args:
            response: Genie conversation response object

        Returns:
            List of message dictionaries with content, data, and code
        """
        messages = []

        if not response or not hasattr(response, 'attachments'):
            return messages

        for attachment in response.attachments:
            message = {"role": "assistant"}

            if attachment.text:
                message["content"] = attachment.text.content
                message["type"] = "text"
                messages.append(message)

            elif attachment.query:
                # Get query results
                data = self.get_query_result(response.query_result.statement_id)

                message["content"] = attachment.query.description or "Query executed successfully"
                message["data"] = data
                message["code"] = attachment.query.query
                message["type"] = "query"
                messages.append(message)

        return messages
