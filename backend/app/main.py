from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.get_traffic_volume_endpoint import get_traffic_volume
from app.startup.load_models import load_traffic_model

app = FastAPI()

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


app.traffic_model = load_traffic_model()

app.include_router(get_traffic_volume.router)
