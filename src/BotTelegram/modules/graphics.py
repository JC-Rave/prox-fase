import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# Grafico de cantidad de alertas por día (últimos 7 días)
def plot_alerts_per_day(data):
    data_frame = pd.DataFrame.from_dict(data, orient="index")
    data_frame["date"] = pd.to_datetime(data_frame["date"])

    today_date = pd.to_datetime(datetime.now().date())
    start_date = today_date - timedelta(days=6)  # 6 días atrás para incluir hoy
    data_frame = data_frame[data_frame["date"] >= start_date]

    alerts_per_day = data_frame.groupby(data_frame["date"].dt.date)["date"].count()
    path_image = "graph_alerts_per_day.png"

    plt.figure(figsize=(8, 6))
    alerts_per_day.plot(kind="bar", color="skyblue")
    plt.title("Cantidad de alertas por día")
    plt.xlabel("Fecha")
    plt.ylabel("Cantidad de alertas")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path_image)
    plt.close()

    return path_image


# Grafico de frecuencia de alertas por día de la semana
def plot_alerts_by_day_week(data):
    data_frame = pd.DataFrame.from_dict(data, orient="index")
    data_frame["date"] = pd.to_datetime(data_frame["date"])

    alerts_per_day_week = data_frame.groupby(data_frame["date"].dt.dayofweek)["date"].count()
    path_image = "graph_alerts_by_day_week.png"

    plt.figure(figsize=(8, 6))
    alerts_per_day_week.plot(kind="bar", color="salmon")
    plt.title("Frecuencia de alertas por día de la semana")
    plt.xlabel("Día de la semana")
    plt.ylabel("Cantidad de alertas")
    plt.xticks(range(7), ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], rotation=45)
    plt.tight_layout()
    plt.savefig(path_image)
    plt.close()

    return path_image


# Grafico de lado del vehículo más frecuente en los incidentes
def plot_vehicle_side(data):
    data_frame = pd.DataFrame.from_dict(data, orient="index")

    path_image = "vehicle_side_graph.png"

    plt.figure(figsize=(6, 6))
    data_frame["side"].value_counts().plot(kind="pie", autopct="%1.1f%%", colors=["lightgreen", "lightblue", "lightcoral", "lightskyblue"])
    plt.title("Lado del vehículo más frecuente en los incidentes")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(path_image)
    plt.close()

    return path_image
    

# Grafico de patrones de incidentes por hora del día
def plot_patterns_incidents(data):
    data_frame = pd.DataFrame.from_dict(data, orient="index")
    data_frame["date"] = pd.to_datetime(data_frame["date"])
    data_frame["time"] = pd.to_timedelta(data_frame["time"])

    data_frame["incident_hour"] = data_frame["time"].dt.components["hours"]
    incidents_per_hour = data_frame.groupby("incident_hour").size()
    path_image = "incident_patterns_graph.png"

    plt.figure(figsize=(8, 6))
    incidents_per_hour.plot(kind="line", color="orange")
    plt.title("Patrones de incidentes por hora del día")
    plt.xlabel("Hora del día")
    plt.ylabel("Cantidad de incidentes")
    plt.xticks(range(24))
    plt.tight_layout()
    plt.savefig(path_image)
    plt.close()

    return path_image

