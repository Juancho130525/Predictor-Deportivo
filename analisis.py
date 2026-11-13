import pandas as pd

# 1. Cargamos los datos y hacemos los cálculos (igual que antes)
df = pd.read_csv('historico_nba.csv')

ataque = df.groupby('TEAM_NAME')['PTS'].mean().reset_index()
ataque.columns = ['Equipo', 'Puntos_Anotados_Promedio']

puntos_totales_partido = df.groupby('GAME_ID')['PTS'].sum().reset_index()
puntos_totales_partido.columns = ['GAME_ID', 'PTS_Totales']
df = df.merge(puntos_totales_partido, on='GAME_ID')
df['PTS_Recibidos'] = df['PTS_Totales'] - df['PTS']

defensa = df.groupby('TEAM_NAME')['PTS_Recibidos'].mean().reset_index()
defensa.columns = ['Equipo', 'Puntos_Recibidos_Promedio']

# Unimos todo en nuestra tabla maestra
estadisticas = pd.merge(ataque, defensa, on='Equipo')

# 2. Función para predecir el partido
def predecir_partido(local, visitante):
    # Buscamos las estadísticas de los equipos (usamos .str.contains para evitar errores de tipeo)
    stats_local = estadisticas[estadisticas['Equipo'].str.contains(local, case=False)].iloc[0]
    stats_visitante = estadisticas[estadisticas['Equipo'].str.contains(visitante, case=False)].iloc[0]

    # Fórmula: (Ataque del Equipo A + Defensa del Equipo B) / 2
    puntos_local = (stats_local['Puntos_Anotados_Promedio'] + stats_visitante['Puntos_Recibidos_Promedio']) / 2
    puntos_visitante = (stats_visitante['Puntos_Anotados_Promedio'] + stats_local['Puntos_Recibidos_Promedio']) / 2
    
    total_puntos = puntos_local + puntos_visitante

    print("\n" + "="*40)
    print(f"🏀 PREDICCIÓN: {stats_local['Equipo']} vs {stats_visitante['Equipo']}")
    print("="*40)
    print(f"Puntos estimados para {stats_local['Equipo']}: {puntos_local:.1f}")
    print(f"Puntos estimados para {stats_visitante['Equipo']}: {puntos_visitante:.1f}")
    print(f"TOTAL de puntos estimados en el partido: {total_puntos:.1f}")
    print("="*40)
    print("💡 Consejo de apuesta: Si la casa de apuestas pone la línea de puntos totales por debajo de este número, apostar a 'Más de' tiene valor estadístico.")
    print("="*40 + "\n")

# 3. Probamos la función con un partido de ejemplo
# Puedes cambiar los nombres por los que quieras probar
predecir_partido("Lakers", "Warriors")