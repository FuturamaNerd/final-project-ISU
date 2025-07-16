// static/script.js

import { NewsEvent, NewsAPIEvent, GDELTEvent, addNewsApiLayer } from './newsEvents.js';

// Continent bounding boxes for determining continent from coordinates
const CONTINENT_BOUNDS = {
    'Americas': { lat_min: -56, lat_max: 84, lon_min: -180, lon_max: -34 },
    'Africa': { lat_min: -35, lat_max: 37, lon_min: -18, lon_max: 51 },
    'Asia': { lat_min: -10, lat_max: 81, lon_min: 26, lon_max: 180 },
    'Europe': { lat_min: 36, lat_max: 81, lon_min: -10, lon_max: 40 },
    'Oceania': { lat_min: -56, lat_max: -10, lon_min: 110, lon_max: 180 }
};

// Continent color scheme
const CONTINENT_COLORS = {
    'Americas': '#FF0000', // Red
    'Africa': '#00FF00',   // Green
    'Asia': '#000000',     // Black
    'Europe': '#FFD700',   // Gold
    'Oceania': '#0000FF'   // Blue
};

// Function to determine continent from coordinates
function getContinentFromCoordinates(lat, lon) {
    for (const [continent, bounds] of Object.entries(CONTINENT_BOUNDS)) {
        if (lat >= bounds.lat_min && lat <= bounds.lat_max && 
            lon >= bounds.lon_min && lon <= bounds.lon_max) {
            return continent;
        }
    }
    return 'Unknown';
}

// Function to get marker color based on continent
function getMarkerColor(continent) {
    return CONTINENT_COLORS[continent] || '#808080'; // Default to gray for unknown
}

// Function to create map legend
function createLegend() {
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '10px';
        div.style.borderRadius = '5px';
        div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
        div.style.fontSize = '12px';
        div.style.minWidth = '200px';
        
        div.innerHTML = `
            <h6 style="margin: 0 0 10px 0; text-align: center;"><strong>Map Legend</strong></h6>
            <div style="margin-bottom: 15px;">
            <div style="margin-bottom: 15px;">
                <h6 style="margin: 0 0 5px 0; font-size: 11px;"><strong>Data Sources:</strong></h6>
                <div style="display: flex; align-items: center; margin: 2px 0;">
                    <div style="width: 20px; height: 20px; background-color: #007bff; border-radius: 50%; margin-right: 8px; opacity: 0.3;"></div>
                    <span>NewsAPI (Large circles - imprecise location)</span>
                </div>
                <div style="display: flex; align-items: center; margin: 2px 0;">
                    <div style="width: 8px; height: 8px; background-color: #28a745; border-radius: 50%; margin-right: 8px;"></div>
                    <span>GDELT (Small dots - precise location)</span>
                </div>
            </div>
            <div style="margin-bottom: 10px;">
                <small style="color: #666; font-style: italic;">Credit to SimpleMaps and Google for coordinate data</small>
            </div>
        `;
        
        return div;
    };
    
    return legend;
}

document.addEventListener('DOMContentLoaded', function() {
    const map = initializeMap('map', {
        center: [20, 0], //map initialization (centered on africa)
        zoom: 2
    });

    // Add legend to map
    const legend = createLegend();
    legend.addTo(map);

    // Fetch NewsAPI data from backend endpoint
    fetch('/api/newsapi')
        .then(response => response.json())
        .then(data => {
            data.events.forEach(eventData => {
                // Only add if both latitude and longitude are present
                if (eventData.latitude != null && eventData.longitude != null) {
                    const continent = getContinentFromCoordinates(eventData.latitude, eventData.longitude);
                    const color = getMarkerColor(continent);
                    
                    // Use large circles for NewsAPI (imprecise location data)
                    L.circle([eventData.latitude, eventData.longitude], {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.3,
                        radius: 150000, // Large radius (150km) to show imprecise location
                        weight: 2
                    }).addTo(map)
                    .bindPopup(`
                        <div style="min-width: 250px;">
                            <b>${eventData.title || 'NewsAPI Article'}</b><br>
                            <small>🌍 ${continent}</small><br>
                            <small>📰 Source: ${eventData.source?.name || 'Unknown'}</small><br>
                            <small>📍 Imprecise location (large circle)</small><br>
                            ${eventData.url ? `<a href="${eventData.url}" target="_blank" style="color: #007bff; text-decoration: none;">📖 Read Article</a>` : ''}
                        </div>
                    `);
                }
            });
        });

    // Fetch events from backend endpoint
    fetch('/api/events/all')
        .then(response => response.json())
        .then(data => {
            data.events.forEach(eventData => {
                if (eventData.data_source === 'gdelt') {
                    // Only add if both latitude and longitude are present AND location_name is not empty
                    if (eventData.latitude != null && eventData.longitude != null && 
                        eventData.location_name && eventData.location_name.trim() !== '') {
                        
                        const continent = getContinentFromCoordinates(eventData.latitude, eventData.longitude);
                        const color = getMarkerColor(continent);
                        
                        // Format the date (convert YYYYMMDD to readable format)
                        let formattedDate = 'Unknown';
                        if (eventData.date && eventData.date.length === 8) {
                            const year = eventData.date.substring(0, 4);
                            const month = eventData.date.substring(4, 6);
                            const day = eventData.date.substring(6, 8);
                            formattedDate = `${year}-${month}-${day}`;
                        }
                        
                        // Use small dots for GDELT (precise location data)
                        L.circle([eventData.latitude, eventData.longitude], {
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.8,
                            radius: 10000, // Small radius (10km) to show precise location
                            weight: 1
                        }).addTo(map)
                        .bindPopup(`
                            <div style="min-width: 250px;">
                                <b>${eventData.scraped_title || eventData.translated_title || eventData.location_name}</b><br>
                                <small>🌍 ${continent}</small><br>
                                <small>📅 ${formattedDate}</small><br>
                                <small>🔢 Event: ${eventData.event_code || 'Unknown'}</small><br>
                                <small>👤 Actor 1: ${eventData.actor1_name || 'Unknown'}</small><br>
                                ${eventData.actor2_name ? `<small>👥 Actor 2: ${eventData.actor2_name}</small><br>` : ''}
                                <small>📊 Goldstein: ${eventData.goldstein || 'Unknown'}</small><br>
                                <small>📍 Precise location (small dot)</small><br>
                                ${eventData.source_url ? `<a href="${eventData.source_url}" target="_blank" style="color: #007bff; text-decoration: none;">📰 Read Article</a>` : ''}
                            </div>
                        `);
                    }
                }
            });
        });

    // todo add other data layers (small dots, standard markers, etc.) here...
});