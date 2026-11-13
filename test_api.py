from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
from datetime import datetime

# Calcular la temporada actual automáticamente
# Si estamos en Noviembre de 2026, la temporada es "2026-27"
ahora = datetime.now()
if ahora.month >= 10: # Si es Octubre o después (inicio de temporada)
    año_inicio = ahora.year
else:
    año_inicio = ahora.year - 1

temporada = f"{año_inicio}-{str(año_inicio+1)[2:]}"

print(f"⏳ Descargando datos de la temporada {temporada}... (Esto puede tardar unos segundos)")

try:
    # Buscamos los partidos
    gamefinder = leaguegamefinder.LeagueGameFinder(
        season_nullable=temporada,
        season_type_nullable='Regular Season',
        league_id_nullable='00' 
    )
    
    df = gamefinder.get_data_frames()[0]
    
    # Si la temporada actual aún no tiene partidos (apenas va a empezar), bajamos la anterior
    if df.empty:
        print("⚠️ No hay partidos jugados de esta temporada. Buscando la anterior...")
        temporada = f"{año_inicio-1}-{str(año_inicio)[2:]}"
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable=temporada,
            season_type_nullable='Regular Season',
            league_id_nullable='00' 
        )
        df = gamefinder.get_data_frames()[0]

    # Guardamos los datos actualizados
    df.to_csv('historico_nba.csv', index=False)
    
    print(f"✅ ¡Datos guardados! Temporada: {temporada}.")
    print(f"Se registraron {len(df)} partidos.")
    
    # Mostramos el partido más reciente descargado para verificar la fecha
    ultimo_partido = df.sort_values(by='GAME_DATE', ascending=False).iloc[0]
    print(f"El último partido registrado es del: {ultimo_partido['GAME_DATE']}")

except Exception as e:
    print(f"❌ Error al descargar: {e}")