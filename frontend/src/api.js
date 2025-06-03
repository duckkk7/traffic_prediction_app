import axios from 'axios';

export async function getTrafficPrediction(routeCoords, datetimeISO) {
    const coordsPlain = routeCoords.map(routeCoords => [...routeCoords]);
    // console.log("coordsPlain:", JSON.stringify(coordsPlain));
    try {
        const response = await axios.post('http://localhost:8000/predict_traffic', {
            coords: coordsPlain,
            datetime: datetimeISO
        });
        const { route } = response.data;
        return route;

    } catch (error) {
        if (error.response) {
            // сервер ответил с ошибкой
            console.log(error.response.data.detail);
            throw new Error(`Ошибка сервера: ${error.response.data.detail || error.response.statusText}`);
        } else if (error.request) {
            // запрос отправлен, но ответа нет
            throw new Error('Сервер временно недоступен.');
        } else {
            // ошибка в настройке запроса
            throw new Error(`Ошибка запроса: ${error.message}`);
        }
    }
}








