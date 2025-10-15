# Polygon Map Visualization Implementation

## 📋 Overview

REGION_GENIE에서 `geometry` 컬럼으로 polygon 데이터를 받았을 때 지도로 시각화하는 기능이 구현되었습니다.

## ✅ 구현 완료 항목

### 1. Geometry 데이터 파싱 (`utils/map_helper.py`)

**추가된 메서드:**
- `parse_geometry(geometry_data)` - WKT/GeoJSON 형식 파싱
- `has_valid_geometry(df, geometry_col)` - Polygon geometry 유효성 검증

**지원 형식:**
- **WKT (Well-Known Text)**: `POLYGON((lng lat, lng lat, ...))`
- **GeoJSON**: `{"type": "Polygon", "coordinates": [[[lng, lat], ...]]}`
- **MultiPolygon**: 여러 개의 polygon을 하나의 feature로

### 2. Polygon 지도 생성 (`utils/map_helper.py`)

**추가된 메서드:**
- `create_polygon_map(df, geometry_col, name_col, value_col, popup_cols, color_scheme, zoom_start)`

**주요 기능:**
- Folium GeoJson 레이어 생성
- Choropleth 스타일 색상 매핑 (값에 따른 색상 변화)
- 자동 name/value 컬럼 감지
- 인터랙티브 popup 정보 표시
- 자동 지도 중심 및 줌 레벨 계산
- 범례 자동 생성

### 3. 자동 지도 생성 로직 (`utils/map_helper.py`)

**수정된 메서드:**
- `auto_create_map(df, map_type)` - Geometry 우선 처리 로직 추가

**우선순위:**
1. Geometry 컬럼 (Polygon/MultiPolygon) → `create_polygon_map()`
2. Lat/Lon 컬럼 (Point) → `create_point_map()`
3. 기타 → `None`

### 4. 통합 및 문서화

**통합 지점:**
- `data_helper.py:create_folium_map()` - 이미 `MapHelper.auto_create_map()` 호출하므로 자동 통합
- `core/message_handler.py` - REGION_GENIE 쿼리 처리 시 Folium map 자동 생성

**문서 업데이트:**
- `CLAUDE.md` - 새로운 기능 설명 추가
- `README.md` - Polygon map 시각화 기능 추가

## 🧪 테스트 결과

### 테스트 스크립트: `test_polygon_map.py`

**테스트 항목:**
1. ✅ Geometry 컬럼 자동 감지
2. ✅ WKT 형식 파싱 (POLYGON)
3. ✅ GeoJSON 형식 파싱
4. ✅ Polygon 지도 생성
5. ✅ Choropleth 색상 매핑
6. ✅ Interactive popup 생성

**생성된 결과물:**
- `test_polygon_map.html` - WKT 형식 테스트 지도
- `test_geojson_map.html` - GeoJSON 형식 테스트 지도

**테스트 명령:**
```bash
python test_polygon_map.py
```

## 🔧 기술 스택

### Python 라이브러리
- **shapely** (≥2.0.0): WKT/GeoJSON 파싱 및 geometry 연산
- **geopandas** (≥0.14.0): GeoDataFrame 생성 및 spatial 연산
- **folium** (≥0.15.0): 인터랙티브 지도 생성
- **pyproj** (≥3.6.0): 좌표계 변환 (필요 시)

### 좌표 시스템
- **CRS**: EPSG:4326 (WGS84) - 표준 위경도 좌표계

## 📊 사용 예시

### 1. WKT 형식 데이터

```python
import pandas as pd
from utils.data_helper import DataHelper

# Sample data with WKT geometry
data = {
    "region_name": ["서울", "부산"],
    "population": [9700000, 3400000],
    "geometry": [
        "POLYGON((126.85 37.45, 127.15 37.45, 127.15 37.65, 126.85 37.65, 126.85 37.45))",
        "POLYGON((128.95 35.05, 129.25 35.05, 129.25 35.25, 128.95 35.25, 128.95 35.05))"
    ]
}

df = pd.DataFrame(data)

# Create Folium map (automatic polygon detection)
folium_map = DataHelper.create_folium_map(df)

# Save to HTML
folium_map.save("region_map.html")
```

