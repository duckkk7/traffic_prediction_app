from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime


class RouteRequest(BaseModel):
    coords: List[List[float]]  # [[lat, lon], ]
    datetime: str

    @field_validator('datetime')
    def validate_datetime(cls, v):
        if v is None:
            raise ValueError("Поле 'datetime' не может быть пустым или отсутствовать")
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            future_date = datetime(2026, 5, 5, 15, 15)
            min_date = datetime(2025, 1, 1)
            if dt < min_date or dt > future_date:
                raise ValueError(f"Дата должна быть в диапазоне с {min_date.date()} по {future_date.date()}")
            return v
        except ValueError as e:
            raise ValueError("Неверный формат даты. Используйте ISO 8601 (например, '2025-05-01T14:00:00').")

    @field_validator('coords', mode='after')
    def validate_coords(cls, v):
        if not isinstance(v, list):
            raise ValueError(f"Поле 'coords' должно быть списком, получено: {type(v).__name__}")
        for i, coord in enumerate(v):
            if not isinstance(coord, list):
                raise ValueError(f"Элемент {i} в 'coords' должен быть списком, получено: {type(coord).__name__}")
        for coord in v:
            if len(coord) != 2:
                raise ValueError("Каждая координата должна содержать два значения: [долгота, широта]")
            lon, lat = coord
            if not (-180 <= lon <= 180):
                raise ValueError(f"Долгота ({lon}) должна быть в диапазоне [-180, 180]")
            if not (-90 <= lat <= 90):
                raise ValueError(f"Широта ({lat}) должна быть в диапазоне [-90, 90]")
        return v


class PredictionResponse(BaseModel):
    route: List[dict]
