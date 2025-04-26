from fastapi import APIRouter, Request

from .shemas import TrafficRequest, TrafficResponse

import pandas as pd

router = APIRouter(
    prefix="/traffic"
)


@router.post("/volume")
async def get_traffic_prediction(request: Request, traffic_request: TrafficRequest):

    traffic_model = request.app.state.traffic_model

    feature_space = {
        'rain_1h': [traffic_request.rain],
        'snow_1h': [traffic_request.snow],
        'temp': [traffic_request.temp],
        'clouds_all': [traffic_request.cloud],
        'hour': [traffic_request.hour],
        'day': [traffic_request.day],
        'month': [traffic_request.month]
    }

    transformed_feature_space = pd.DataFrame.from_dict(feature_space)

    traffic_volume = traffic_model.predict(transformed_feature_space)

    return TrafficResponse(traffic_volume=traffic_volume)
