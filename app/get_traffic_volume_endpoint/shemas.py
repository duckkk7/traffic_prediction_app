from pydantic import BaseModel


class TrafficRequest(BaseModel):
    rain: float
    snow: float
    temp: float
    cloud: float
    hour: float
    day: int
    month: int


class TrafficResponse(BaseModel):
    traffic_volume: float
