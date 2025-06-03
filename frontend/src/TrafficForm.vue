<template>
  <div class="app-container">
    <div class="sidebar">
      <h2>Прогноз пробок</h2>
      <form @submit.prevent>
        <div class="mb-3">
          <label for="date" class="form-label">Дата</label>
          <input type="date" id="date" v-model="date" class="form-control" required />
        </div>

        <div class="mb-3">
          <label for="time" class="form-label">Время</label>
          <input type="time" id="time" v-model="time" class="form-control" required />
        </div>

        <div class="mb-3">
          <label for="start" class="form-label">Начало маршрута</label>
          <input type="text" id="start" v-model="startAddress" class="form-control" placeholder="Начало маршрута" />
        </div>

        <div class="mb-3">
          <label for="end" class="form-label">Конец маршрута</label>
          <input type="text" id="end" v-model="endAddress" class="form-control" placeholder="Конец маршрута" />
        </div>

        <button
            type="button"
            class="btn btn-secondary w-100 mb-3"
            @click="placeMarker"
        >
          Поставить маркеры
        </button>

        <button
            type="button"
            class="btn btn-primary w-100"
            :disabled="!canSubmit"
            @click="getPrediction"
        >
          Получить прогноз
        </button>
      </form>
    </div>

    <TrafficMap ref="mapRef"
        :enableMarkerPlacement="placingMarkers"
        @address-selected="handleAddressSelected"
        @route-built="handleRoute"
    />

    <div v-if="errorMessage" class="modal-overlay">
      <div class="custom-modal-content">
        <h3>Ошибка</h3>
        <p>{{ errorMessage }}</p>
        <button class="btn btn-secondary" @click="errorMessage = ''">Закрыть</button>
      </div>
    </div>

  </div>
</template>

<script>
import TrafficMap from "./TrafficMap.vue";
import { getTrafficPrediction } from "@/api";

export default {
  components: { TrafficMap },

  data() {
    return {
      startAddress: '',
      endAddress: '',
      routeCoords: null,
      date: "",
      time: "",
      selectedArea: null,
      placingMarkers: false,
      errorMessage: '',
    }
  },

  computed: {
    canSubmit() {
      return (
          this.date &&
          this.time &&
          this.startAddress &&
          this.endAddress
      );
    }
  },

  methods: {
    placeMarker() {
      this.placingMarkers = !this.placingMarkers;
      console.log("placingMarkers = ", this.placingMarkers);
    },

    handleAddressSelected(payload) {
      if (payload.type === 'start') {
        this.startAddress = payload.address
      } else if (payload.type === 'end') {
        this.endAddress = payload.address
      }
    },

    handleRoute(coords) {
      this.routeCoords = coords;
    },

    async getPrediction() {
      const datetime = `${this.date}T${this.time}:00`;
      try {
        const route = await getTrafficPrediction(this.routeCoords, datetime);
        console.log('POST sent')

        await this.$refs.mapRef.renderPredictedRoute(route)
        this.errorMessage = ''; // очищаем ошибку при успешном запросе
      } catch (err) {
        console.error("Ошибка прогноза:", err);
        this.errorMessage = err.message || 'Произошла неизвестная ошибка при получении прогноза.';
      }
    }
  },
};
</script>

<style>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  height: 100%;
  flex-shrink: 0;
  overflow-y: auto;

  background: #212529;
  color: white;
  padding: 20px;

  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
}

.sidebar h2 {
  text-align: center;
  margin-bottom: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.custom-modal-content {
  background: white;
  color: black;
  padding: 20px;
  border-radius: 5px;
  width: 30%;
  text-align: center;
}

.modal-content h3 {
  margin-bottom: 15px;
  color: #dc3545;
}

.modal-content p {
  margin-bottom: 20px;
}

.modal-content .btn {
  padding: 10px 20px;
}
</style>
