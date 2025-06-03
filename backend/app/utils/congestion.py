def classify_congestion(speed):
    if speed > 40:
        return 1, "#00cc44"  # зеленый
    elif speed > 25:
        return 4, "#ffcc00"  # желтый
    elif speed > 10:
        return 7, "#ffaa00"  # оранжевый
    else:
        return 9, "#cc0000"  # красный

