"""
Map Helper for Geospatial Visualization

Provides utilities for working with geospatial data and creating interactive maps.
"""

import pandas as pd
import folium
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

    def __init__(self):
        """Initialize the MapHelper."""
        pass

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
        zoom_start: int = 10
    ) -> folium.Map:
        """
        Create an interactive point map from latitude/longitude data.

        Args:
            df: DataFrame with geographic data
            lat_col: Name of latitude column
            lon_col: Name of longitude column
            popup_cols: List of column names to display in popups
            color_col: Column to use for color coding markers
            size_col: Column to use for sizing markers
            zoom_start: Initial zoom level

        Returns:
            Folium Map object
        """
        # Create a copy to avoid modifying original data
        df_map = df.copy()

        # Debug: Print original data
        print(f"\n🔍 CREATE_POINT_MAP - Original data types:")
        print(f"  - {lat_col} dtype: {df_map[lat_col].dtype}")
        print(f"  - {lon_col} dtype: {df_map[lon_col].dtype}")
        print(f"\n📊 Sample original values (first 5):")
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

        print(f"\n🎯 Map center: ({center_lat:.6f}, {center_lon:.6f})")
        print(f"📏 Coordinate ranges:")
        print(f"  - Latitude: {lat_min:.6f} to {lat_max:.6f}")
        print(f"  - Longitude: {lon_min:.6f} to {lon_max:.6f}")

        # Create base map (zoom_start will be overridden by fit_bounds)
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )

        # Create category to color mapping if color_col is categorical
        category_color_map = {}
        if color_col and color_col in df_map.columns:
            if not pd.api.types.is_numeric_dtype(df_map[color_col]):
                unique_categories = df_map[color_col].unique()
                for idx, category in enumerate(unique_categories):
                    category_color_map[category] = self.CATEGORY_COLORS[idx % len(self.CATEGORY_COLORS)]
                print(f"\n🎨 Created color mapping for {len(unique_categories)} categories")
                for category, color in list(category_color_map.items())[:5]:
                    print(f"  - {category}: {color}")
                if len(category_color_map) > 5:
                    print(f"  ... and {len(category_color_map) - 5} more")

        # Add points (use df_map with converted coordinates)
        marker_count = 0
        for idx, row in df_map.iterrows():
            lat = row[lat_col]
            lon = row[lon_col]

            # Skip invalid coordinates
            if pd.isna(lat) or pd.isna(lon):
                continue

            marker_count += 1
            if marker_count <= 3:
                print(f"  🔵 Adding marker {marker_count}: ({lat:.6f}, {lon:.6f})")

            # Build popup content
            popup_html = ""
            if popup_cols:
                popup_html = "<div style='font-family: Arial; font-size: 12px;'>"
                for col in popup_cols:
                    if col in row:
                        popup_html += f"<b>{col}:</b> {row[col]}<br>"
                popup_html += "</div>"

            # Determine marker color
            color = 'blue'
            if color_col and color_col in row:
                value = row[color_col]

                # Check if categorical (using pre-built color map)
                if category_color_map and value in category_color_map:
                    color = category_color_map[value]
                elif isinstance(value, (int, float)):
                    # Use value-based coloring for numeric data (use df_map for min/max)
                    max_val = df_map[color_col].max()
                    min_val = df_map[color_col].min()
                    if max_val > min_val:
                        normalized = (value - min_val) / (max_val - min_val)
                        if normalized > 0.66:
                            color = 'red'
                        elif normalized > 0.33:
                            color = 'orange'
                        else:
                            color = 'green'

            # Determine marker size
            radius = 8
            if size_col and size_col in row:
                value = row[size_col]
                if isinstance(value, (int, float)):
                    # Use df_map for min/max
                    max_val = df_map[size_col].max()
                    min_val = df_map[size_col].min()
                    if max_val > min_val:
                        # Scale between 5 and 20
                        normalized = (value - min_val) / (max_val - min_val)
                        radius = 5 + (normalized * 15)

            # Add marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300) if popup_html else None,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)

        print(f"\n✅ Total markers added: {marker_count}")

        # Add legend if color_col is used
        if color_col and color_col in df_map.columns:
            # Get unique categories
            unique_categories = df_map[color_col].unique()

            # Only add legend for categorical data (not numeric)
            if not pd.api.types.is_numeric_dtype(df_map[color_col]):
                # Create legend HTML
                legend_html = '''
                <div style="position: fixed;
                            top: 10px; right: 10px; width: 200px;
                            background-color: white;
                            border: 2px solid grey;
                            border-radius: 5px;
                            z-index: 9999;
                            font-size: 14px;
                            padding: 10px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    <p style="margin: 0 0 10px 0; font-weight: bold; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
                        Category Legend
                    </p>
                '''

                # Create category to color mapping
                category_colors = {}
                for idx, category in enumerate(unique_categories):
                    color = self.CATEGORY_COLORS[idx % len(self.CATEGORY_COLORS)]
                    category_colors[category] = color
                    legend_html += f'''
                    <p style="margin: 5px 0; display: flex; align-items: center;">
                        <span style="display: inline-block; width: 20px; height: 20px;
                                     background-color: {color}; border-radius: 50%;
                                     margin-right: 8px; border: 1px solid #999;"></span>
                        <span style="flex: 1;">{category}</span>
                    </p>
                    '''

                legend_html += '</div>'

                # Add legend to map
                m.get_root().html.add_child(folium.Element(legend_html))

                print(f"🎨 Added legend with {len(unique_categories)} categories")

        # Fit map bounds to show all markers with some padding
        # Create bounds: [[south-west corner], [north-east corner]]
        bounds = [[lat_min, lon_min], [lat_max, lon_max]]
        m.fit_bounds(bounds, padding=[30, 30])  # Add 30px padding on all sides

        print(f"🗺️  Map fitted to bounds: SW({lat_min:.6f}, {lon_min:.6f}) to NE({lat_max:.6f}, {lon_max:.6f})")

        return m

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

        # Auto-detect value column if not specified
        if not value_col:
            numeric_cols = df_map.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) > 0:
                value_col = numeric_cols[0]
                print(f"  📊 Auto-detected value column: '{value_col}'")

        # Calculate center using projected coordinates (EPSG:5179 for Korea)
        projected = gdf.to_crs(epsg=5179)
        center_lat = projected.geometry.centroid.to_crs(epsg=4326).y.mean()
        center_lon = projected.geometry.centroid.to_crs(epsg=4326).x.mean()

        print(f"  🎯 Map center: ({center_lat:.6f}, {center_lon:.6f})")

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

        # Create choropleth_mapbox figure
        fig = px.choropleth_mapbox(
            gdf,
            geojson=gdf.set_geometry('geometry').__geo_interface__,
            locations=gdf.index,
            color=value_col if value_col else None,
            color_continuous_scale=color_scheme,
            mapbox_style="carto-positron",
            center={"lat": center_lat, "lon": center_lon},
            zoom=zoom_start,
            opacity=0.7,
            hover_name=name_col if name_col else None,
            hover_data=hover_data_dict if hover_data_dict else None
        )

        # Update layout to prevent clipping and ensure full width
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            autosize=True,
            height=600,
            width=None,  # Let Streamlit control the width
            mapbox=dict(
                center={"lat": center_lat, "lon": center_lon},
                zoom=zoom_start
            ),
            # Remove any padding that might cause clipping
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        print(f"  ✅ Polygon map created successfully with {len(gdf)} regions")

        return fig

    def create_heatmap(
        self,
        df: pd.DataFrame,
        lat_col: str,
        lon_col: str,
        weight_col: Optional[str] = None,
        zoom_start: int = 10
    ) -> folium.Map:
        """
        Create a heatmap from point data.

        Args:
            df: DataFrame with geographic data
            lat_col: Name of latitude column
            lon_col: Name of longitude column
            weight_col: Column to use for heatmap intensity
            zoom_start: Initial zoom level

        Returns:
            Folium Map object
        """
        from folium.plugins import HeatMap

        # Create a copy to avoid modifying original data
        df_map = df.copy()

        # Convert lat/lon columns to numeric, handling errors
        df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
        df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')

        # Remove rows with invalid coordinates
        df_map = df_map.dropna(subset=[lat_col, lon_col])

        if df_map.empty:
            raise ValueError("No valid coordinates found after conversion")

        # Calculate center and bounds
        center_lat = df_map[lat_col].mean()
        center_lon = df_map[lon_col].mean()

        # Get min/max coordinates for bounds
        lat_min, lat_max = df_map[lat_col].min(), df_map[lat_col].max()
        lon_min, lon_max = df_map[lon_col].min(), df_map[lon_col].max()

        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )

        # Prepare heatmap data (use df_map with converted coordinates)
        heat_data = []
        for idx, row in df_map.iterrows():
            lat = row[lat_col]
            lon = row[lon_col]

            if pd.isna(lat) or pd.isna(lon):
                continue

            if weight_col and weight_col in row:
                weight = row[weight_col]
                heat_data.append([lat, lon, weight])
            else:
                heat_data.append([lat, lon])

        # Add heatmap layer
        HeatMap(heat_data).add_to(m)

        # Fit map bounds to show all data points with padding
        bounds = [[lat_min, lon_min], [lat_max, lon_max]]
        m.fit_bounds(bounds, padding=[30, 30])

        return m

    def create_choropleth_map(
        self,
        df: pd.DataFrame,
        geo_data: Any,
        location_col: str,
        value_col: str,
        key_on: str = 'feature.properties.name',
        color_scheme: str = 'blue',
        zoom_start: int = 6
    ) -> folium.Map:
        """
        Create a choropleth (thematic) map.

        Args:
            df: DataFrame with data to visualize
            geo_data: GeoJSON data or path to GeoJSON file
            location_col: Column in df that matches geo_data features
            value_col: Column with values to visualize
            key_on: Property in geo_data to match with location_col
            color_scheme: Color scheme to use
            zoom_start: Initial zoom level

        Returns:
            Folium Map object
        """
        # Create base map (centered on data)
        m = folium.Map(
            location=[37.5665, 126.9780],  # Default: Seoul
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )

        # Create choropleth
        folium.Choropleth(
            geo_data=geo_data,
            name='choropleth',
            data=df,
            columns=[location_col, value_col],
            key_on=key_on,
            fill_color=color_scheme.capitalize(),
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=value_col
        ).add_to(m)

        folium.LayerControl().add_to(m)

        return m

    def map_to_html(self, folium_map: folium.Map) -> str:
        """
        Convert Folium map to HTML string.

        Args:
            folium_map: Folium Map object

        Returns:
            HTML string representation of the map
        """
        return folium_map._repr_html_()

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
            Plotly Figure for polygon data, Folium Map for point/heatmap data, or None if mapping not possible
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

            if map_type == "heatmap":
                return self.create_heatmap(df, lat_col, lon_col)
            else:
                # Default to point map with category colors (returns Folium Map)
                return self.create_point_map(
                    df, lat_col, lon_col,
                    popup_cols=popup_cols,
                    color_col=color_col
                )

        return None
