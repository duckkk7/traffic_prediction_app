import pickle
import pandas as pd
from scipy.spatial import KDTree
from pyproj import Transformer
import torch
from app.models.model import TrafficGNN


link_gps_df = pd.read_csv("data/link_gps.csv", sep='\t',
                          header=None, names=["link_id", "lon", "lat"])
transformer = Transformer.from_crs("epsg:4326", "epsg:3857",
                                   always_xy=True)
link_gps_df[["mercator_x", "mercator_y"]] = link_gps_df.apply(
    lambda row: pd.Series(transformer.transform(row["lon"], row["lat"])), axis=1)
coords = list(zip(link_gps_df["mercator_x"], link_gps_df["mercator_y"]))
tree = KDTree(coords)


def get_traffic_model(model_path: str = "app/models/traffic_gnn_model.pt",
                      in_channels: int = 21,
                      hidden_channels: int = 64):
    model = TrafficGNN(in_channels=in_channels, hidden_channels=hidden_channels)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    return model


def load_pickle(path: str):
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_all(model_path='app/models/traffic_gnn_model.pt',
             xmap_path='app/models/x_map.pkl',
             lid_path='app/models/link_ids.pkl',
             in_channels=21,
             hidden_channels=64):
    model = get_traffic_model(model_path, in_channels, hidden_channels)
    x_map = load_pickle(xmap_path)
    edge_index = torch.load("app/models/edge_index.pt", map_location='cpu')
    link_ids = load_pickle(lid_path)
    return model, x_map, edge_index, link_ids
