from nba_api.stats.endpoints import leaguedashplayerstats
from datetime import datetime
import pandas as pd

ahora = datetime.now()
año_inicio = ahora.year if ahora.month >= 10 else ahora.year - 1
temporada = f"{año_inicio}-{str(año_inicio+1)[2:]}"

print(f"⏳ Descargando estadísticas de jugadores de la temporada {temporada}...")

try:
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=temporada,
        per_mode_detailed='PerGame' # Promedios por partido
    )
    
    df_jugadores = stats.get_data_frames()[0]
    
    # Guardamos solo lo que nos importa: Nombre, Equipo, Puntos, Asistencias, Rebotes
    columnas = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'AST', 'REB']
    df_jugadores = df_jugadores[columnas]
    
    df_jugadores.to_csv('jugadores_nba.csv', index=False)
    print("✅ ¡Datos de jugadores guardados en 'jugadores_nba.csv'!")
    
except Exception as e:
    print(f"❌ Error: {e}")