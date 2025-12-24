let userLocation = null;

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
                document.getElementById('emergency-types').style.display = 'block';
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
        alert('🚨 SOS triggered successfully! Help is on the way.');
        window.location.href = '/';
    } else {
        alert('Failed to trigger SOS. Please try again.');
    }
}

// Initialize on page load
init();