function initializeMap(mapContainerId, options = {}) {
    // Leaflet.js
    const map = L.map(mapContainerId).setView(
        options.center || [0, 0],
        options.zoom || 2
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    return map;
}

// Export for use in other scripts
window.initializeMap = initializeMap;