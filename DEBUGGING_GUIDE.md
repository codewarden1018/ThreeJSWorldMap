# Debugging Guide - Globe Click Detection & Borders

## What I've Added:

### ✓ Border Highlighting
When you click a region, its borders now **light up in RED** (like milradar.com)

### ✓ Console Debug Messages
The browser will now show you exactly what's being clicked

---

## How to Start the Server & See Console Output:

### Option 1: Use the Batch File (Recommended)
1. **Double-click** `start_server.bat` in the project folder
2. A command window will open showing server output
3. **Keep this window open** - it shows what the server is doing

### Option 2: Manual Start
1. Open Command Prompt in the project folder
2. Run: `python app_sqlite.py`
3. Keep the terminal open

---

## How to Debug Click Detection:

### Step 1: Open Browser Console
1. Go to http://localhost:5000
2. Press **F12** (or right-click → Inspect)
3. Click the **Console** tab at the top

### Step 2: Click on the Globe
When you click anywhere, you'll see messages like:
```
Clicked at: lat=31.50, lon=-99.75
Found sub-region: Texas
Selected region: Texas USA-TEX
```

### Step 3: Understand What You See

**If it shows the CORRECT region:**
```
Clicked at: lat=31.50, lon=-99.75
Found sub-region: Texas        ← Correct!
```
✓ Click detection is working

**If it shows WRONG region:**
```
Clicked at: lat=36.00, lon=-97.50
Found sub-region: Oklahoma     ← You clicked near the border
```
→ This means you clicked near the Oklahoma/Texas border
→ The point-in-polygon algorithm detected Oklahoma
→ Try clicking more in the center of the region

**If it shows NO region:**
```
Clicked at: lat=31.50, lon=-99.75
No region found at this point
```
→ The click point isn't inside any region in the database
→ GeoJSON data might be missing or incomplete

---

## Border Highlighting Feature:

When you click a region:
1. **Previous highlights** are cleared (back to original color)
2. **New region borders** turn **RED** (bright highlight)
3. **Info panel** shows the region name

To clear highlights:
- Click the **X** button on the info panel
- Click another region (it will clear old and highlight new)

---

## Known Issues & Workarounds:

### Issue 1: Incomplete Borders
**Symptom**: Some state borders appear broken or incomplete

**Causes**:
- GeoJSON data quality issues
- Longitude wrapping at ±180° (date line)
- MultiPolygon structures

**Workaround**:
- I've added date line crossing detection
- If borders still incomplete, the GeoJSON source data may be simplified
- You can replace with higher-quality GeoJSON files

### Issue 2: Click Detection Off By One
**Symptom**: You click Texas but get Oklahoma

**Causes**:
1. **Border clicks**: You're clicking right on the border line
2. **Polygon overlap**: Regions might overlap slightly in the data
3. **Coordinate precision**: Small rounding errors

**Solutions**:
- Click more in the **center** of regions
- The ray-casting algorithm works on exact coordinates
- Border pixels might be ambiguous

### Issue 3: Can't Click Small Regions
**Symptom**: Small states are hard to click

**Solution**:
- **Zoom in** using scroll wheel
- Get closer to the region
- Click in the center, not edges

---

## Testing Checklist:

Run through these tests to verify everything works:

### ✓ Basic Clicking
- [ ] Click Texas → Shows "Texas" + RED borders
- [ ] Click California → Shows "California" + RED borders
- [ ] Click France → Shows "France" + CYAN borders (countries)

### ✓ Border Colors
- [ ] Countries: CYAN (#66ffcc)
- [ ] States: ORANGE (#ffaa44)
- [ ] Selected: RED (#ff0000)

### ✓ Info Panel
- [ ] Shows region name
- [ ] Shows code (e.g., "USA-TEX")
- [ ] Shows type (State/Country)
- [ ] Close button works
- [ ] Closing clears red highlight

### ✓ Console Output
- [ ] Shows lat/lon when clicking
- [ ] Shows "Found sub-region: [Name]"
- [ ] Shows "Selected region: [Name] [Code]"

---

## Advanced Debugging:

### Check Database Content
Run this to see all states in database:
```bash
python -c "import sqlite3; db = sqlite3.connect('database/globe.db'); cursor = db.cursor(); cursor.execute('SELECT name, code FROM regions WHERE region_type=\"state\"'); print(cursor.fetchall())"
```

### Check Specific Region Data
```bash
python -c "import sqlite3, json; db = sqlite3.connect('database/globe.db'); cursor = db.cursor(); cursor.execute('SELECT name, code, geojson_data FROM regions WHERE name=\"Texas\"'); row = cursor.fetchone(); print(f'Name: {row[0]}'); print(f'Code: {row[1]}'); print(f'Has GeoJSON: {bool(row[2])}')"
```

### Verify Point-in-Polygon for Texas
Texas approximate center: 31.5°N, 99.5°W

In browser console, test if a point is in Texas:
```javascript
// After clicking Texas once to load it
const texas = Array.from(globe.countries.values()).find(r => r.name === 'Texas');
const isInside = globe.isPointInRegion(31.5, -99.5, texas.geometry);
console.log('Point in Texas:', isInside); // Should be true
```

---

## Getting Better GeoJSON Data:

If borders are still incomplete, try higher-quality GeoJSON:

### US States (High Detail)
- https://eric.clst.org/tech/usgeojson/
- https://github.com/PublicaMundi/MappingAPI (current source)
- https://github.com/nvkelso/natural-earth-vector

### How to Replace Data:
1. Download new GeoJSON file
2. Save as `us-states-detailed.geojson`
3. Run:
```python
from import_regions import import_geojson_from_file
import_geojson_from_file('us-states-detailed.geojson', 'state', 'USA')
```
4. Restart server

---

## Next Steps:

1. **Run the server** using `start_server.bat`
2. **Open browser** to http://localhost:5000
3. **Open console** (F12)
4. **Click regions** and watch console output
5. **Report what you see** - the console messages will tell us exactly what's happening!

The console output is the key to debugging this. Let me know what messages appear when you click!
