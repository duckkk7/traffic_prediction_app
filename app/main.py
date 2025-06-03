from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.get_traffic_volume_endpoint.get_traffic_volume import router as traffic_router

# from app.get_traffic_volume_endpoint import get_traffic_volume
# from app.startup.load_models import load_traffic_model


app = FastAPI(title="Traffic Prediction")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(traffic_router)

# app.traffic_model = load_traffic_model()
# app.include_router(get_traffic_volume.router)