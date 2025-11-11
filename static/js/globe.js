import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class InteractiveGlobe {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.globe = null;
        this.atmosphere = null;
        this.countries = new Map();
        this.regionBorders = [];
        this.selectedRegion = null;
        this.hoveredRegion = null;
        this.selectedMesh = null; // Filled mesh for selected region

        // Raycaster for click detection
        this.raycaster = new THREE.Raycaster();
        this.raycaster.params.Line.threshold = 0.5; // Increase threshold for easier line selection
        this.mouse = new THREE.Vector2();

        this.init();
        this.loadRegions();
    }

    init() {
        // Scene
        this.scene = new THREE.Scene();

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            45,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.z = 300;

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('globe-container').appendChild(this.renderer.domElement);

        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 150;
        this.controls.maxDistance = 500;
        this.controls.enablePan = false;
        this.controls.rotateSpeed = 0.5;
        this.controls.zoomSpeed = 0.8;

        // Create Globe
        this.createGlobe();

        // Add Lights
        this.addLights();

        // Add Stars Background
        this.addStars();

        // Event Listeners
        window.addEventListener('resize', () => this.onWindowResize());
        this.renderer.domElement.addEventListener('click', (e) => this.onMouseClick(e));
        this.renderer.domElement.addEventListener('mousemove', (e) => this.onMouseMove(e));

        // Close panel button
        document.getElementById('close-panel').addEventListener('click', () => {
            this.hideInfoPanel();
        });

        // Start animation
        this.animate();

        // Hide loading screen
        setTimeout(() => {
            document.getElementById('loading-screen').classList.add('hidden');
        }, 1000);
    }

    createGlobe() {
        // Earth Sphere
        const geometry = new THREE.SphereGeometry(100, 64, 64);

        // Custom shader material for day/night effect
        const material = new THREE.ShaderMaterial({
            uniforms: {
                sunDirection: { value: new THREE.Vector3(1, 0, 0.5).normalize() }
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;

                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 sunDirection;
                varying vec3 vNormal;
                varying vec3 vPosition;

                void main() {
                    // Base dark color
                    vec3 darkColor = vec3(0.05, 0.05, 0.08);
                    vec3 lightColor = vec3(0.15, 0.15, 0.2);

                    // Calculate lighting
                    float intensity = dot(vNormal, sunDirection);
                    intensity = max(intensity, 0.0);

                    // Mix colors based on light intensity
                    vec3 color = mix(darkColor, lightColor, intensity * 0.8);

                    // Add slight atmospheric effect
                    float atmosphere = pow(1.0 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
                    color += vec3(0.1, 0.15, 0.2) * atmosphere * 0.3;

                    gl_FragColor = vec4(color, 1.0);
                }
            `
        });

        this.globe = new THREE.Mesh(geometry, material);
        this.scene.add(this.globe);

        // Add atmosphere glow
        const atmosphereGeometry = new THREE.SphereGeometry(102, 64, 64);
        const atmosphereMaterial = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec3 vNormal;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vNormal;
                void main() {
                    float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
                    gl_FragColor = vec4(0.3, 0.6, 1.0, 1.0) * intensity;
                }
            `,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide,
            transparent: true
        });

        this.atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
        this.scene.add(this.atmosphere);

        // Add latitude/longitude grid
        this.addGrid();
    }

    addGrid() {
        const gridGroup = new THREE.Group();

        // Latitude lines
        for (let lat = -80; lat <= 80; lat += 20) {
            const curve = new THREE.EllipseCurve(
                0, 0,
                100, 100,
                0, 2 * Math.PI,
                false,
                0
            );
            const points = curve.getPoints(64);
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({
                color: 0x334455,
                transparent: true,
                opacity: 0.3
            });
            const line = new THREE.Line(geometry, material);
            line.rotation.x = (lat * Math.PI) / 180;
            gridGroup.add(line);
        }

        // Longitude lines
        for (let lon = 0; lon < 360; lon += 20) {
            const curve = new THREE.EllipseCurve(
                0, 0,
                100, 100,
                0, Math.PI,
                false,
                0
            );
            const points = curve.getPoints(32);
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({
                color: 0x334455,
                transparent: true,
                opacity: 0.3
            });
            const line = new THREE.Line(geometry, material);
            line.rotation.y = (lon * Math.PI) / 180;
            gridGroup.add(line);
        }

        this.globe.add(gridGroup);
    }

    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 3, 5);
        this.scene.add(directionalLight);
    }

    addStars() {
        const starsGeometry = new THREE.BufferGeometry();
        const starsMaterial = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.7,
            transparent: true,
            opacity: 0.8
        });

        const starsVertices = [];
        for (let i = 0; i < 10000; i++) {
            const x = (Math.random() - 0.5) * 2000;
            const y = (Math.random() - 0.5) * 2000;
            const z = (Math.random() - 0.5) * 2000;
            starsVertices.push(x, y, z);
        }

        starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
        const stars = new THREE.Points(starsGeometry, starsMaterial);
        this.scene.add(stars);
    }

    async loadRegions() {
        try {
            // Try to load from database first
            const response = await fetch('/api/regions');
            const regions = await response.json();

            if (regions.length > 0) {
                // Load regions from database
                console.log(`Loading ${regions.length} regions from database`);
                regions.forEach((region) => {
                    const geojson = JSON.parse(region.geojson_data);
                    const customData = region.custom_data ? JSON.parse(region.custom_data) : {};

                    this.countries.set(region.code, {
                        id: region.id,
                        name: region.name,
                        code: region.code,
                        type: region.region_type,
                        owner: region.owner,
                        geometry: geojson,
                        color: customData.color || '#66ffcc'
                    });

                    // Only create borders (lines), not filled meshes
                    this.createRegionBorders(geojson, region);
                });
            } else {
                // Fallback to external GeoJSON
                console.log('No regions in database, loading from external source...');
                await this.loadExternalCountries();
            }

            console.log(`Loaded ${this.countries.size} regions`);

        } catch (error) {
            console.error('Error loading regions:', error);
            // Fallback to external source
            await this.loadExternalCountries();
        }
    }

    async loadExternalCountries() {
        try {
            const response = await fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson');
            const data = await response.json();

            data.features.forEach((feature) => {
                const countryName = feature.properties.ADMIN || feature.properties.name;
                const countryCode = feature.properties.ISO_A3 || feature.properties.iso_a3;

                const regionData = {
                    name: countryName,
                    code: countryCode,
                    type: 'country',
                    geometry: feature.geometry,
                    color: '#66ffcc'
                };

                this.countries.set(countryCode, regionData);
                this.createRegionBorders(feature.geometry, regionData);
            });
        } catch (error) {
            console.error('Error loading external countries:', error);
        }
    }

    createRegionBorders(geometry, regionData) {
        if (!geometry || !geometry.coordinates) return;

        const processPolygon = (coords) => {
            if (!coords || coords.length < 2) return;

            const points3D = [];
            coords.forEach(coord => {
                const [lon, lat] = coord;
                const phi = (90 - lat) * (Math.PI / 180);
                const theta = (lon + 180) * (Math.PI / 180);

                const x = -100 * Math.sin(phi) * Math.cos(theta);
                const y = 100 * Math.cos(phi);
                const z = 100 * Math.sin(phi) * Math.sin(theta);

                points3D.push(new THREE.Vector3(x, y, z));
            });

            if (points3D.length < 2) return;

            // Create border line only
            const lineGeometry = new THREE.BufferGeometry().setFromPoints(points3D);
            const color = new THREE.Color(regionData.color || '#66ffcc');

            const lineMaterial = new THREE.LineBasicMaterial({
                color: color,
                transparent: true,
                opacity: 0.6,
                linewidth: 1
            });

            const line = new THREE.Line(lineGeometry, lineMaterial);
            line.userData = {
                regionId: regionData.id,
                regionCode: regionData.code,
                regionName: regionData.name,
                regionType: regionData.type,
                regionOwner: regionData.owner,
                regionColor: regionData.color,
                originalColor: color.getHex(),
                isRegionBorder: true,
                geometry: geometry // Store for later if we want to fill it
            };

            this.globe.add(line);
            this.regionBorders.push(line);
        };

        if (geometry.type === 'Polygon') {
            geometry.coordinates.forEach(ring => {
                processPolygon(ring);
            });
        } else if (geometry.type === 'MultiPolygon') {
            geometry.coordinates.forEach(polygon => {
                polygon.forEach(ring => {
                    processPolygon(ring);
                });
            });
        }
    }

    onMouseClick(event) {
        // Calculate mouse position in normalized device coordinates
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        // Update the raycaster
        this.raycaster.setFromCamera(this.mouse, this.camera);

        // Check for intersections with region borders
        const intersects = this.raycaster.intersectObjects(this.regionBorders);

        if (intersects.length > 0) {
            const clickedLine = intersects[0].object;
            this.selectRegion(clickedLine);
        } else {
            this.deselectRegion();
        }
    }

    onMouseMove(event) {
        // Only change cursor, don't do expensive raycasting on every move
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.regionBorders);

        if (intersects.length > 0) {
            this.renderer.domElement.style.cursor = 'pointer';
        } else {
            this.renderer.domElement.style.cursor = 'grab';
        }
    }

    selectRegion(borderLine) {
        // Deselect previous region
        if (this.selectedRegion && this.selectedRegion !== borderLine) {
            this.selectedRegion.material.color.setHex(this.selectedRegion.userData.originalColor);
            this.selectedRegion.material.opacity = 0.6;
        }

        // Remove previous filled mesh if exists
        if (this.selectedMesh) {
            this.globe.remove(this.selectedMesh);
            this.selectedMesh = null;
        }

        // Select new region
        this.selectedRegion = borderLine;
        this.selectedRegion.material.color.setHex(0xff4444); // Red highlight
        this.selectedRegion.material.opacity = 1.0;

        // Show info panel
        this.showInfoPanel(borderLine.userData);
    }

    deselectRegion() {
        if (this.selectedRegion) {
            this.selectedRegion.material.color.setHex(this.selectedRegion.userData.originalColor);
            this.selectedRegion.material.opacity = 0.6;
            this.selectedRegion = null;
        }

        if (this.selectedMesh) {
            this.globe.remove(this.selectedMesh);
            this.selectedMesh = null;
        }

        this.hideInfoPanel();
    }

    showInfoPanel(regionData) {
        const panel = document.getElementById('info-panel');
        document.getElementById('region-name').textContent = regionData.regionName || 'Unknown';
        document.getElementById('region-code').textContent = regionData.regionCode || '-';
        document.getElementById('region-type').textContent = regionData.regionType || 'country';
        document.getElementById('region-owner').textContent = regionData.regionOwner || 'None';
        document.getElementById('region-points').textContent = '-';

        panel.classList.remove('hidden');
    }

    hideInfoPanel() {
        const panel = document.getElementById('info-panel');
        panel.classList.add('hidden');
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize globe when page loads
document.addEventListener('DOMContentLoaded', () => {
    new InteractiveGlobe();
});
