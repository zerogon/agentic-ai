"""
Map Helper for Geospatial Visualization

Provides utilities for working with geospatial data and creating interactive maps.
"""

import pandas as pd
import plotly.express as px
from typing import Optional, Dict, Any, List, Tuple, Union
import json
from shapely import wkt
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
import geopandas as gpd
from utils.seoul_boundary import detect_seoul_data, get_seoul_boundary


class MapHelper:
    """Helper class for geospatial data visualization."""

    # Predefined color schemes for choropleth maps
    COLOR_SCHEMES = {
        "blue": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
        "green": ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"],
        "red": ["#fff5f0", "#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#a50f15", "#67000d"],
        "orange": ["#fff5eb", "#fee6ce", "#fdd0a2", "#fdae6b", "#fd8d3c", "#f16913", "#d94801", "#a63603", "#7f2704"],
        "purple": ["#fcfbfd", "#efedf5", "#dadaeb", "#bcbddc", "#9e9ac8", "#807dba", "#6a51a3", "#54278f", "#3f007d"]
    }

    # Category colors - vibrant and distinct colors for categorical data
    CATEGORY_COLORS = [
        '#e41a1c',  # Red
        '#377eb8',  # Blue
        '#4daf4a',  # Green
        '#984ea3',  # Purple
        '#ff7f00',  # Orange
        '#ffff33',  # Yellow
        '#a65628',  # Brown
        '#f781bf',  # Pink
        '#999999',  # Gray
        '#66c2a5',  # Teal
        '#fc8d62',  # Coral
        '#8da0cb',  # Lavender
        '#e78ac3',  # Rose
        '#a6d854',  # Lime
        '#ffd92f',  # Gold
        '#e5c494',  # Tan
        '#b3b3b3',  # Silver
    ]

    # Rank-based color mapping for polygon maps
    RANK_COLOR_MAP = {
        "max": "#296ed4",     # Darkest blue
        "up": "#d3e7f4",      # Medium blue
        "min": "#f06305",     # Darkest red
        "down": "#f7dfd2",    # Medium red
        "default": "#cccccc"  # Gray for unrecognized values
    }

    def __init__(self):
        """Initialize the MapHelper."""
        pass

    @staticmethod
    def calculate_auto_zoom(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> int:
        """
        Calculate appropriate zoom level based on coordinate bounds.

        Args:
            lat_min: Minimum latitude
            lat_max: Maximum latitude
            lon_min: Minimum longitude
            lon_max: Maximum longitude

        Returns:
            Appropriate zoom level (0-20)
        """
        # Calculate the span of coordinates
        lat_span = abs(lat_max - lat_min)
        lon_span = abs(lon_max - lon_min)

        # Use the larger span to determine zoom
        max_span = max(lat_span, lon_span)

        # Zoom level mapping based on coordinate span
        # These values are empirically determined for good fit
        if max_span >= 10:  # Country/region level
            return 5
        elif max_span >= 5:  # Large area
            return 6
        elif max_span >= 2:  # Medium area
            return 7
        elif max_span >= 1:  # City level
            return 8
        elif max_span >= 0.5:  # District level
            return 9
        elif max_span >= 0.2:  # Neighborhood level
            return 10
        elif max_span >= 0.1:  # Local area
            return 11
        elif max_span >= 0.05:  # Small area
            return 12
        elif max_span >= 0.02:  # Very small area
            return 13
        elif max_span >= 0.01:  # Street level
            return 14
        else:  # Building level
            return 15

    @staticmethod
    def parse_geometry(geometry_data: Union[str, dict]) -> Optional[Union[Polygon, MultiPolygon]]:
        """
        Parse geometry data from various formats (WKT, GeoJSON).

        Args:
            geometry_data: Geometry data as WKT string or GeoJSON dict

        Returns:
            Shapely Polygon or MultiPolygon object, or None if parsing fails
        """
        try:
            # Case 1: WKT format (string starting with POLYGON/MULTIPOLYGON)
            if isinstance(geometry_data, str):
                geometry_data = geometry_data.strip()

                if geometry_data.upper().startswith(('POLYGON', 'MULTIPOLYGON', 'POINT', 'LINESTRING')):
                    geom = wkt.loads(geometry_data)
                    return geom

                # Try to parse as JSON string
                try:
                    geometry_data = json.loads(geometry_data)
                except json.JSONDecodeError:
                    print(f"  ❌ Invalid geometry string: {geometry_data[:100]}...")
                    return None

            # Case 2: GeoJSON format (dict)
            if isinstance(geometry_data, dict):
                geom = shape(geometry_data)
                print(f"  ✅ Parsed GeoJSON geometry: {geom.geom_type}")
                return geom

            print(f"  ❌ Unknown geometry format: {type(geometry_data)}")
            return None

        except Exception as e:
            print(f"  ❌ Geometry parsing error: {e}")
            return None

    def has_valid_geometry(self, df: pd.DataFrame, geometry_col: str) -> bool:
        """
        Check if DataFrame has valid polygon geometry data.

        Args:
            df: Input DataFrame
            geometry_col: Name of geometry column

        Returns:
            True if valid polygon geometry exists
        """
        if geometry_col not in df.columns:
            return False

        # Sample first non-null value
        sample_data = df[geometry_col].dropna().iloc[0] if not df[geometry_col].dropna().empty else None

        if sample_data is None:
            return False

        # Try to parse sample
        geom = self.parse_geometry(sample_data)

        if geom is None:
            return False

        # Check if it's a polygon type
        return geom.geom_type in ['Polygon', 'MultiPolygon']

    def detect_geo_columns(self, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """
        Detect potential geographic columns in a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with detected column types: {
                'latitude': column_name or None,
                'longitude': column_name or None,
                'location': column_name or None,
                'geometry': column_name or None
            }
        """
        result = {
            'latitude': None,
            'longitude': None,
            'location': None,
            'geometry': None
        }

        # Exact match keywords (prioritized)
        lat_keywords_exact = ['lat', 'latitude', '위도']
        lon_keywords_exact = ['lon', 'lng', 'longitude', '경도']
        # Partial match keywords (fallback)
        lat_keywords_partial = ['y', 'y_coord', 'northing']
        lon_keywords_partial = ['x', 'x_coord', 'easting']
        # Location/address columns
        loc_keywords = ['location', 'address', 'place', 'city', 'region', 'country', 'area', 'district']
        # Geometry columns
        geo_keywords = ['geometry', 'geom', 'shape', 'wkt', 'wkb']

        # Try exact matches first for latitude
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword == col_lower for keyword in lat_keywords_exact):
                # Validate latitude range
                try:
                    numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_vals) > 0:
                        min_val, max_val = numeric_vals.min(), numeric_vals.max()
                        if -90 <= min_val <= 90 and -90 <= max_val <= 90:
                            result['latitude'] = col
                            break
                except:
                    pass

        # If no exact match, try partial matches for latitude
        if not result['latitude']:
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in lat_keywords_partial):
                    # Validate latitude range
                    try:
                        numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(numeric_vals) > 0:
                            min_val, max_val = numeric_vals.min(), numeric_vals.max()
                            if -90 <= min_val <= 90 and -90 <= max_val <= 90:
                                result['latitude'] = col
                                break
                    except:
                        pass

        # Try exact matches first for longitude
        for col in df.columns:
            col_lower = col.lower()
            if col == result['latitude']:  # Skip latitude column
                continue
            if any(keyword == col_lower for keyword in lon_keywords_exact):
                # Validate longitude range
                try:
                    numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_vals) > 0:
                        min_val, max_val = numeric_vals.min(), numeric_vals.max()
                        if -180 <= min_val <= 180 and -180 <= max_val <= 180:
                            result['longitude'] = col
                            break
                except:
                    pass

        # If no exact match, try partial matches for longitude
        if not result['longitude']:
            for col in df.columns:
                col_lower = col.lower()
                if col == result['latitude']:  # Skip latitude column
                    continue
                if any(keyword in col_lower for keyword in lon_keywords_partial):
                    # Validate longitude range
                    try:
                        numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(numeric_vals) > 0:
                            min_val, max_val = numeric_vals.min(), numeric_vals.max()
                            if -180 <= min_val <= 180 and -180 <= max_val <= 180:
                                result['longitude'] = col
                                break
                    except:
                        pass

        # Check for location
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in loc_keywords):
                result['location'] = col
                break

        # Check for geometry
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in geo_keywords):
                result['geometry'] = col
                break

        return result

    def can_create_map(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if the DataFrame contains sufficient geographic data for mapping.

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (can_map: bool, reason: str)
        """
        if df is None or df.empty:
            return False, "DataFrame is empty"

        geo_cols = self.detect_geo_columns(df)

        # Check for lat/lon pair
        if geo_cols['latitude'] and geo_cols['longitude']:
            return True, "point"

        # Check for geometry column
        if geo_cols['geometry']:
            return True, "geometry"

        # Check for location column
        if geo_cols['location']:
            return True, "location"

        return False, "No geographic columns detected"

    def create_point_map(
        self,
        df: pd.DataFrame,
        lat_col: str,
        lon_col: str,
        popup_cols: Optional[List[str]] = None,
        color_col: Optional[str] = None,
        size_col: Optional[str] = None,
        zoom_start: int = 10,
        mapbox_style: str = "carto-positron"
    ):
        """
        Create an interactive point map from latitude/longitude data using Plotly.

        Args:
            df: DataFrame with geographic data
            lat_col: Name of latitude column
            lon_col: Name of longitude column
            popup_cols: List of column names to display in hover tooltips
            color_col: Column to use for color coding markers
            size_col: Column to use for sizing markers
            zoom_start: Initial zoom level
            mapbox_style: Plotly mapbox style ('carto-positron', 'open-street-map', 'stamen-terrain', etc.)

        Returns:
            Plotly Figure object
        """
        # Create a copy to avoid modifying original data
        df_map = df.copy()

        for i in range(min(5, len(df_map))):
            print(f"  Row {i}: lat={df_map[lat_col].iloc[i]}, lon={df_map[lon_col].iloc[i]}")

        # Convert lat/lon columns to numeric, handling errors
        df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
        df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')

        # Debug: Print converted data
        print(f"\n✅ After numeric conversion:")
        for i in range(min(5, len(df_map))):
            print(f"  Row {i}: lat={df_map[lat_col].iloc[i]}, lon={df_map[lon_col].iloc[i]}")

        # Remove rows with invalid coordinates
        df_map = df_map.dropna(subset=[lat_col, lon_col])

        print(f"\n📍 Valid coordinates: {len(df_map)}/{len(df)} rows")

        if df_map.empty:
            raise ValueError("No valid coordinates found after conversion")

        # Calculate center and bounds
        center_lat = df_map[lat_col].mean()
        center_lon = df_map[lon_col].mean()

        # Get min/max coordinates for bounds
        lat_min, lat_max = df_map[lat_col].min(), df_map[lat_col].max()
        lon_min, lon_max = df_map[lon_col].min(), df_map[lon_col].max()

        # Calculate auto zoom level based on coordinate bounds
        auto_zoom = self.calculate_auto_zoom(lat_min, lat_max, lon_min, lon_max)

        # Use auto zoom if zoom_start is default (10), otherwise respect user's choice
        final_zoom = auto_zoom if zoom_start == 10 else zoom_start

        # Prepare hover data columns
        hover_data_dict = {}
        if popup_cols:
            for col in popup_cols:
                if col in df_map.columns and col not in [lat_col, lon_col]:
                    hover_data_dict[col] = True

        # Add color and size columns to hover data if they exist
        if color_col and color_col in df_map.columns:
            hover_data_dict[color_col] = True
        if size_col and size_col in df_map.columns:
            hover_data_dict[size_col] = True

        # Determine if color_col is categorical or numeric
        is_categorical = False
        if color_col and color_col in df_map.columns:
            is_categorical = not pd.api.types.is_numeric_dtype(df_map[color_col])

        # Create scatter_mapbox figure
        fig = px.scatter_mapbox(
            df_map,
            lat=lat_col,
            lon=lon_col,
            color=color_col if color_col else None,
            size=size_col if size_col else None,
            hover_data=hover_data_dict if hover_data_dict else None,
            color_discrete_sequence=self.CATEGORY_COLORS if is_categorical else None,
            color_continuous_scale="Viridis" if not is_categorical and color_col else None,
            mapbox_style=mapbox_style,
            zoom=final_zoom,
            center={"lat": center_lat, "lon": center_lon},
            opacity=0.7
        )

        # Update layout to prevent clipping and ensure full width
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            autosize=True,
            height=600,
            width=None,  # Let Streamlit control the width
            mapbox=dict(
                center={"lat": center_lat, "lon": center_lon},
                zoom=final_zoom
            ),
            # Remove any padding that might cause clipping
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # Update marker sizes if size_col is specified
        if size_col and size_col in df_map.columns:
            # Scale marker sizes between 5 and 20
            fig.update_traces(marker=dict(sizemode='diameter', sizemin=5, sizeref=2))


        return fig

    def create_polygon_map(
        self,
        df: pd.DataFrame,
        geometry_col: str,
        name_col: Optional[str] = None,
        value_col: Optional[str] = None,
        popup_cols: Optional[List[str]] = None,
        color_scheme: str = 'Blues',
        zoom_start: int = 10,
        show_context_boundary: Union[bool, str] = "auto",
        context_boundary_geojson: Optional[dict] = None
    ):
        """
        Create an interactive polygon map from geometry data using Plotly choropleth_mapbox.

        Args:
            df: DataFrame with geometry data
            geometry_col: Name of geometry column (WKT or GeoJSON format)
            name_col: Column with region/polygon names
            value_col: Column with numeric values for color coding
            popup_cols: List of column names to display in popups (used for hover_data)
            color_scheme: Plotly color scheme (Blues, Reds, Greens, etc.)
            zoom_start: Initial zoom level
            show_context_boundary: Not used in Plotly implementation
            context_boundary_geojson: Not used in Plotly implementation

        Returns:
            Plotly Figure object
        """
        # Create a copy to avoid modifying original data
        df_map = df.copy()

        # Convert to GeoDataFrame
        geometries = []
        valid_indices = []

        for idx, row in df_map.iterrows():
            geom_data = row[geometry_col]
            geom = self.parse_geometry(geom_data)

            if geom and geom.geom_type in ['Polygon', 'MultiPolygon']:
                geometries.append(geom)
                valid_indices.append(idx)
            else:
                print(f"  ⚠️  Skipping invalid geometry at row {idx}")

        if not geometries:
            raise ValueError("No valid polygon geometries found in data")

        # Filter dataframe to valid rows only
        df_map = df_map.loc[valid_indices].reset_index(drop=True)

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df_map, geometry=geometries, crs="EPSG:4326")

        print(f"  ✅ Created GeoDataFrame with {len(gdf)} polygons")

        # Auto-detect name column if not specified
        if not name_col:
            name_candidates = ['name', 'region', 'area', 'district', 'location', '지역', '이름', '명', '행정구역']
            for col in df_map.columns:
                if col.lower() in name_candidates or any(cand in col.lower() for cand in name_candidates):
                    name_col = col
                    print(f"  🏷️  Auto-detected name column: '{name_col}'")
                    break

        # Auto-detect rank column (highest priority)
        rank_col = None
        rank_keywords = ['rank', 'ranking', '순위', 'RANK']
        for col in df_map.columns:
            if col.lower() in rank_keywords or any(keyword in col.lower() for keyword in rank_keywords):
                rank_col = col
                break

        # Auto-detect value column if not specified (and no rank column)
        if not value_col and not rank_col:
            numeric_cols = df_map.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) > 0:
                value_col = numeric_cols[0]
                print(f"  📊 Auto-detected value column: '{value_col}'")

        # Calculate center using projected coordinates (EPSG:5179 for Korea)
        projected = gdf.to_crs(epsg=5179)
        center_lat = projected.geometry.centroid.to_crs(epsg=4326).y.mean()
        center_lon = projected.geometry.centroid.to_crs(epsg=4326).x.mean()

        # Calculate bounds for auto zoom
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        lon_min, lat_min, lon_max, lat_max = bounds

        # Calculate auto zoom level based on geometry bounds
        auto_zoom = self.calculate_auto_zoom(lat_min, lat_max, lon_min, lon_max)

        # Use auto zoom if zoom_start is default (10), otherwise respect user's choice
        final_zoom = auto_zoom if zoom_start == 10 else zoom_start

        # Prepare hover data columns
        hover_data_dict = {}
        if popup_cols:
            for col in popup_cols:
                if col in df_map.columns and col not in [geometry_col]:
                    hover_data_dict[col] = True

        # Add name and value columns to hover data if they exist
        if name_col and name_col in df_map.columns:
            hover_data_dict[name_col] = True
        if value_col and value_col in df_map.columns:
            hover_data_dict[value_col] = True

        # If rank column exists, use rank-based discrete colors
        if rank_col:
            print(f"  🎨 Using rank-based color scheme for '{rank_col}' column")

            # Normalize rank values to lowercase for matching
            gdf['_color_rank'] = gdf[rank_col].astype(str).str.lower().str.strip()

            # Map each region to its color based on rank
            # This creates a color map where each region name maps to a color
            color_discrete_map = {}
            for idx, row in gdf.iterrows():
                region_name = row[name_col] if name_col else str(idx)
                rank_value = row['_color_rank']
                if rank_value in self.RANK_COLOR_MAP:
                    color_discrete_map[region_name] = self.RANK_COLOR_MAP[rank_value]
                else:
                    color_discrete_map[region_name] = self.RANK_COLOR_MAP["default"]

            # Create a copy for plotting without geometry column to avoid serialization issues
            gdf_plot = gdf.drop(columns=['geometry'])

            # Create choropleth_mapbox figure with discrete colors
            # Fixed settings for rank-based maps
            # Show only penetration rate in hover, hide everything else
            hover_data_rank = {
                '1인여성가구_홈보안침투율': True,  # Show only this column
                '_color_rank': False,  # Hide internal color column
            }

            # Hide other columns only if they exist in the dataframe
            for col in ['inq', 'rank']:
                if col in gdf_plot.columns:
                    hover_data_rank[col] = False

            # Also explicitly hide name_col (행정구역) from hover_data
            if name_col and name_col in gdf_plot.columns:
                hover_data_rank[name_col] = False

            fig = px.choropleth_mapbox(
                gdf_plot,
                geojson=gdf.set_geometry('geometry').__geo_interface__,
                locations=gdf_plot.index,
                color=name_col if name_col else gdf_plot.index,  # Color by region name
                color_discrete_map=color_discrete_map,
                mapbox_style="carto-positron",
                center={"lat": 37.55, "lon": 127.0},  # Seoul center
                zoom=11,  # Fixed zoom level for rank maps
                opacity=0.8,
                hover_name='행정구역',  # Don't show any hover_name to avoid duplication
                hover_data=hover_data_rank
            )
        else:
            # Create choropleth_mapbox figure with continuous color scale (existing logic)
            fig = px.choropleth_mapbox(
                gdf,
                geojson=gdf.set_geometry('geometry').__geo_interface__,
                locations=gdf.index,
                color=value_col if value_col else None,
                color_continuous_scale=color_scheme,
                mapbox_style="carto-positron",
                center={"lat": center_lat, "lon": center_lon},
                zoom=final_zoom,
                opacity=0.7,
                hover_name=name_col if name_col else None,
                hover_data=hover_data_dict if hover_data_dict else None
            )

        # Update layout to prevent clipping and ensure full width with interactive controls
        # For rank maps, use fixed center and zoom; otherwise use calculated values
        map_center = {"lat": 37.55, "lon": 127.0} if rank_col else {"lat": center_lat, "lon": center_lon}
        map_zoom = 11 if rank_col else final_zoom

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            autosize=True,
            height=600,
            width=None,  # Let Streamlit control the width
            mapbox=dict(
                center=map_center,
                zoom=map_zoom
            ),
            # Remove any padding that might cause clipping
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            # Enable interactive controls
            dragmode='pan',
            hovermode='closest'
        )

        # Enable zoom controls and interaction
        fig.update_traces(
            marker=dict(opacity=0.9),
            selector=dict(type='choroplethmapbox')
        )

        # Configure modebar (toolbar) options for better UX
        config = {
            'scrollZoom': True,  # Enable scroll to zoom
            'displayModeBar': True,  # Show toolbar
            'displaylogo': False,  # Hide Plotly logo
            'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],
            'modeBarButtonsToRemove': ['select2d', 'lasso2d']
        }

        # Store config as attribute for Streamlit to use
        fig._config = config

        print(f"  ✅ Polygon map created successfully with {len(gdf)} regions")

        return fig



    def auto_create_map(
        self,
        df: pd.DataFrame,
        map_type: str = "auto"
    ):
        """
        Automatically create the most appropriate map based on data.

        Args:
            df: DataFrame with geographic data
            map_type: Type of map ('auto', 'point', 'heatmap', 'polygon')

        Returns:
            Plotly Figure object, or None if mapping not possible
        """
        can_map, reason = self.can_create_map(df)
        if not can_map:
            return None

        geo_cols = self.detect_geo_columns(df)

        # Priority 1: Check for geometry column (polygon data)
        if geo_cols['geometry']:
            geometry_col = geo_cols['geometry']

            # Check if it's valid polygon geometry
            if self.has_valid_geometry(df, geometry_col):
                print(f"🗺️  Detected polygon geometry in column '{geometry_col}'")

                # Auto-detect name column
                name_col = None
                name_candidates = ['name', 'region', 'area', 'district', 'location', '지역', '이름', '명', '행정구역']
                for col in df.columns:
                    if col != geometry_col and (col.lower() in name_candidates or any(cand in col.lower() for cand in name_candidates)):
                        name_col = col
                        break

                # Auto-detect value column (first numeric column)
                value_col = None
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if len(numeric_cols) > 0:
                    value_col = numeric_cols[0]

                # Determine popup columns (exclude geometry, name, value)
                popup_cols = [col for col in df.columns if col not in [geometry_col, name_col, value_col]][:5]

                # Create polygon map (returns Plotly Figure)
                return self.create_polygon_map(
                    df,
                    geometry_col=geometry_col,
                    name_col=name_col,
                    value_col=value_col,
                    popup_cols=popup_cols
                )

        # Priority 2: Check for lat/lon (point data)
        if geo_cols['latitude'] and geo_cols['longitude']:
            lat_col = geo_cols['latitude']
            lon_col = geo_cols['longitude']

            # Determine other columns for popup (exclude lat/lon)
            popup_cols = [col for col in df.columns if col not in [lat_col, lon_col]][:5]

            # Auto-detect category column for color coding
            color_col = None
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            # Exclude lat/lon columns
            categorical_cols = [c for c in categorical_cols if c not in [lat_col, lon_col]]
            if len(categorical_cols) > 0:
                color_col = categorical_cols[0]
                print(f"🎨 Auto-detected category column for colors: '{color_col}'")

            # Default to point map with category colors (returns Plotly Figure)
            return self.create_point_map(
                df, lat_col, lon_col,
                popup_cols=popup_cols,
                color_col=color_col
            )

        return None
