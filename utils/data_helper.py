"""
Data Helper Functions
Provides utilities for data processing and visualization
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Tuple
import folium
from utils.map_helper import MapHelper


class DataHelper:
    @staticmethod
    def _smart_sort_dataframe(df: pd.DataFrame, sort_column: str) -> pd.DataFrame:
        """
        Smart sort DataFrame by detecting column type and sorting appropriately
        Handles numeric strings, dates, and regular strings

        Args:
            df: Input DataFrame
            sort_column: Column name to sort by

        Returns:
            Sorted DataFrame
        """
        if sort_column not in df.columns:
            return df

        df_copy = df.copy()

        # Try numeric conversion first (handles "1", "2", "10" correctly)
        try:
            numeric_values = pd.to_numeric(df_copy[sort_column], errors='coerce')
            # Check if at least some values were successfully converted
            if not numeric_values.isna().all() and numeric_values.notna().sum() > 0:
                # Create temporary sort key
                df_copy['_sort_key'] = numeric_values
                # Sort by numeric values, putting NaN at the end
                df_sorted = df_copy.sort_values('_sort_key', na_position='last').drop('_sort_key', axis=1)
                return df_sorted
        except Exception:
            pass

        # Try datetime conversion (handles dates/times)
        try:
            datetime_values = pd.to_datetime(df_copy[sort_column], errors='coerce')
            # Check if at least some values were successfully converted
            if not datetime_values.isna().all() and datetime_values.notna().sum() > 0:
                df_copy['_sort_key'] = datetime_values
                df_sorted = df_copy.sort_values('_sort_key', na_position='last').drop('_sort_key', axis=1)
                return df_sorted
        except Exception:
            pass

        # Fallback to string sorting
        return df_copy.sort_values(sort_column)

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
                # Smart sort DataFrame by x-axis column (handles numeric strings, dates, etc.)
                df_sorted = DataHelper._smart_sort_dataframe(df, x_col)

                # Use graph_objects instead of px.line to avoid WebGL
                fig = go.Figure()

                if isinstance(y_col, list):
                    # Multiple lines
                    for col in y_col:
                        if col in df_sorted.columns:
                            fig.add_trace(go.Scatter(
                                x=df_sorted[x_col],
                                y=df_sorted[col],
                                mode='lines+markers',
                                name=str(col),
                                line=dict(width=2),
                                marker=dict(size=4)
                            ))
                else:
                    # Single line - ensure y_col exists
                    if y_col and y_col in df_sorted.columns:
                        fig.add_trace(go.Scatter(
                            x=df_sorted[x_col],
                            y=df_sorted[y_col],
                            mode='lines+markers',
                            name=str(y_col),
                            line=dict(width=2),
                            marker=dict(size=4)
                        ))
                    else:
                        # Fallback: use first numeric column
                        numeric_cols = df_sorted.select_dtypes(include=['number']).columns.tolist()
                        if x_col in numeric_cols:
                            numeric_cols.remove(x_col)
                        if len(numeric_cols) > 0:
                            y_col = numeric_cols[0]
                            fig.add_trace(go.Scatter(
                                x=df_sorted[x_col],
                                y=df_sorted[y_col],
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

                # Configure X-axis: sort categories if categorical
                if df_sorted[x_col].dtype == 'object' or df_sorted[x_col].dtype.name == 'category':
                    fig.update_xaxes(categoryorder='array', categoryarray=df_sorted[x_col].unique())

                # Configure Y-axis: ensure it's treated as numeric/continuous
                fig.update_yaxes(
                    type='linear',  # Force linear numeric scale
                    autorange=True,  # Auto-scale based on data
                    rangemode='tozero'  # Start from zero if appropriate
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

        # Check for map data first (latitude/longitude columns)
        lat_col, lon_col, _ = DataHelper._detect_map_columns(df)


        if lat_col and lon_col:
            # Validate coordinates
            is_valid = DataHelper._validate_coordinates(df, lat_col, lon_col)
            if is_valid:
                return "map"

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

        # Normalize column name for matching (remove spaces, special chars, lowercase)
        def normalize_col_name(col_name):
            import re
            normalized = str(col_name).lower().strip()
            # Remove special characters and spaces
            normalized = re.sub(r'[^a-z0-9가-힣]', '', normalized)
            return normalized

        # Detect latitude column (case-insensitive, including partial matches)
        # First, try exact matches for better accuracy
        lat_candidates_exact = ['latitude', 'lat', '위도', 'wido']
        lat_candidates_partial = ['y', '위', 'gislatitude', 'gislat', 'coord_lat']

        # Try exact matches first
        for col in df.columns:
            col_normalized = normalize_col_name(col)
            for cand in lat_candidates_exact:
                if col_normalized == cand or cand == col_normalized:
                    # Validate that column contains reasonable latitude values
                    try:
                        numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(numeric_vals) > 0:
                            min_val, max_val = numeric_vals.min(), numeric_vals.max()
                            # Check if values are in valid latitude range
                            if -90 <= min_val <= 90 and -90 <= max_val <= 90:
                                lat_col = col
                                break
                    except:
                        pass
            if lat_col:
                break

        # If no exact match, try partial matches
        if not lat_col:
            for col in df.columns:
                col_normalized = normalize_col_name(col)
                for cand in lat_candidates_partial:
                    if cand in col_normalized:
                        # Validate that column contains reasonable latitude values
                        try:
                            numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(numeric_vals) > 0:
                                min_val, max_val = numeric_vals.min(), numeric_vals.max()
                                # Check if values are in valid latitude range
                                if -90 <= min_val <= 90 and -90 <= max_val <= 90:
                                    lat_col = col
                                    break
                        except:
                            pass
                if lat_col:
                    break

        # Detect longitude column (case-insensitive, including partial matches)
        lon_candidates_exact = ['longitude', 'lon', 'lng', '경도', 'gyeongdo']
        lon_candidates_partial = ['x', '경', 'gislongitude', 'gislon', 'coord_lon', 'coord_lng']

        # Try exact matches first
        for col in df.columns:
            col_normalized = normalize_col_name(col)
            # Skip if this is the latitude column
            if col == lat_col:
                continue
            for cand in lon_candidates_exact:
                if col_normalized == cand or cand == col_normalized:
                    # Validate that column contains reasonable longitude values
                    try:
                        numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(numeric_vals) > 0:
                            min_val, max_val = numeric_vals.min(), numeric_vals.max()
                            # Check if values are in valid longitude range
                            if -180 <= min_val <= 180 and -180 <= max_val <= 180:
                                lon_col = col
                                print(f"  🎯 Detected longitude column: '{col}' (exact match: '{cand}', range: {min_val:.2f} to {max_val:.2f})")
                                break
                    except:
                        pass
            if lon_col:
                break

        # If no exact match, try partial matches
        if not lon_col:
            for col in df.columns:
                col_normalized = normalize_col_name(col)
                # Skip if this is the latitude column
                if col == lat_col:
                    continue
                for cand in lon_candidates_partial:
                    if cand in col_normalized:
                        # Validate that column contains reasonable longitude values
                        try:
                            numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(numeric_vals) > 0:
                                min_val, max_val = numeric_vals.min(), numeric_vals.max()
                                # Check if values are in valid longitude range
                                if -180 <= min_val <= 180 and -180 <= max_val <= 180:
                                    lon_col = col
                                    print(f"  🎯 Detected longitude column: '{col}' (partial match: '{cand}', range: {min_val:.2f} to {max_val:.2f})")
                                    break
                        except:
                            pass
                if lon_col:
                    break

        # Detect category/color column (case-insensitive, including partial matches)
        category_candidates = [
            'category', 'type', 'group', 'class', '카테고리', '유형',
            'region', 'area', '지역', 'name', 'label', '이름', '명'
        ]
        for col in df.columns:
            col_normalized = normalize_col_name(col)
            # Check exact match or if candidate is in column name
            for cand in category_candidates:
                if cand in col_normalized or col_normalized in cand:
                    color_col = col
                    print(f"  🎯 Detected category column: '{col}' (matched: '{cand}')")
                    break
            if color_col:
                break

        # If no explicit category column, use first categorical column
        if not color_col:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            # Exclude lat/lon columns
            categorical_cols = [c for c in categorical_cols if c not in [lat_col, lon_col]]
            if len(categorical_cols) > 0:
                color_col = categorical_cols[0]
                print(f"  🎯 Using first categorical column as color: '{color_col}'")

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
                print(f"    📋 Available columns: {df.columns.tolist()}")
                return False

            # Try to convert to numeric if needed
            lat_series = pd.to_numeric(df[lat_col], errors='coerce')
            lon_series = pd.to_numeric(df[lon_col], errors='coerce')


            # Check for NaN values after conversion
            lat_nan_count = lat_series.isna().sum()
            lon_nan_count = lon_series.isna().sum()
            total_rows = len(df)
  
            # Allow up to 10% NaN values (some data might have missing coordinates)
            if lat_nan_count > total_rows * 0.1 or lon_nan_count > total_rows * 0.1:
                print(f"    ❌ Too many NaN values after conversion (>10%)")
                if lat_nan_count > 0:
                    print(f"    📋 First NaN {lat_col} values: {df[lat_col][lat_series.isna()].head(3).tolist()}")
                if lon_nan_count > 0:
                    print(f"    📋 First NaN {lon_col} values: {df[lon_col][lon_series.isna()].head(3).tolist()}")
                return False

            # Get valid (non-NaN) coordinates for range checking
            valid_lat = lat_series.dropna()
            valid_lon = lon_series.dropna()

            if len(valid_lat) == 0 or len(valid_lon) == 0:
                print(f"    ❌ No valid coordinates after dropping NaN values")
                return False

            # Check latitude range (-90 to 90)
            lat_min, lat_max = valid_lat.min(), valid_lat.max()
            print(f"    - {lat_col} range: {lat_min:.6f} to {lat_max:.6f}")
            if lat_min < -90 or lat_max > 90:
                print(f"    ❌ Latitude out of range (-90 to 90)")
                print(f"    💡 Hint: Check if latitude/longitude columns are swapped")
                return False

            # Check longitude range (-180 to 180)
            lon_min, lon_max = valid_lon.min(), valid_lon.max()
            print(f"    - {lon_col} range: {lon_min:.6f} to {lon_max:.6f}")
            if lon_min < -180 or lon_max > 180:
                print(f"    ❌ Longitude out of range (-180 to 180)")
                print(f"    💡 Hint: Check if latitude/longitude columns are swapped")
                return False

            # Additional validation: Check if coordinates are all zeros (common error)
            if lat_min == lat_max == 0 and lon_min == lon_max == 0:
                print(f"    ⚠️ Warning: All coordinates are (0, 0) - likely invalid data")
                return False

            print(f"    ✅ Coordinates are valid! ({len(valid_lat)} valid points)")
            return True

        except Exception as e:
            print(f"    ❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def create_folium_map(
        df: pd.DataFrame,
        map_type: str = "auto"
    ) -> Optional[folium.Map]:
        """
        Create an interactive Folium map from geographic data.

        Args:
            df: DataFrame with geographic data (lat/lon columns)
            map_type: Type of map ('auto', 'point', 'heatmap')

        Returns:
            Folium Map object or None if mapping not possible
        """
        map_helper = MapHelper()

        # Check if we can create a map
        can_map, reason = map_helper.can_create_map(df)
        if not can_map:
            print(f"❌ Cannot create map: {reason}")
            return None

        # Auto-create map based on data
        folium_map = map_helper.auto_create_map(df, map_type=map_type)

        return folium_map

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

