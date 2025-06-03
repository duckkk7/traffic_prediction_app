from fastapi import APIRouter, HTTPException
from datetime import datetime

from .schemas import RouteRequest, PredictionResponse
from scipy.spatial import KDTree
from app.utils.geo import to_mercator
import numpy as np

from app.startup.load_models import tree, link_gps_df, load_all
from app.utils.geo import get_nearest_links, extrapolate_speed
from app.utils.congestion import classify_congestion
from app.utils.gnn_inference import predict_speed
from app.utils.geo import build_link_neighbors
from pyproj import Transformer

transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
model, x_map, edge_index, link_ids = load_all()
neighbors_dict = build_link_neighbors(edge_index, link_ids)


router = APIRouter()


@router.post("/predict_traffic", response_model=PredictionResponse)
async def predict_traffic(req: RouteRequest):
    # 1. получаем ближайшие link_id по координатам маршрута
    coords = [tuple(pt) for pt in req.coords]
    nearest_links = get_nearest_links(coords, tree, link_gps_df)
    if not nearest_links:
        raise HTTPException(400, "Маршрут не пересекает известных сегментов (link_id)")

    # 2. получаем временные признаки (дальше)
    dt = datetime.fromisoformat(req.datetime)

    # 3. выполняем предсказание скорости по всей сети (GNN-инференс)
    pred_dict = predict_speed(model, x_map, edge_index, dt)

    # 4. построим KDTree по центроидам link_id, по которым есть предсказания
    gps_coords = link_gps_df[link_gps_df["link_id"].isin(pred_dict.keys())]
    lid_to_coord = gps_coords.groupby("link_id")[["lat", "lon"]].mean().reset_index()
    coord_array = lid_to_coord[["lon", "lat"]].values
    lid_list = lid_to_coord["link_id"].tolist()

    lons, lats = coord_array[:, 0], coord_array[:, 1]
    mx, my = transformer.transform(lons.tolist(), lats.tolist())
    lid_coords_merc = list(zip(mx, my))

    lid_tree = KDTree(lid_coords_merc)

    # обрабатываем каждую координату маршрута
    # деалем обратную операцию операции 1. т.е. теперь строим дерево по link_id и ищем для них ближайшие точки
    route = []
    for lon, lat in req.coords:
        mx, my = to_mercator(lon, lat)
        dist, idx = lid_tree.query((mx, my), distance_upper_bound=100)

        if np.isinf(dist) or idx >= len(lid_list):
            avg_speed = float(np.mean(list(pred_dict.values()))) if pred_dict else None
            level, color = classify_congestion(avg_speed)
            route.append({
                "coord": [lon, lat],
                "speed": avg_speed,
                "color": color,
                "approx": True
            })
            continue
        lid = lid_list[idx]
        if lid in pred_dict:
            speed = pred_dict[lid]
            approx = False
        else:
            speed, approx = extrapolate_speed(lid, pred_dict, neighbors_dict)
        level, color = classify_congestion(speed)
        route.append({
            "coord": [lon, lat],
            "speed": float(speed),
            "color": color,
            "approx": approx
        })
    return {"route": route}


