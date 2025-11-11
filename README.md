# Interactive Globe Project

A beautiful 3D interactive globe with country borders, similar to milradar.com. Built with Python Flask and Three.js.

## Features

- 3D globe with dark theme
- Country borders with cyan highlighting
- Interactive controls (drag to rotate, scroll to zoom)
- Click countries to view information
- Day/night visualization shader
- Atmosphere glow effect
- Latitude/longitude grid
- MySQL database for dynamic country data
- Support for sub-regions (e.g., US states)
- API endpoints for country management

## Requirements

- Python 3.8+
- MySQL/MariaDB (via phpMyAdmin or direct installation)
- Modern web browser with WebGL support

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure MySQL Database:**
   - Open `app.py`
   - Update the `DB_CONFIG` dictionary with your MySQL credentials:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'root',         # Your MySQL username
         'password': '',         # Your MySQL password
         'database': 'globe_db',
         'charset': 'utf8mb4',
         'cursorclass': pymysql.cursors.DictCursor
     }
     ```

3. **Run the application:**
   ```bash
   python app.py
   ```

   The application will:
   - Automatically create the `globe_db` database
   - Create the `regions` table
   - Start the Flask server on `http://localhost:5000`

4. **Open in browser:**
   Navigate to `http://localhost:5000`

## Project Structure

```
milradar/
├── app.py                      # Flask backend with API endpoints
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── index.html             # Main SPA page
└── static/
    ├── css/
    │   └── style.css          # Dark theme styling
    └── js/
        └── globe.js           # Three.js globe implementation
```

## Database Schema

### `regions` Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR(255) | Country/region name |
| code | VARCHAR(10) | ISO country code (e.g., 'USA', 'FRA') |
| parent_id | INT | Foreign key to parent region (for subdivisions) |
| region_type | VARCHAR(50) | Type: 'country', 'state', 'province', etc. |
| geojson_data | LONGTEXT | GeoJSON geometry for custom borders |
| custom_data | TEXT | JSON string for additional custom fields |
| owner | VARCHAR(255) | Owner (for game mechanics) |
| created_at | TIMESTAMP | Creation timestamp |

## API Endpoints

### Get All Regions
```
GET /api/regions
Query params:
  - type: Filter by region_type (e.g., 'country', 'state')
  - parent_id: Get child regions of a parent
```

### Get Region by ID
```
GET /api/region/<id>
```

### Get Region by Code
```
GET /api/region/code/<code>
```

### Create Region
```
POST /api/region
Body: {
  "name": "United States",
  "code": "USA",
  "region_type": "country",
  "owner": "PlayerName",
  "custom_data": "{\"population\": 331000000}"
}
```

### Update Region
```
PUT /api/region/<id>
Body: Same as create
```

## Adding Custom Data

You can add custom information to countries through the API or directly in the database:

### Example: Add country with custom data
```bash
curl -X POST http://localhost:5000/api/region \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Serbia",
    "code": "SRB",
    "region_type": "country",
    "owner": "Player1",
    "custom_data": "{\"population\": 7000000, \"capital\": \"Belgrade\"}"
  }'
```

### Example: Add US state as sub-region
```bash
# First, get USA's ID (let's say it's 1)
curl -X POST http://localhost:5000/api/region \
  -H "Content-Type: application/json" \
  -d '{
    "name": "California",
    "code": "US-CA",
    "parent_id": 1,
    "region_type": "state",
    "owner": "Player2"
  }'
```

## Controls

- **Drag**: Click and drag to rotate the globe
- **Scroll**: Zoom in/out
- **Click**: Click on a country to view information

## Future Enhancements

- Import detailed GeoJSON for accurate country shapes
- Add sub-region boundaries (states, provinces)
- Implement hover effects
- Add search functionality
- Create admin panel for managing regions
- Add conquest game mechanics
- Add country coloring based on ownership
- Implement real-time updates via WebSockets

## Technologies

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: Vanilla JavaScript, Three.js
- **3D Graphics**: WebGL
- **Geographic Data**: GeoJSON

## License

MIT License
