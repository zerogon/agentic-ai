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
        title: Optional[str] = None,
        dark_mode: bool = False
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
            elif chart_type == "map":
                # Map visualization with lat/lon coordinates
                lat_col, lon_col, color_col = DataHelper._detect_map_columns(df)

                if not lat_col or not lon_col:
                    error_msg = f"❌ 지도 생성 실패: 위도/경도 컬럼을 찾을 수 없습니다."
                    raise ValueError(error_msg)

                # Convert coordinates to numeric (handles string/object dtypes)
                df_map = df.copy()
                df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
                df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')

                # Remove rows with invalid coordinates
                df_map = df_map.dropna(subset=[lat_col, lon_col])

                if df_map.empty:
                    raise ValueError("❌ 유효한 좌표 데이터가 없습니다.")

                # Check if lat/lon are swapped (common issue)
                lat_min, lat_max = df_map[lat_col].min(), df_map[lat_col].max()
                lon_min, lon_max = df_map[lon_col].min(), df_map[lon_col].max()

                # If latitude values are in longitude range and vice versa, swap them
                lat_in_lon_range = (lat_min >= -180 and lat_max <= 180 and (lat_min < -90 or lat_max > 90))
                lon_in_lat_range = (lon_min >= -90 and lon_max <= 90)

                if lat_in_lon_range and lon_in_lat_range:
                    # Swap the columns silently
                    df_map[lat_col], df_map[lon_col] = df_map[lon_col].copy(), df_map[lat_col].copy()
                    lat_min, lat_max = df_map[lat_col].min(), df_map[lat_col].max()
                    lon_min, lon_max = df_map[lon_col].min(), df_map[lon_col].max()

                # Validate coordinate ranges
                if not DataHelper._validate_coordinates(df_map, lat_col, lon_col):
                    raise ValueError(f"❌ 좌표 범위가 올바르지 않습니다.")

                # Calculate center point
                center_lat = (df_map[lat_col].min() + df_map[lat_col].max()) / 2
                center_lon = (df_map[lon_col].min() + df_map[lon_col].max()) / 2

                # Calculate appropriate zoom level based on coordinate range
                lat_range = df_map[lat_col].max() - df_map[lat_col].min()
                lon_range = df_map[lon_col].max() - df_map[lon_col].min()
                max_range = max(lat_range, lon_range)

                # Zoom level heuristic
                if max_range > 10:
                    zoom = 4
                elif max_range > 5:
                    zoom = 5
                elif max_range > 2:
                    zoom = 6
                elif max_range > 1:
                    zoom = 7
                else:
                    zoom = 8

                # Try multiple map styles for best visual quality
                try:
                    # Create figure with size column if available
                    size_col = None
                    numeric_cols = df_map.select_dtypes(include=['number']).columns.tolist()
                    # Remove lat/lon from numeric columns
                    numeric_cols = [c for c in numeric_cols if c not in [lat_col, lon_col]]
                    if len(numeric_cols) > 0:
                        size_col = numeric_cols[0]  # Use first numeric column for size

                    if True:  # Always use scatter_geo for reliability
                        fig = px.scatter_geo(
                            df_map,
                            lat=lat_col,
                            lon=lon_col,
                            color=color_col if color_col else None,
                            size=size_col if size_col else None,
                            hover_name=color_col if color_col else None,
                            hover_data={col: True for col in df_map.columns if col not in [lat_col, lon_col]},
                            title=title if title else "📍 Geographic Distribution",
                            projection="natural earth",
                            color_continuous_scale="Plasma" if color_col and pd.api.types.is_numeric_dtype(df_map[color_col]) else None,
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )

                        # Calculate projection scale
                        projection_scale = 100 / max_range if max_range > 0 else 20

                        # Beautiful geo styling based on theme
                        if dark_mode:
                            # Elegant dark theme with gradient feel
                            fig.update_geos(
                                center=dict(lat=center_lat, lon=center_lon),
                                projection_scale=projection_scale,
                                visible=True,
                                resolution=110,  # Higher resolution for smoother borders
                                showcountries=True,
                                countrycolor="#3B4252",
                                countrywidth=1.5,
                                showcoastlines=True,
                                coastlinecolor="#4C566A",
                                coastlinewidth=1,
                                showland=True,
                                landcolor="#2E3440",
                                showocean=True,
                                oceancolor="#1a1f2e",
                                showlakes=True,
                                lakecolor="#1a1f2e",
                                showrivers=False,
                                bgcolor="#1a1f2e"
                            )
                        else:
                            # Clean, modern light theme
                            fig.update_geos(
                                center=dict(lat=center_lat, lon=center_lon),
                                projection_scale=projection_scale,
                                visible=True,
                                resolution=110,  # Higher resolution
                                showcountries=True,
                                countrycolor="#CBD5E1",
                                countrywidth=1.5,
                                showcoastlines=True,
                                coastlinecolor="#94A3B8",
                                coastlinewidth=1,
                                showland=True,
                                landcolor="#F1F5F9",
                                showocean=True,
                                oceancolor="#E0F2FE",
                                showlakes=True,
                                lakecolor="#BAE6FD",
                                showrivers=False,
                                bgcolor="#F8FAFC"
                            )

                        # Subtle marker styling
                        if size_col:
                            fig.update_traces(
                                marker=dict(
                                    sizemode='diameter',
                                    sizemin=4,
                                    sizeref=2. * df_map[size_col].max() / (20.**2),
                                    opacity=0.8,
                                    line=dict(width=1, color='rgba(255,255,255,0.5)')
                                )
                            )
                        else:
                            fig.update_traces(
                                marker=dict(
                                    size=8,
                                    opacity=0.8,
                                    line=dict(width=1, color='rgba(255,255,255,0.5)')
                                )
                            )

                    # Common layout styling with larger map size
                    if dark_mode:
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='#0F172A',
                            plot_bgcolor='#0F172A',
                            height=700,  # Increased from default
                            font=dict(family="Inter, sans-serif", size=12, color="#E2E8F0"),
                            title=dict(
                                font=dict(size=20, family="Inter, sans-serif", color="#F1F5F9", weight=600),
                                x=0.5,
                                xanchor='center'
                            ),
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=0.98,
                                xanchor="right",
                                x=0.98,
                                bgcolor="rgba(15,23,42,0.85)",
                                bordercolor="#475569",
                                borderwidth=1,
                                font=dict(color="#F1F5F9", size=11)
                            ),
                            hoverlabel=dict(
                                bgcolor="#1E293B",
                                font_size=12,
                                font_family="Inter, sans-serif",
                                font_color="#F1F5F9",
                                bordercolor="#475569"
                            ),
                            margin=dict(l=0, r=0, t=40, b=0)  # Minimize margins for larger map area
                        )
                    else:
                        fig.update_layout(
                            paper_bgcolor='#FFFFFF',
                            plot_bgcolor='#FFFFFF',
                            height=700,  # Increased from default
                            font=dict(family="Inter, sans-serif", size=12, color="#1F2937"),
                            title=dict(
                                font=dict(size=20, family="Inter, sans-serif", color="#111827", weight=600),
                                x=0.5,
                                xanchor='center'
                            ),
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=0.98,
                                xanchor="right",
                                x=0.98,
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor="#E5E7EB",
                                borderwidth=1,
                                font=dict(color="#1F2937", size=11)
                            ),
                            hoverlabel=dict(
                                bgcolor="#FFFFFF",
                                font_size=12,
                                font_family="Inter, sans-serif",
                                font_color="#1F2937",
                                bordercolor="#D1D5DB"
                            ),
                            margin=dict(l=0, r=0, t=40, b=0)  # Minimize margins for larger map area
                        )

                except Exception as map_error:
                    print(f"  ❌ All map creation methods failed: {map_error}")
                    import traceback
                    traceback.print_exc()
                    raise ValueError(f"Failed to create map visualization: {map_error}")
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

        # Debug logging
        print(f"🔍 Auto-detecting chart type for DataFrame:")
        print(f"  - Columns: {df.columns.tolist()}")
        print(f"  - Shape: {df.shape}")

        # Check for map data first (latitude/longitude columns)
        lat_col, lon_col, _ = DataHelper._detect_map_columns(df)
        print(f"  - Map column detection: lat={lat_col}, lon={lon_col}")

        if lat_col and lon_col:
            # Validate coordinates
            is_valid = DataHelper._validate_coordinates(df, lat_col, lon_col)
            print(f"  - Coordinate validation: {is_valid}")
            if is_valid:
                print(f"✅ Auto-detected chart type: MAP")
                return "map"

        # Count numeric vs categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # If mostly numeric, use line or scatter
        if len(numeric_cols) >= 2:
            print(f"✅ Auto-detected chart type: SCATTER (numeric columns: {len(numeric_cols)})")
            return "scatter"

        # If one categorical and one numeric, use bar
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            print(f"✅ Auto-detected chart type: BAR (categorical + numeric)")
            return "bar"

        # If mostly categorical, use bar
        if len(categorical_cols) > 0:
            print(f"✅ Auto-detected chart type: BAR (categorical only)")
            return "bar"

        # Default
        print(f"✅ Auto-detected chart type: BAR (default)")
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
    def _detect_map_columns(df: pd.DataFrame) -> tuple:
        """
        Auto-detect latitude, longitude, and category columns

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (lat_col, lon_col, color_col)
        """
        lat_col = None
        lon_col = None
        color_col = None

        # Detect latitude column (case-insensitive, including partial matches)
        lat_candidates = ['latitude', 'lat', '위도', 'y', 'wido']
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Check exact match or if candidate is in column name
            if col_lower in lat_candidates or any(cand in col_lower for cand in lat_candidates):
                lat_col = col
                break

        # Detect longitude column (case-insensitive, including partial matches)
        lon_candidates = ['longitude', 'lon', 'lng', '경도', 'x', 'gyeongdo']
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Check exact match or if candidate is in column name
            if col_lower in lon_candidates or any(cand in col_lower for cand in lon_candidates):
                lon_col = col
                break

        # Detect category/color column (case-insensitive, including partial matches)
        category_candidates = ['category', 'type', 'group', 'class', '카테고리', '유형', 'region', 'area', '지역']
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Check exact match or if candidate is in column name
            if col_lower in category_candidates or any(cand in col_lower for cand in category_candidates):
                color_col = col
                break

        # If no explicit category column, use first categorical column
        if not color_col:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            # Exclude lat/lon columns
            categorical_cols = [c for c in categorical_cols if c not in [lat_col, lon_col]]
            if len(categorical_cols) > 0:
                color_col = categorical_cols[0]

        return lat_col, lon_col, color_col

    @staticmethod
    def _validate_coordinates(df: pd.DataFrame, lat_col: str, lon_col: str) -> bool:
        """
        Validate latitude and longitude values

        Args:
            df: Input DataFrame
            lat_col: Latitude column name
            lon_col: Longitude column name

        Returns:
            True if coordinates are valid
        """
        try:
            print(f"  🔍 Validating coordinates:")

            # Check if columns exist
            if lat_col not in df.columns or lon_col not in df.columns:
                print(f"    ❌ Columns missing: lat_col={lat_col in df.columns}, lon_col={lon_col in df.columns}")
                return False

            # Show sample data
            print(f"    - Sample {lat_col}: {df[lat_col].head(3).tolist()}")
            print(f"    - Sample {lon_col}: {df[lon_col].head(3).tolist()}")
            print(f"    - {lat_col} dtype: {df[lat_col].dtype}")
            print(f"    - {lon_col} dtype: {df[lon_col].dtype}")

            # Try to convert to numeric if needed
            lat_series = pd.to_numeric(df[lat_col], errors='coerce')
            lon_series = pd.to_numeric(df[lon_col], errors='coerce')

            print(f"    - {lat_col} numeric dtype: {lat_series.dtype}")
            print(f"    - {lon_col} numeric dtype: {lon_series.dtype}")

            # Check for NaN values after conversion
            lat_nan_count = lat_series.isna().sum()
            lon_nan_count = lon_series.isna().sum()
            print(f"    - {lat_col} NaN count: {lat_nan_count}/{len(df)}")
            print(f"    - {lon_col} NaN count: {lon_nan_count}/{len(df)}")

            if lat_nan_count > 0 or lon_nan_count > 0:
                print(f"    ❌ Contains NaN values after conversion")
                return False

            # Check latitude range (-90 to 90)
            lat_min, lat_max = lat_series.min(), lat_series.max()
            print(f"    - {lat_col} range: {lat_min} to {lat_max}")
            if lat_min < -90 or lat_max > 90:
                print(f"    ❌ Latitude out of range (-90 to 90)")
                return False

            # Check longitude range (-180 to 180)
            lon_min, lon_max = lon_series.min(), lon_series.max()
            print(f"    - {lon_col} range: {lon_min} to {lon_max}")
            if lon_min < -180 or lon_max > 180:
                print(f"    ❌ Longitude out of range (-180 to 180)")
                return False

            print(f"    ✅ Coordinates are valid!")
            return True

        except Exception as e:
            print(f"    ❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            return False

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
