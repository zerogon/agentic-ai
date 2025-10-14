"""
Data Agent - Dataset Metadata Collection and Analysis
Collects metadata from Databricks tables via Genie API
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from databricks.sdk import WorkspaceClient
from utils.genie_helper import GenieHelper


class DataAgent:
    """
    Data Agent for collecting and analyzing dataset metadata

    Collects:
    - Table/column information
    - Row counts
    - Last updated timestamps
    - Data quality metrics
    """

    def __init__(self, workspace_client: WorkspaceClient):
        """
        Initialize Data Agent

        Args:
            workspace_client: Databricks WorkspaceClient instance
        """
        self.w = workspace_client

    def collect_metadata(self, space_id: str, table_names: List[str]) -> Dict:
        """
        Collect metadata for specified tables using Genie

        Args:
            space_id: Genie Space ID
            table_names: List of table names to query

        Returns:
            Dict mapping table names to metadata:
            {
                "table_name": {
                    "columns": ["col1", "col2"],
                    "rows": 100,
                    "last_updated": "2025-10-12T14:00:00Z",
                    "exists": True
                }
            }
        """
        metadata = {}
        genie = GenieHelper(self.w, space_id)

        for table_name in table_names:
            try:
                # Query table metadata using Genie
                table_meta = self._query_table_metadata(genie, table_name)
                metadata[table_name] = table_meta
            except Exception as e:
                # Mark table as non-existent or error
                metadata[table_name] = {
                    "columns": [],
                    "rows": 0,
                    "last_updated": None,
                    "exists": False,
                    "error": str(e)
                }

        return metadata

    def _query_table_metadata(self, genie: GenieHelper, table_name: str) -> Dict:
        """
        Query metadata for a single table

        Args:
            genie: GenieHelper instance
            table_name: Name of table to query

        Returns:
            Dict with table metadata
        """
        # Construct metadata query
        metadata_query = f"""
        DESCRIBE TABLE {table_name}
        """

        # Execute query via Genie
        result = genie.start_conversation(metadata_query)

        if not result["success"]:
            return {
                "columns": [],
                "rows": 0,
                "last_updated": None,
                "exists": False,
                "error": result.get("error", "Unknown error")
            }

        # Process response to extract column information
        messages = genie.process_response(result["response"])

        columns = []
        for msg in messages:
            if msg.get("type") == "query" and not msg["data"].empty:
                # Extract column names from DESCRIBE result
                df = msg["data"]
                if "col_name" in df.columns:
                    columns = df["col_name"].tolist()

        # Query row count
        row_count = self._query_row_count(genie, table_name)

        # Query last updated timestamp (if available)
        last_updated = self._query_last_updated(genie, table_name)

        return {
            "columns": columns,
            "rows": row_count,
            "last_updated": last_updated,
            "exists": len(columns) > 0
        }

    def _query_row_count(self, genie: GenieHelper, table_name: str) -> int:
        """
        Query row count for table

        Args:
            genie: GenieHelper instance
            table_name: Table name

        Returns:
            Row count (0 if error)
        """
        try:
            count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
            result = genie.start_conversation(count_query)

            if result["success"]:
                messages = genie.process_response(result["response"])
                for msg in messages:
                    if msg.get("type") == "query" and not msg["data"].empty:
                        df = msg["data"]
                        if "row_count" in df.columns:
                            return int(df["row_count"].iloc[0])

            return 0
        except Exception:
            return 0

    def _query_last_updated(self, genie: GenieHelper, table_name: str) -> Optional[str]:
        """
        Query last updated timestamp for table

        Args:
            genie: GenieHelper instance
            table_name: Table name

        Returns:
            ISO format timestamp string or None
        """
        try:
            # Try to get table properties
            properties_query = f"SHOW TBLPROPERTIES {table_name}"
            result = genie.start_conversation(properties_query)

            if result["success"]:
                messages = genie.process_response(result["response"])
                for msg in messages:
                    if msg.get("type") == "query" and not msg["data"].empty:
                        df = msg["data"]
                        # Look for transient_lastDdlTime or similar
                        if "key" in df.columns and "value" in df.columns:
                            for _, row in df.iterrows():
                                if "lastDdlTime" in str(row["key"]).lower():
                                    # Convert timestamp to ISO format
                                    timestamp = int(row["value"])
                                    dt = datetime.fromtimestamp(timestamp)
                                    return dt.isoformat() + "Z"

            # Fallback: return current timestamp
            return datetime.now().isoformat() + "Z"
        except Exception:
            return datetime.now().isoformat() + "Z"

    def collect_metadata_from_genie_spaces(
        self,
        genie_domains: List[str],
        table_names: List[str],
        space_id_getter
    ) -> Dict:
        """
        Collect metadata from multiple Genie spaces

        Args:
            genie_domains: List of Genie domain names (e.g., ["SALES_GENIE", "CONTRACT_GENIE"])
            table_names: List of table names to query
            space_id_getter: Function to get space ID from domain name

        Returns:
            Combined metadata dict
        """
        combined_metadata = {}

        for domain in genie_domains:
            try:
                space_id = space_id_getter(domain)
                domain_metadata = self.collect_metadata(space_id, table_names)

                # Merge with combined metadata
                for table_name, meta in domain_metadata.items():
                    if table_name not in combined_metadata:
                        combined_metadata[table_name] = meta
                    else:
                        # Merge metadata (prefer existing if already valid)
                        if not combined_metadata[table_name].get("exists"):
                            combined_metadata[table_name] = meta

            except Exception as e:
                # Log error but continue with other domains
                print(f"Error collecting metadata from {domain}: {str(e)}")

        return combined_metadata

    def analyze_data_quality(self, metadata: Dict) -> Dict:
        """
        Analyze data quality metrics from metadata

        Args:
            metadata: Dataset metadata dict

        Returns:
            Dict with quality analysis:
            {
                "total_tables": int,
                "valid_tables": int,
                "total_rows": int,
                "average_rows_per_table": float,
                "tables_with_data": int,
                "empty_tables": int,
                "freshness_ok": bool
            }
        """
        total_tables = len(metadata)
        valid_tables = sum(1 for meta in metadata.values() if meta.get("exists"))
        total_rows = sum(meta.get("rows", 0) for meta in metadata.values())
        tables_with_data = sum(1 for meta in metadata.values() if meta.get("rows", 0) > 0)
        empty_tables = valid_tables - tables_with_data

        average_rows = total_rows / valid_tables if valid_tables > 0 else 0

        # Check freshness (within 30 days)
        now = datetime.now()
        freshness_ok = True
        for meta in metadata.values():
            if meta.get("last_updated"):
                try:
                    last_updated = datetime.fromisoformat(meta["last_updated"].replace('Z', '+00:00'))
                    days_old = (now - last_updated).days
                    if days_old > 30:
                        freshness_ok = False
                        break
                except Exception:
                    pass

        return {
            "total_tables": total_tables,
            "valid_tables": valid_tables,
            "total_rows": total_rows,
            "average_rows_per_table": round(average_rows, 2),
            "tables_with_data": tables_with_data,
            "empty_tables": empty_tables,
            "freshness_ok": freshness_ok
        }
