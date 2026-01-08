let userLocation = null;
let sosMap = null;
let userMarker = null;

function initSOSMap() {
    const defaultLocation = { lat: 20.5937, lng: 78.9629 };
    
    sosMap = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: defaultLocation,
        disableDefaultUI: true,
        zoomControl: true
    });
}

function init() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                
                document.getElementById('location-status').innerHTML = 
                    `✅ Location captured: ${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)}`;
                
                document.getElementById('map').style.display = 'block';
                document.getElementById('emergency-types').style.display = 'block';
                
                // Update map
                sosMap.setCenter({ lat: userLocation.latitude, lng: userLocation.longitude });
                
                userMarker = new google.maps.Marker({
                    position: { lat: userLocation.latitude, lng: userLocation.longitude },
                    map: sosMap,
                    title: 'Your Location',
                    icon: {
                        url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
                    }
                });
                
                // Watch for location updates
                navigator.geolocation.watchPosition(
                    (position) => {
                        userLocation = {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        };
                        userMarker.setPosition({ lat: userLocation.latitude, lng: userLocation.longitude });
                    },
                    (error) => console.error('Location watch failed:', error),
                    { enableHighAccuracy: true, timeout: 5000 }
                );
            },
            (error) => {
                document.getElementById('location-status').innerHTML = 
                    `❌ Error getting location: ${error.message}`;
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    } else {
        document.getElementById('location-status').innerHTML = 
            '❌ Geolocation not supported by this browser';
    }
}

async function triggerSOS(type) {
    if (!userLocation) {
        alert('Location not available. Please allow location access.');
        return;
    }
    
    try {
        const response = await fetch('/emergency/trigger', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: type,
                latitude: userLocation.latitude,
                longitude: userLocation.longitude
            })
        });
        
        if (response.ok) {
            alert('🚨 SOS triggered successfully! Redirecting to map...');
            const result = await response.json();
            window.location.href = `/map/${result.emergency_id}`;
        } else {
            alert('Failed to trigger SOS. Please try again.');
        }
    } catch (error) {
        console.error('SOS failed:', error);
        alert('Network error. Please try again.');
    }
}

// Initialize on page load
if (typeof google !== 'undefined') {
    initSOSMap();
}
init();