### 2. GeoJSON 형식 데이터

```python
data = {
    "region_name": ["Region A"],
    "value": [100],
    "geometry": [{
        "type": "Polygon",
        "coordinates": [[
            [126.85, 37.45],
            [127.15, 37.45],
            [127.15, 37.65],
            [126.85, 37.65],
            [126.85, 37.45]
        ]]
    }]
}

df = pd.DataFrame(data)
folium_map = DataHelper.create_folium_map(df)
```

### 3. REGION_GENIE 쿼리 (자동)

사용자가 REGION_GENIE에 다음과 같은 쿼리를 입력하면:

```
"서울시 구별 인구 분포를 보여줘"
```

시스템이 자동으로:
1. REGION_GENIE에 쿼리 전달
2. Geometry 컬럼 포함된 결과 수신
3. `create_folium_map()` 자동 호출
4. Polygon 지도 생성 및 표시

## 🎨 시각화 특징

### 색상 스타일링 (개선됨)
- **색상 방식**: 각 영역마다 구분 가능한 색상 (17가지 고유 색상)
- **색상 순환**: 17개 이상의 영역은 색상 재사용
- **불투명도**: 70% (fillOpacity=0.7)
- **경계선**: 흰색, 두께 2px
- **범례**: 자동 생성 (지역명 + 값 표시)

### Interactive 기능
- **Hover**: Polygon 위에 마우스를 올리면 하이라이트 (불투명도 90%, 경계선 두께 증가)
- **Click**: 마커 클릭 시 popup 정보 표시
- **Zoom**: 마우스 휠로 확대/축소
- **Pan**: 드래그로 지도 이동
- **자동 맞춤**: 첫 로드 시 모든 polygon이 보이도록 자동 줌/중심 조정 (50px 패딩)

### 범례 (Legend)
- **위치**: 우상단 고정
- **내용**: 각 지역의 색상 + 이름 + 값 (있는 경우)
- **스크롤**: 지역이 많을 경우 자동 스크롤 (최대 높이 400px)
- **스타일**: 그림자 효과, 둥근 모서리

### Popup 정보
- **지역명**: 자동 감지된 name 컬럼
- **수치값**: 자동 감지된 value 컬럼 (1000단위 구분자 포맷팅)
- **추가 정보**: popup_cols로 지정된 컬럼들
- **위치**: 각 polygon의 중심점(centroid)에 마커 표시

## 🔄 데이터 플로우

```
REGION_GENIE Query
    ↓
Genie API Response (with geometry column)
    ↓
message_handler.py: process_response()
    ↓
data_helper.py: create_folium_map()
    ↓
map_helper.py: auto_create_map()
    ↓
map_helper.py: detect_geo_columns() → geometry column detected
    ↓
map_helper.py: create_polygon_map()
    ↓
Folium Map (HTML)
    ↓
Streamlit Display (st.components.v1.html)
```

## 📝 Geometry 컬럼 감지 로직

### 우선순위
1. **컬럼명 매칭**: `geometry`, `geom`, `shape`, `wkt`, `wkb`
2. **데이터 형식 검증**: WKT/GeoJSON 형식 확인
3. **Geometry 타입 검증**: Polygon 또는 MultiPolygon 확인

### 자동 컬럼 감지
- **Name 컬럼**: `name`, `region`, `area`, `district`, `location`, `지역`, `이름`
- **Value 컬럼**: 첫 번째 숫자 컬럼 (numeric dtype)

## ⚠️ 알려진 제약사항

### 좌표계
- **지원**: EPSG:4326 (WGS84) 위경도 좌표
- **미지원**: 투영 좌표계 (필요 시 pyproj로 변환 필요)

### 성능
- **권장**: 1000개 이하 polygon
- **1000개 이상**: 렌더링 시간 증가, simplify() 고려

### 브라우저 호환성
- **권장**: Chrome, Firefox, Safari 최신 버전
- **IE**: 미지원

