"""
Import higher quality US States GeoJSON data
This uses a better data source with more accurate boundaries
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

def import_us_states_high_quality():
    """Import US states from a better quality source"""

    # Try multiple sources, in order of quality
    sources = [
        {
            'name': 'Eric Clst (High Quality)',
            'url': 'https://raw.githubusercontent.com/datasets/geo-us-states/master/data/admin.geojson'
        },
        {
            'name': 'Natural Earth',
            'url': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_1_states_provinces.geojson'
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

    for source in sources:
        try:
            print(f"\nTrying source: {source['name']}")
            print(f"URL: {source['url']}")

            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            data = response.json()

            imported = 0
            features = data.get('features', [])
            print(f"Found {len(features)} features")

            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry')

                # Try different property names for US states
                name = (properties.get('name') or
                       properties.get('NAME') or
                       properties.get('name_en') or
                       properties.get('admin') or
                       properties.get('gn_name'))

                # Filter for US states only if this is a world dataset
                country = properties.get('admin') or properties.get('country') or 'USA'
                if 'United States' not in country and country != 'USA':
                    continue

                if not name:
                    continue

                # Generate code
                code = f"US-{name[:2].upper()}" if len(name) >= 2 else f"US-{name.upper()}"

                # Better code mapping for common states
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

                code = state_codes.get(name, code)

                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO regions
                        (name, code, parent_id, region_type, geojson_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, code, parent_id, 'state', json.dumps(geometry)))

                    imported += 1
                    print(f"  [OK] {name} ({code})")

                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")

            db.commit()

            if imported > 0:
                print(f"\n✓ Successfully imported {imported} states from {source['name']}")
                db.close()
                return True

        except Exception as e:
            print(f"  Failed: {e}")
            continue

    db.close()
    print("\n✗ Could not import from any source")
    return False

if __name__ == '__main__':
    print("="*60)
    print("US States - High Quality Import")
    print("="*60)

    print("\nStep 1: Clearing old state data...")
    clear_existing_states()

    print("\nStep 2: Importing high-quality state boundaries...")
    if import_us_states_high_quality():
        print("\n" + "="*60)
        print("SUCCESS! Restart your server to see the changes.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Import failed. You may need to download GeoJSON manually.")
        print("See ADDING_REGIONS.md for alternative sources.")
        print("="*60)
