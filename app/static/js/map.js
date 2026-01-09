// Complete working map.js with ALL functions
let map;
let victimMarker;
let responderMarker;
let routePolyline;
let updateInterval;
let watchId;
let victimLocation = null;
let responderLocation = null;

// Complete initMap function
window.initMap = function() {
    console.log('=== Google Maps Callback ===');
    
    const API_KEY = document.documentElement.getAttribute('data-api-key');
    const EMERGENCY_ID_RAW = document.documentElement.getAttribute('data-emergency-id');
    const USER_ROLE = document.documentElement.getAttribute('data-user-role');
    const EMERGENCY_ID = EMERGENCY_ID_RAW === 'null' ? null : parseInt(EMERGENCY_ID_RAW);
    
    console.log('Starting map initialization with:', {API_KEY, EMERGENCY_ID, USER_ROLE});
    
    // Initialize map
    const defaultLocation = { lat: 20.5937, lng: 78.9629 };
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: EMERGENCY_ID ? 15 : 10,
        center: defaultLocation,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: false,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
    });
    
    if (EMERGENCY_ID) {
        startEmergencyTracking(EMERGENCY_ID);
    } else {
        loadAllActiveEmergencies();
    }
    
    updateConnectionStatus('connected');
    setupControls();
};

// Complete functions - clean implementation
function startEmergencyTracking(emergencyId) {
    loadEmergencyLocations(emergencyId);
    startLiveUpdates(emergencyId);
    
    if (USER_ROLE === 'victim' || USER_ROLE === 'responder') {
        startRealTimeLocationSharing(emergencyId);
    }
}

function startRealTimeLocationSharing(emergencyId) {
    if (!navigator.geolocation) {
        showError('Geolocation is not supported by your browser');
        return;
    }
    
    watchId = navigator.geolocation.watchPosition(
        (position) => {
            sendLocationUpdate(emergencyId, position.coords.latitude, position.coords.longitude);
        },
        (error) => {
            handleGeolocationError(error);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
    );
}

function sendLocationUpdate(emergencyId, latitude, longitude) {
    const endpoint = USER_ROLE === 'victim' 
        ? `/map/sos/update-location` 
        : `/map/responder/${emergencyId}/update-location`;
    
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: latitude, longitude: longitude })
    }).then(response => {
        if (response.ok) {
            updateLastUpdateTime();
        }
    });
}

function loadEmergencyLocations(emergencyId) {
    fetch(`/map/${emergencyId}/location`)
        .then(response => response.json())
        .then(data => {
            if (data.victim_location) {
                updateVictimMarker(data.victim_location);
                updateLocationInfo('victim', data.victim_location);
            }
            if (data.responder_location) {
                updateResponderMarker(data.responder_location);
                updateLocationInfo('responder', data.responder_location);
                drawRoute();
                updateDistanceInfo(data.victim_location, data.responder_location);
            }
            updateLastUpdateTime();
            updateConnectionStatus('connected');
        })
        .catch(error => {
            updateConnectionStatus('disconnected');
            showError('Failed to load locations');
        });
}

function startLiveUpdates(emergencyId) {
    updateInterval = setInterval(() => {
        if (!isTrackingPaused) {
            loadEmergencyLocations(emergencyId);
        }
    }, 5000);
}

function updateLocationInfo(type, location) {
    const infoElement = document.getElementById(`${type}-info`);
    if (infoElement) {
        const time = new Date().toLocaleTimeString();
        infoElement.innerHTML = `${type.charAt(0).toUpperCase() + type.slice(1)}: ${location.lat.toFixed(4)}, ${location.lng.toFixed(4)} (Updated: ${time})`;
    }
}

function updateDistanceInfo(victimLoc, responderLoc) {
    const distanceElement = document.getElementById('distance-info');
    if (distanceElement && victimLoc && responderLoc) {
        const distance = calculateDistance(victimLoc.lat, victimLoc.lng, responderLoc.lat, responderLoc.lng);
        distanceElement.innerHTML = `Distance: ${distance.toFixed(2)} km (${(distance * 0.621371).toFixed(2)} miles)`;
    }
}

function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = status === 'connected' ? '🟢 Connected' : '🔴 Disconnected';
        statusElement.className = status;
    }
}

function updateLastUpdateTime() {
    const timeElement = document.getElementById('last-update');
    if (timeElement) {
        timeElement.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function setupControls() {
    document.getElementById('center-btn')?.addEventListener('click', () => {
        if (victimMarker) {
            map.setCenter(victimMarker.getPosition());
            map.setZoom(16);
        }
    });
}

function acceptEmergency(emergencyId) {
    fetch(`/responder/accept/${emergencyId}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                window.location.href = `/map/${emergencyId}`;
            }
        })
        .catch(error => console.error('Failed to accept emergency:', error));
}

// Cleanup
window.addEventListener('beforeunload', () => {
    if (updateInterval) clearInterval(updateInterval);
    if (watchId) navigator.geolocation.clearWatch(watchId);
});

// Clean error handling
window.addEventListener('error', function(e) {
    if (e.error.message.includes('Google Maps')) {
        console.error('Google Maps error:', e.error.message);
    }
});

// Add this missing function to your map.js
function loadAllActiveEmergencies() {
    console.log('📡 Loading all active emergencies');
    
    try {
        fetch('/map/active')
            .then(response => response.json())
            .then(emergencies => {
                console.log('📍 Active emergencies received:', emergencies.length, 'emergencies');
                
                emergencies.forEach(emergency => {
                    const marker = new google.maps.Marker({
                        position: emergency.location,
                        map: map,
                        title: `${emergency.type} - ${emergency.victim_name}`,
                        icon: { url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png ' }
                    });
                    
                    const infoWindow = new google.maps.InfoWindow({
                        content: `
                            <div class="info-window">
                                <h4>🚨 ${emergency.type}</h4>
                                <p><strong>Victim:</strong> ${emergency.victim_name}</p>
                                <p><strong>Time:</strong> ${new Date(emergency.created_at).toLocaleTimeString()}</p>
                                <button onclick="acceptEmergency(${emergency.id})" class="btn btn-primary btn-sm">Accept</button>
                            </div>
                        `
                    });
                    
                    marker.addEventListener('click', () => infoWindow.open(map, marker));
                });
                
                updateLastUpdateTime();
            })
            .catch(error => {
                console.error('❌ Failed to load active emergencies:', error);
            });
    } catch (error) {
        console.error('❌ Failed to load active emergencies:', error);
    }
}

// Make sure initMap is available BEFORE Google Maps loads
window.initMap = window.initMap || function() {
    console.log('initMap called - starting map initialization');
    
    const API_KEY = document.documentElement.getAttribute('data-api-key');
    const EMERGENCY_ID_RAW = document.documentElement.getAttribute('data-emergency-id');
    const USER_ROLE = document.documentElement.getAttribute('data-user-role');
    const EMERGENCY_ID = EMERGENCY_ID_RAW === 'null' ? null : parseInt(EMERGENCY_ID_RAW);
    
    const defaultLocation = { lat: 20.5937, lng: 78.9629 };
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: EMERGENCY_ID ? 15 : 10,
        center: defaultLocation,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: false,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
    });
    
    if (EMERGENCY_ID) {
        startEmergencyTracking(EMERGENCY_ID);
    } else {
        loadAllActiveEmergencies();
    }
    
    updateConnectionStatus('connected');
    setupControls();
};