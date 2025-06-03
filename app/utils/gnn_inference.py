import torch
import numpy as np
from app.utils.time_features import get_time_features


def predict_speed(model, x_map, edge_index, dt):
    """
    выполняет инференс по всей дорожной сети и возвращает словарь link_id => скорость (км/ч)
    """
    time_feat = get_time_features(dt)

    x_list = []
    lid_to_idx = {}
    for i, (lid, road_feat) in enumerate(x_map.items()):
        full_feat = torch.cat([road_feat, time_feat])  # объединяем road + time признаки
        x_list.append(full_feat)
        lid_to_idx[lid] = i

    x_tensor = torch.stack(x_list)

    model.eval()
    with torch.no_grad():
        y_pred = model(x_tensor, edge_index) * 120.0  # денормализация

    # возвращаем предсказания: link_id => скорость
    pred_dict = {lid: float(y_pred[idx]) for lid, idx in lid_to_idx.items()}
    return pred_dict