## 🚀 향후 개선 사항

### 단기 (구현 가능)
- [ ] Polygon simplify() 옵션 (대용량 데이터 최적화)
- [ ] 다양한 색상 스키마 선택 옵션
- [ ] Tooltip 추가 (hover 시 정보 표시)
- [ ] 클러스터링 (1000개 이상 polygon)

### 중기 (추가 연구 필요)
- [ ] 좌표계 자동 변환 (EPSG 감지 및 변환)
- [ ] 3D 지도 시각화 (높이 데이터 활용)
- [ ] 애니메이션 효과 (시간에 따른 변화)
- [ ] 커스텀 베이스맵 선택

## 📚 참고 자료

- **Shapely Documentation**: https://shapely.readthedocs.io/
- **GeoPandas Guide**: https://geopandas.org/
- **Folium Documentation**: https://python-visualization.github.io/folium/
- **WKT Format Spec**: https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
- **GeoJSON Spec**: https://geojson.org/

## 🎯 실제 사용 케이스

### 1. 서울시 구별 인구 분포
```sql
-- REGION_GENIE 쿼리 예시
SELECT
    district_name,
    population,
    ST_AsText(boundary) as geometry
FROM seoul_districts
```

### 2. 전국 시도별 GDP
```sql
SELECT
    province_name,
    gdp_value,
    ST_AsText(boundary) as geometry
FROM korea_provinces
```

### 3. 상권 분석 (폴리곤)
```sql
SELECT
    business_zone,
    avg_revenue,
    ST_AsText(zone_boundary) as geometry
FROM commercial_zones
```

## ✅ 구현 완료 체크리스트

- [x] Geometry 파싱 메서드 구현
- [x] Polygon 지도 생성 메서드 구현
- [x] 자동 감지 로직 통합
- [x] WKT 형식 지원
- [x] GeoJSON 형식 지원
- [x] Choropleth 스타일링
- [x] Interactive popup
- [x] 자동 name/value 컬럼 감지
- [x] 테스트 스크립트 작성
- [x] 테스트 실행 및 검증
- [x] 문서화 (CLAUDE.md, README.md)
- [x] 기존 시스템 통합 확인

## 🎉 결론

Polygon 지도 시각화 기능이 성공적으로 구현되었습니다. REGION_GENIE에서 geometry 컬럼을 포함한 데이터를 반환하면, 시스템이 자동으로 인터랙티브한 Choropleth 지도를 생성하여 표시합니다.

**주요 성과:**
- WKT 및 GeoJSON 형식 모두 지원
- 자동 감지 및 처리로 사용자 경험 최적화
- 기존 Point map과 동일한 UX 제공
- 확장 가능한 아키텍처 유지


## 🏙️ 서울 권역 전용 기능 (2024.10.15 추가)

### 배경 윤곽선 자동 표시
**목적**: 서울시 구별 데이터 시각화 시 서울 전체 경계를 배경으로 표시

**동작 방식**:
1. **자동 감지**: 지역명 컬럼에서 서울 자치구 이름 감지 (강남구, 서초구 등)
2. **배경 레이어 추가**: 서울시 전체 경계를 회색 투명 윤곽선으로 표시
3. **전경 레이어**: 구별 데이터를 밝은 색상으로 오버레이

**시각적 효과**:
- 배경: 연한 회색 (fillOpacity=0.15), 점선 경계
- 전경: 각 구마다 구분 가능한 색상 (fillOpacity=0.7)
- 결과: 서울 전체 컨텍스트 안에서 구별 데이터 위치 명확히 파악

**구현 파일**:
- `utils/seoul_boundary.py` - 서울 경계 GeoJSON 및 자동 감지 로직
- `utils/map_helper.py` - 배경 레이어 추가 로직

**테스트**:
```bash
python test_seoul_polygon.py
```

**생성 파일**:
- `test_seoul_districts.html` - 서울 구별 지도 (배경 윤곽선 있음)
- `test_non_seoul_regions.html` - 비서울 지도 (배경 윤곽선 없음)

