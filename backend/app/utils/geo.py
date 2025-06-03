from typing import List, Tuple
import pandas as pd
from scipy.spatial import KDTree
import numpy as np
from pyproj import Transformer
from collections import defaultdict


def to_mercator(lon: float, lat: float) -> Tuple[float, float]:
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    return transformer.transform(lon, lat)


# находим все link_id находящиеся в пределах max_dist_meters (100м) от маршрута (GPS-точек)
# используем проекцию меркатора и KDTree в метрах
def get_nearest_links(
        coords: List[Tuple[float, float]],
        tree: KDTree,
        link_gps_df: pd.DataFrame,
        max_dist_meters: float = 100.0) -> List[int]:
    if not coords:
        return []

    # преобразуем маршрут в метры
    mercator_coords = [to_mercator(lon, lat) for lon, lat in coords]  # lat/lon в lon/lat

    # дерево точек уже должен быть построен в метрах
    idx_lists = tree.query_ball_point(mercator_coords, r=max_dist_meters)
    flat_idxs = [i for sublist in idx_lists for i in sublist]
    if not flat_idxs:
        return []

    nearest_links = link_gps_df.iloc[flat_idxs]["link_id"].tolist()
    return list(set(nearest_links))


# строим словарь link_id - соседи (по edge_index)
def build_link_neighbors(edge_index_tensor, link_ids):
    neighbors_dict = defaultdict(set)
    edge_index_np = edge_index_tensor.cpu().numpy()
    for src_idx, dst_idx in zip(edge_index_np[0], edge_index_np[1]):
        src_lid = link_ids[src_idx]
        dst_lid = link_ids[dst_idx]
        neighbors_dict[src_lid].add(dst_lid)
        neighbors_dict[dst_lid].add(src_lid)
    return neighbors_dict


#  возвращаем до k соседей link_id из заранее построенного neighbors_dict
def get_k_neighbours_via_edge_index(link_id: int, neighbors_dict: dict, k: int = 5) -> list:
    if link_id not in neighbors_dict:
        return []
    neighbors = list(neighbors_dict[link_id])
    return neighbors[:k]


# экстраполируем скорость для неизвестного link_id на основе его соседей из neighbors_dict
def extrapolate_speed(
        lid: int,
        pred_dict: dict,
        neighbors_dict: dict) -> tuple[float, bool]:
    if lid not in neighbors_dict:
        return None, False
    neighbors = neighbors_dict[lid]
    known_speeds = [pred_dict[n] for n in neighbors if n in pred_dict]
    if known_speeds:
        return float(np.mean(known_speeds)), True
    return None, False


