"""
Import DETAILED US States GeoJSON with high accuracy
Uses 10m resolution Natural Earth data or alternatives
"""
import sqlite3
import json
import requests

DATABASE = 'database/globe.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def clear_existing_states():
    """Remove old state data"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM regions WHERE region_type = 'state'")
    db.commit()
    db.close()
    print("Cleared old state data")

def import_detailed_us_states():
    """Import US states with HIGH DETAIL boundaries"""

    # High-detail sources (in order of preference)
    sources = [
        {
            'name': 'PublicaMundi (Good detail)',
            'url': 'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json',
            'filter_us': False
        },
        {
            'name': 'Python Folium Example Data',
            'url': 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json',
            'filter_us': False
        },
        {
            'name': 'Natural Earth 50m (Medium detail)',
            'url': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson',
            'filter_us': True
        },
        {
            'name': 'GeoJSON Maps',
            'url': 'https://raw.githubusercontent.com/datasets/geo-boundaries-us-110m/master/data/states.geojson',
            'filter_us': False
        }
    ]

    db = get_db()
    cursor = db.cursor()

    # Get USA parent ID
    cursor.execute('SELECT id FROM regions WHERE code = "USA"')
    usa = cursor.fetchone()
    parent_id = usa['id'] if usa else None

    if not parent_id:
        print("Creating USA parent...")
        cursor.execute('INSERT INTO regions (name, code, region_type) VALUES (?, ?, ?)',
                      ('United States', 'USA', 'country'))
        db.commit()
        parent_id = cursor.lastrowid

    # State code mapping
    state_codes = {
        'Alabama': 'US-AL', 'Alaska': 'US-AK', 'Arizona': 'US-AZ',
        'Arkansas': 'US-AR', 'California': 'US-CA', 'Colorado': 'US-CO',
        'Connecticut': 'US-CT', 'Delaware': 'US-DE', 'Florida': 'US-FL',
        'Georgia': 'US-GA', 'Hawaii': 'US-HI', 'Idaho': 'US-ID',
        'Illinois': 'US-IL', 'Indiana': 'US-IN', 'Iowa': 'US-IA',
        'Kansas': 'US-KS', 'Kentucky': 'US-KY', 'Louisiana': 'US-LA',
        'Maine': 'US-ME', 'Maryland': 'US-MD', 'Massachusetts': 'US-MA',
        'Michigan': 'US-MI', 'Minnesota': 'US-MN', 'Mississippi': 'US-MS',
        'Missouri': 'US-MO', 'Montana': 'US-MT', 'Nebraska': 'US-NE',
        'Nevada': 'US-NV', 'New Hampshire': 'US-NH', 'New Jersey': 'US-NJ',
        'New Mexico': 'US-NM', 'New York': 'US-NY', 'North Carolina': 'US-NC',
        'North Dakota': 'US-ND', 'Ohio': 'US-OH', 'Oklahoma': 'US-OK',
        'Oregon': 'US-OR', 'Pennsylvania': 'US-PA', 'Rhode Island': 'US-RI',
        'South Carolina': 'US-SC', 'South Dakota': 'US-SD', 'Tennessee': 'US-TN',
        'Texas': 'US-TX', 'Utah': 'US-UT', 'Vermont': 'US-VT',
        'Virginia': 'US-VA', 'Washington': 'US-WA', 'West Virginia': 'US-WV',
        'Wisconsin': 'US-WI', 'Wyoming': 'US-WY', 'Puerto Rico': 'US-PR',
        'District of Columbia': 'US-DC'
    }

    for source in sources:
        try:
            print(f"\nTrying: {source['name']}")
            print(f"URL: {source['url']}")

            response = requests.get(source['url'], timeout=60)
            response.raise_for_status()
            data = response.json()

            imported = 0
            features = data.get('features', [])
            print(f"Found {len(features)} features")

            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry')

                # Try different name fields
                name = (properties.get('name') or
                       properties.get('NAME') or
                       properties.get('name_en') or
                       properties.get('NAME_1') or
                       properties.get('admin') or
                       properties.get('gn_name') or
                       properties.get('id'))

                # Filter for US only if needed
                if source.get('filter_us'):
                    country = properties.get('admin') or properties.get('iso_a2') or ''
                    if 'United States' not in country and 'US' not in country:
                        continue

                if not name or not geometry:
                    continue

                # Get code
                code = state_codes.get(name, f"US-{name[:2].upper()}")

                # Check if geometry has meaningful data
                coords = geometry.get('coordinates', [])
                if not coords:
                    print(f"  [SKIP] {name}: no coordinates")
                    continue

                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO regions
                        (name, code, parent_id, region_type, geojson_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, code, parent_id, 'state', json.dumps(geometry)))

                    imported += 1

                    # Show sample coordinate count for debugging
                    if geometry['type'] == 'Polygon':
                        coord_count = len(coords[0]) if coords else 0
                    elif geometry['type'] == 'MultiPolygon':
                        coord_count = sum(len(poly[0]) for poly in coords) if coords else 0
                    else:
                        coord_count = 0

                    print(f"  [OK] {name} ({code}) - {coord_count} coordinates")

                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")

            db.commit()

            if imported > 0:
                print(f"\nSUCCESS: Imported {imported} states from {source['name']}")

                # Show quality info
                cursor.execute('SELECT name, LENGTH(geojson_data) as size FROM regions WHERE region_type="state" ORDER BY size DESC LIMIT 3')
                print("\nMost detailed states (by data size):")
                for row in cursor:
                    print(f"  {row['name']}: {row['size']:,} bytes")

                db.close()
                return True

            print(f"No states imported from this source")

        except Exception as e:
            print(f"  Failed: {e}")
            continue

    db.close()
    print("\nCould not import from any source")
    return False

if __name__ == '__main__':
    print("="*60)
    print("US States - DETAILED Import (High Accuracy)")
    print("="*60)

    print("\nStep 1: Clearing old state data...")
    clear_existing_states()

    print("\nStep 2: Importing detailed state boundaries...")
    if import_detailed_us_states():
        print("\n" + "="*60)
        print("SUCCESS! Restart server and refresh browser.")
        print("The new boundaries should be much more accurate.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("All sources failed.")
        print("="*60)
