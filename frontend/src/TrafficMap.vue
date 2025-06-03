<template>
  <div id="map" ref="mapContainer" class="map-container"></div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";

let placingMarkers;
let routeLayer;

export default {
  name: 'TrafficMap',
  emits: ['address-selected', 'route-built'],
  props: {
    enableMarkerPlacement: Boolean,
  },
  data() {
    return {
      startMarker: null,
      endMarker: null,
      startAddress: '',
      endAddress: '',
      markerCount: 0,
      customIcon: L.icon({
        iconUrl:
            "https://masterprintspb.ru/wp-content/uploads/2014/10/Map-Marker-PNG-File.png",
        iconSize: [32, 32],
        iconAnchor: [16, 32],
      }),
    };
  },


  watch: {
    enableMarkerPlacement(val) {
      // console.log("ИЗ ВОТЧЕРА enableMarkerPlacement =", val);
      placingMarkers = val;
      // console.log("ИЗ ВОТЧЕРА placingMarkers =", val);

      this.markerCount = 0;
      this.clearMarkers();
      this.clearRoute();

      if (val)
        document.body.classList.add("marker-cursor");
      else
        document.body.classList.remove("marker-cursor");
    }
  },

  mounted() {
    this.initMap();
    // console.log("mounted, container =", this.$refs.mapContainer);
    // console.log("mounted, leaflet id =", this.$refs.mapContainer._leaflet_id);
  },

  methods: {
    initMap() {
      const container = this.$refs.mapContainer;
      this.map = L.map(container).setView([39.9042, 116.4074], 12)
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(this.map);
      // console.log(this.map._layers)
      this.map.on("click", this.onMapClick);
      // console.log("initMap: click listener attached");
    },

    onMapClick(e) {
      console.log("click:", {placing: placingMarkers, count: this.markerCount});
      if (!placingMarkers || this.markerCount >= 2) {
        console.log("ignored");
        return;
      }

      const {lat, lng} = e.latlng;
      // console.log("onMapClick: placing marker at", lat, lng);
      const marker = L.marker([lat, lng], {icon: this.customIcon}).addTo(
          this.map
      );
      // console.log("onMapClick: marker added", marker);
      // console.log(this.map._layers)

      const type = this.markerCount === 0 ? "start" : "end";
      if (type === "start")
        this.startMarker = marker;
      else
        this.endMarker = marker;

      this.reverseGeocode(lat, lng, type);

      this.markerCount += 1;
      // console.log("onMapClick: markerCount->", this.markerCount);

      if (this.markerCount === 2) {
        // console.log("onMapClick: both markers placed -== drawRoute");
        //  cраз строим маршрут и сбрасываем курсор
        document.body.classList.remove("marker-cursor");
        this.drawRoute();
      }
    },

    clearMarkers() {
      // console.log("clearMarkers");
      if (this.startMarker) this.map.removeLayer(this.startMarker);
      if (this.endMarker) this.map.removeLayer(this.endMarker);
      this.startMarker = null;
      this.endMarker = null;
    },

    clearRoute() {
      console.log("clearRoute", routeLayer);
      if (routeLayer) {
        this.map.removeLayer(routeLayer);
      }
      routeLayer = null;
    },

    async reverseGeocode(lat, lon, type) {
      console.log("reverseGeocode:", {type, lat, lon});
      try {
        const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
        );
        const data = await res.json();
        const address = data.display_name || `${lat}, ${lon}`;
        // console.log("reverseGeocode: address ", address);
        if (this.markerCount === 1) {
          this.$emit('address-selected', {type: 'start', address: address});
          // console.log('addr emited 1')
        } else {
          this.$emit('address-selected', {type: 'end', address: address})
          // console.log('addr emited 2')
        }
      } catch (err) {
        console.error("Geocoding error:", err);
        this.$emit('address-selected', {
          type,
          address: `${lat}, ${lon}`,
          lat,
          lon,
        });
      }
    },

    async drawRoute() {
      console.log("drawRoute");
      if (!this.startMarker || !this.endMarker) return;
      const a = this.startMarker.getLatLng();
      const b = this.endMarker.getLatLng();
      const url = `https://router.project-osrm.org/route/v1/driving/` +
          `${a.lng},${a.lat};${b.lng},${b.lat}?overview=full&geometries=geojson`;
      console.log("drawRoute: fetch", url);
      try {
        const res = await fetch(url);
        const json = await res.json();
        console.log("drawRoute: response", json);
        const coords = json.routes[0].geometry.coordinates;
        this.$emit('route-built', coords)
        const latlngs = coords.map(([lng, lat]) => [lat, lng]);
        routeLayer = L.polyline(latlngs, {
          color: "blue",
          weight: 4,
        }).addTo(this.map);

        // this.predictedLayers.push(routeLayer)
        // polylines.push(polyline);

        console.log("drawRoute: polyline added");
        console.log(this.map._layers)
      } catch (err) {
        console.error("Routing error:", err);
      }
    },


    async renderPredictedRoute(routePoints) {
      this.clearRoute();
      if (!routePoints || routePoints.length < 2) return;
      const latlngs = routePoints.map(p => [p.coord[1], p.coord[0]]);
      const segments = [];
      for (let i = 1; i < latlngs.length; i++) {
        const prev = latlngs[i - 1];
        const curr = latlngs[i];

        const polyline = L.polyline([prev, curr], {
          color: routePoints[i].color,
          weight: 6,
          dashArray: routePoints[i].approx ? '10,10' : null,
        }).addTo(this.map);
        polyline.bindPopup(`Скорость: ${routePoints[i].speed?.toFixed(1) ?? 'н/д'} км/ч\n
        Экстраполяция: ${routePoints[i].approx ? 'Да' : 'Нет'}`);
        segments.push(polyline);
      }
      routeLayer = L.layerGroup(segments).addTo(this.map);
    }
  },
};
</script>

<style>
.map-container {
  position: absolute;
  top: 0;
  left: 300px;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: all !important;
}

/* при включенном режиме курсор меняется на крестик */
.marker-cursor * {
  cursor: crosshair !important;
}
</style>
