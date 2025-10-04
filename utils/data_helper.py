"""
Data Helper Functions
Provides utilities for data processing and visualization
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict


class DataHelper:
    @staticmethod
    def create_chart(
        df: pd.DataFrame,
        chart_type: str,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        title: Optional[str] = None
    ):
        """
        Create a Plotly chart from DataFrame

        Args:
            df: Input DataFrame
            chart_type: Type of chart (bar, line, pie, scatter, etc.)
            x_col: Column for x-axis
            y_col: Column for y-axis (can be list for multiple lines)
            title: Chart title

        Returns:
            Plotly figure object
        """
        if df.empty:
            return None

        # Auto-detect columns if not specified
        if not x_col and len(df.columns) > 0:
            x_col = df.columns[0]

        # For line and bar charts, if y_col not specified, use all numeric columns
        if not y_col and len(df.columns) > 1:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) > 0:
                # Exclude x_col from numeric columns if it's numeric
                if x_col in numeric_cols:
                    numeric_cols.remove(x_col)
                # Use first numeric column or all if multiple
                y_col = numeric_cols[0] if len(numeric_cols) == 1 else numeric_cols
            else:
                y_col = df.columns[1]

        chart_type = chart_type.lower()

        try:
            if chart_type == "bar":
                fig = px.bar(df, x=x_col, y=y_col, title=title)
            elif chart_type == "line":
                # Use graph_objects instead of px.line to avoid WebGL
                fig = go.Figure()

                if isinstance(y_col, list):
                    # Multiple lines
                    for col in y_col:
                        if col in df.columns:
                            fig.add_trace(go.Scatter(
                                x=df[x_col],
                                y=df[col],
                                mode='lines+markers',
                                name=str(col),
                                line=dict(width=2),
                                marker=dict(size=4)
                            ))
                else:
                    # Single line - ensure y_col exists
                    if y_col and y_col in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df[x_col],
                            y=df[y_col],
                            mode='lines+markers',
                            name=str(y_col),
                            line=dict(width=2),
                            marker=dict(size=4)
                        ))
                    else:
                        # Fallback: use first numeric column
                        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                        if x_col in numeric_cols:
                            numeric_cols.remove(x_col)
                        if len(numeric_cols) > 0:
                            y_col = numeric_cols[0]
                            fig.add_trace(go.Scatter(
                                x=df[x_col],
                                y=df[y_col],
                                mode='lines+markers',
                                name=str(y_col),
                                line=dict(width=2),
                                marker=dict(size=4)
                            ))

                # Configure layout for stable SVG rendering
                fig.update_layout(
                    title=title,
                    xaxis_title=str(x_col) if x_col else None,
                    yaxis_title=str(y_col) if not isinstance(y_col, list) else None,
                    hovermode='closest',
                    template='plotly',
                    autosize=True
                )
            elif chart_type == "pie":
                fig = px.pie(df, names=x_col, values=y_col, title=title)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=x_col, y=y_col, title=title)
            elif chart_type == "heatmap":
                # Use numeric columns for heatmap
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    fig = px.imshow(df[numeric_cols].corr(), title=title)
                else:
                    fig = px.bar(df, x=x_col, y=y_col, title=title)
            else:
                # Default to bar chart
                fig = px.bar(df, x=x_col, y=y_col, title=title)

            # Apply common stable rendering settings to all chart types
            if fig:
                fig.update_layout(
                    modebar_remove=['lasso2d', 'select2d'],
                    dragmode='pan'
                )

            return fig

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating {chart_type} chart: {e}")
            print(f"Traceback: {error_details}")
            print(f"DataFrame info - Shape: {df.shape}, Columns: {df.columns.tolist()}, x_col: {x_col}, y_col: {y_col}")

            # Fallback: try simple bar chart
            try:
                if not x_col:
                    x_col = df.columns[0]
                if not y_col:
                    y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
                print(f"Falling back to bar chart with x={x_col}, y={y_col}")
                return px.bar(df, x=x_col, y=y_col, title=title)
            except Exception as fallback_error:
                print(f"Fallback bar chart also failed: {fallback_error}")
                return None

    @staticmethod
    def auto_detect_chart_type(df: pd.DataFrame) -> str:
        """
        Automatically detect the best chart type for the data

        Args:
            df: Input DataFrame

        Returns:
            Recommended chart type
        """
        if df.empty:
            return "bar"

        # Count numeric vs categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # If mostly numeric, use line or scatter
        if len(numeric_cols) >= 2:
            return "scatter"

        # If one categorical and one numeric, use bar
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            return "bar"

        # If mostly categorical, use bar
        if len(categorical_cols) > 0:
            return "bar"

        # Default
        return "bar"

    @staticmethod
    def format_sql_code(sql: str) -> str:
        """
        Format SQL code for display

        Args:
            sql: SQL query string

        Returns:
            Formatted SQL string
        """
        # Basic SQL formatting
        keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "JOIN", "LEFT JOIN", "RIGHT JOIN"]

        formatted = sql
        for keyword in keywords:
            formatted = formatted.replace(f" {keyword} ", f"\n{keyword} ")
            formatted = formatted.replace(f" {keyword.lower()} ", f"\n{keyword} ")

        return formatted.strip()

    @staticmethod
    def summarize_dataframe(df: pd.DataFrame) -> Dict:
        """
        Create a summary of DataFrame statistics

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {"rows": 0, "columns": 0}

        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {},
            "null_counts": df.isnull().sum().to_dict()
        }
