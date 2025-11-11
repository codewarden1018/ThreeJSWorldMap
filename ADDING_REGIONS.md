# Adding Regions (States, Provinces, etc.)

This guide explains how to add sub-regions like US states, Canadian provinces, or any other territorial subdivisions to your interactive globe.

## Overview

Sub-regions are stored in the database with a `parent_id` that links them to their parent country. They have their own GeoJSON geometry data that defines their borders.

## Color Coding

- **Countries**: Cyan borders (#66ffcc)
- **Sub-regions** (states, provinces): Orange/Yellow borders (#ffaa44)

## Method 1: Import from GeoJSON URL

The easiest way is to use the `import_regions.py` script:

```bash
python import_regions.py
```

This will automatically:
1. Create a USA country entry
2. Download US states GeoJSON data
3. Import all 50 states into the database

## Method 2: Import from Local File

If you have a GeoJSON file locally:

```python
from import_regions import import_geojson_from_file

# Import Canadian provinces
import_geojson_from_file(
    filepath='path/to/canada-provinces.geojson',
    region_type='province',
    parent_code='CAN'
)
```

## Method 3: Manual API Import

You can also add regions via the API:

```bash
# First, create the parent country (if it doesn't exist)
curl -X POST http://localhost:5000/api/region ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"United States\", \"code\": \"USA\", \"region_type\": \"country\"}"

# Then, add a state with GeoJSON data
curl -X POST http://localhost:5000/api/region ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"California\", \"code\": \"US-CA\", \"parent_id\": 1, \"region_type\": \"state\", \"geojson_data\": \"{...geometry...}\"}"
```

## Where to Find GeoJSON Data

### US States
- https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json
- https://github.com/datasets/geo-us-states

### Other Regions
- **World Countries**: https://github.com/datasets/geo-countries
- **Canadian Provinces**: https://github.com/codeforamerica/click_that_hood/blob/master/public/data/canada.geojson
- **UK Counties**: https://github.com/martinjc/UK-GeoJSON
- **EU Countries**: https://github.com/leakyMirror/map-of-europe
- **General GeoJSON**: https://geojson-maps.ash.ms/

### Custom GeoJSON

You can also create your own GeoJSON using:
- **geojson.io**: Draw regions manually
- **QGIS**: Professional GIS software
- **Mapshaper**: Simplify complex GeoJSON files

## Database Schema

When you import a region, it's stored with this structure:

| Field | Description | Example |
|-------|-------------|---------|
| id | Auto-generated ID | 1 |
| name | Region name | "California" |
| code | Unique code | "US-CA" |
| parent_id | ID of parent region | 1 (USA's ID) |
| region_type | Type of region | "state" |
| geojson_data | JSON geometry | "{\"type\":\"Polygon\",...}" |
| owner | Owner (for game) | "Player1" |
| custom_data | Custom JSON data | "{\"population\":39000000}" |

## Viewing Regions

After importing:

1. **Restart the Flask server** (Ctrl+C, then `python app_sqlite.py`)
2. **Refresh your browser** at http://localhost:5000
3. **Sub-regions appear in orange/yellow** on the globe
4. **Click them** to see their information

## Example: Import Multiple Region Sets

```python
from import_regions import import_geojson_from_url, create_usa_country

# US States
create_usa_country()
import_geojson_from_url(
    url='https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json',
    region_type='state',
    parent_code='USA'
)

# Canadian Provinces (if you have the file)
import_geojson_from_file(
    filepath='canada-provinces.geojson',
    region_type='province',
    parent_code='CAN'
)
```

## Troubleshooting

### Regions Don't Appear
- Make sure you restarted the Flask server
- Check browser console (F12) for errors
- Verify data in database: Open `database/globe.db` in SQLite browser

### Wrong Colors
- Countries: cyan (#66ffcc)
- Sub-regions: orange (#ffaa44)
- Check the `region_type` field in database

### Click Detection Not Working
- Click detection is simplified in current version
- For accurate detection, you need point-in-polygon algorithms
- Will be improved in future updates

## Advanced: Custom Region Properties

You can add custom data to regions for your game:

```python
import json

custom_data = {
    'population': 39000000,
    'capital': 'Sacramento',
    'strength': 100,
    'defense': 75
}

# Via API
cursor.execute('''
    UPDATE regions
    SET custom_data = ?, owner = ?
    WHERE code = ?
''', (json.dumps(custom_data), 'Player1', 'US-CA'))
```

This data will appear in the info panel when you click the region!
