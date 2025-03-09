function initMap() {
    let chosen = null;

    const button = document.querySelector("header button");
    const coords = document.querySelector("#coords");
    button.disabled = true;

    button.addEventListener("click", function(ev) {
        if (button.disabled) {
            return;
        }

        if (grecaptcha.getResponse() === "") {
            alert("Please complete the captcha");
            return;
        }

        button.disabled = true;

        const body = {
            coords: chosen,
            captcha: grecaptcha.getResponse()
        };

        fetch("/report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }).then(resp => {
            return resp.json();
        }).then(data => {
            alert(data.message);
        }).catch(err => {
            alert("An error occurred while submitting the report. See the console for details.");
            console.error(err);
        }).finally(() => {
            grecaptcha.reset();
            button.disabled = false;
        })
    });

    function coordinatesSet(lat, lon) {
        lat = lat.toFixed(6);
        lon = lon.toFixed(6);
        chosen = { lat, lon };
        coords.innerText = `${lat}, ${lon}`;
        coords.className = '';
        button.disabled = false;
    }

    let marker = null;

    const mapOptions = {
        center: { lat: 0, lng: 0 },
        zoom: 2,
        zoomControl: true,
        scaleControl: true,
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.DEFAULT,
            mapTypeIds: ['hybrid', 'roadmap', 'satellite']
        },
        streetViewControl: false,
        fullscreenControl: false,
        rotateControl: true
    };

    const mapContainer = document.querySelector('main');
    const map = new google.maps.Map(mapContainer, mapOptions);

    map.addListener('click', function(event) {
        const position = event.latLng;

        if (marker) {
            marker.setPosition(position);
        } else {
            marker = new google.maps.Marker({
                position,
                map,
                icon: {
                    url: 'https://maps.gstatic.com/tactile/omnibox/search-nearby-1x.png',
                    origin: new google.maps.Point(42, 0),
                    size: new google.maps.Size(21, 21)
                }
            });
        }

        coordinatesSet(position.lat(), position.lng());
    });
}
