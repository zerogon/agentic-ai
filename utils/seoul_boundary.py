"""
Seoul Boundary GeoJSON Data

Provides geographic boundary data for Seoul metropolitan area
to be used as context layer in polygon maps.
"""

# Simplified Seoul boundary (rectangular approximation)
# Coordinates based on Seoul's approximate geographic extent
SEOUL_SIMPLE_BOUNDARY = {
    "type": "Feature",
    "properties": {
        "name": "서울특별시",
        "name_en": "Seoul",
        "type": "metropolitan_boundary"
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [126.764, 37.429],  # Southwest corner
            [127.184, 37.429],  # Southeast corner
            [127.184, 37.702],  # Northeast corner
            [126.764, 37.702],  # Northwest corner
            [126.764, 37.429]   # Close the polygon
        ]]
    }
}

# More accurate Seoul boundary (8-point polygon for better shape)
SEOUL_BOUNDARY = {
    "type": "Feature",
    "properties": {
        "name": "서울특별시",
        "name_en": "Seoul Metropolitan City",
        "type": "administrative_boundary"
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            # Approximated from actual Seoul administrative boundary
            # Points arranged clockwise from southwest
            [126.765, 37.430],  # Southwest (Geumcheon-gu area)
            [126.820, 37.413],  # South-southwest (Gwanak-gu)
            [127.050, 37.413],  # South (Gangnam-gu)
            [127.140, 37.470],  # Southeast (Songpa-gu)
            [127.184, 37.540],  # East (Gangdong-gu)
            [127.120, 37.680],  # Northeast (Nowon-gu)
            [126.950, 37.702],  # North (Dobong-gu)
            [126.800, 37.650],  # Northwest (Eunpyeong-gu)
            [126.780, 37.550],  # West (Gangseo-gu)
            [126.765, 37.430]   # Close the polygon
        ]]
    }
}

# Seoul district names (for auto-detection)
SEOUL_DISTRICTS = [
    # 강남권 (Gangnam area)
    "강남구", "서초구", "송파구", "강동구",

    # 강북권 (Gangbuk area)
    "종로구", "중구", "용산구", "성동구", "광진구",
    "동대문구", "중랑구", "성북구", "강북구", "도봉구",
    "노원구", "은평구", "서대문구", "마포구", "양천구",
    "강서구", "구로구", "금천구", "영등포구", "동작구",
    "관악구"
]

# English names for reference
SEOUL_DISTRICTS_EN = [
    "Gangnam-gu", "Seocho-gu", "Songpa-gu", "Gangdong-gu",
    "Jongno-gu", "Jung-gu", "Yongsan-gu", "Seongdong-gu", "Gwangjin-gu",
    "Dongdaemun-gu", "Jungnang-gu", "Seongbuk-gu", "Gangbuk-gu", "Dobong-gu",
    "Nowon-gu", "Eunpyeong-gu", "Seodaemun-gu", "Mapo-gu", "Yangcheon-gu",
    "Gangseo-gu", "Guro-gu", "Geumcheon-gu", "Yeongdeungpo-gu", "Dongjak-gu",
    "Gwanak-gu"
]


def is_seoul_district(name: str) -> bool:
    """
    Check if a region name is a Seoul district.

    Args:
        name: Region name to check

    Returns:
        True if the name matches a Seoul district
    """
    if not name:
        return False

    name_lower = name.lower().strip()

    # Check Korean names
    for district in SEOUL_DISTRICTS:
        if district.lower() in name_lower or name_lower in district.lower():
            return True

    # Check English names
    for district in SEOUL_DISTRICTS_EN:
        if district.lower() in name_lower or name_lower in district.lower():
            return True

    return False


def detect_seoul_data(df, name_col: str) -> bool:
    """
    Detect if a DataFrame contains Seoul district data.

    Args:
        df: DataFrame with region data
        name_col: Name of the column containing region names

    Returns:
        True if data appears to be Seoul districts
    """
    import pandas as pd

    if not name_col or name_col not in df.columns:
        return False

    # Check first 5 rows for Seoul district names
    sample_size = min(5, len(df))
    seoul_count = 0

    for idx in range(sample_size):
        region_name = str(df[name_col].iloc[idx])
        if is_seoul_district(region_name):
            seoul_count += 1

    # If majority (>50%) of samples are Seoul districts, consider it Seoul data
    return seoul_count > (sample_size / 2)


def get_seoul_boundary(simplified: bool = False) -> dict:
    """
    Get Seoul boundary GeoJSON.

    Args:
        simplified: If True, return simplified rectangular boundary

    Returns:
        GeoJSON Feature dict
    """
    return SEOUL_SIMPLE_BOUNDARY if simplified else SEOUL_BOUNDARY
