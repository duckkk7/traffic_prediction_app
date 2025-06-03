import numpy as np
import torch


def get_time_features(dt):
    hour = dt.hour + dt.minute / 60.0
    day_of_week = dt.weekday()
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    dow_sin = np.sin(2 * np.pi * day_of_week / 7)
    dow_cos = np.cos(2 * np.pi * day_of_week / 7)
    return torch.tensor([hour_sin, hour_cos, dow_sin, dow_cos], dtype=torch.float32)

