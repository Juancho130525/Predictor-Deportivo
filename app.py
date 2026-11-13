from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__, template_folder='templates')

# --- 1. CARGAMOS Y CALCULAMOS LOS DATOS AL INICIAR ---
print("⏳ Calculando estadísticas de la NBA...")
try:
    df = pd.read_csv('historico_nba.csv')
    df_jugadores = pd.read_csv('jugadores_nba.csv')
    
    # TRUCO MAESTRO: Extraemos la abreviatura del equipo desde la columna MATCHUP.
    # Ejemplo: si MATCHUP dice "ATL vs. MIA", tomamos las primeras 3 letras "ATL".
    # Esto evita errores si la columna TEAM_ABBREVIATION no estaba en el CSV original.
    df['ABREV_SEGURA'] = df['MATCHUP'].str.split(' ').str[0]
    mapa_equipos = dict(zip(df['TEAM_NAME'], df['ABREV_SEGURA']))

    ataque = df.groupby('TEAM_NAME')['PTS'].mean().reset_index()
    ataque.columns = ['Equipo', 'Puntos_Anotados_Promedio']

    puntos_totales_partido = df.groupby('GAME_ID')['PTS'].sum().reset_index()
    puntos_totales_partido.columns = ['GAME_ID', 'PTS_Totales']
    df = df.merge(puntos_totales_partido, on='GAME_ID')
    df['PTS_Recibidos'] = df['PTS_Totales'] - df['PTS']

    defensa = df.groupby('TEAM_NAME')['PTS_Recibidos'].mean().reset_index()
    defensa.columns = ['Equipo', 'Puntos_Recibidos_Promedio']

    estadisticas = pd.merge(ataque, defensa, on='Equipo')
    lista_equipos = sorted(estadisticas['Equipo'].tolist())
    print("✅ Datos listos.")
except Exception as e:
    print(f"❌ Error al cargar datos: {e}")
    estadisticas = None
    lista_equipos = []
    df_jugadores = None
    mapa_equipos = {}

# --- 2. RUTAS DE LA PÁGINA WEB ---
@app.route('/')
def index():
    return render_template('index.html', equipos=lista_equipos)

@app.route('/predecir')
def predecir():
    if estadisticas is None or df_jugadores is None:
        return jsonify({"error": "Base de datos no cargada"}), 500

    local = request.args.get('local')
    visitante = request.args.get('visitante')

    try:
        stats_local = estadisticas[estadisticas['Equipo'] == local].iloc[0]
        stats_visitante = estadisticas[estadisticas['Equipo'] == visitante].iloc[0]

        puntos_local = (stats_local['Puntos_Anotados_Promedio'] + stats_visitante['Puntos_Recibidos_Promedio']) / 2
        puntos_visitante = (stats_visitante['Puntos_Anotados_Promedio'] + stats_local['Puntos_Recibidos_Promedio']) / 2
        total_puntos = puntos_local + puntos_visitante

        if puntos_local > puntos_visitante:
            ganador = local
            diferencia = puntos_local - puntos_visitante
        else:
            ganador = visitante
            diferencia = puntos_visitante - puntos_local

        # --- BUSCAR JUGADORES ---
        abrev_local = mapa_equipos.get(local, "")
        abrev_visitante = mapa_equipos.get(visitante, "")

        # Esto imprimirá en la terminal para que veamos qué está pasando
        print(f"🔍 Buscando jugadores para: {local} ({abrev_local}) y {visitante} ({abrev_visitante})")

        top_local = df_jugadores[df_jugadores['TEAM_ABBREVIATION'] == abrev_local].sort_values(by='PTS', ascending=False).head(2)
        top_visitante = df_jugadores[df_jugadores['TEAM_ABBREVIATION'] == abrev_visitante].sort_values(by='PTS', ascending=False).head(2)

        lista_top_local = top_local.to_dict('records')
        lista_top_visitante = top_visitante.to_dict('records')

        return jsonify({
            "local": local,
            "visitante": visitante,
            "puntos_local": round(puntos_local, 1),
            "puntos_visitante": round(puntos_visitante, 1),
            "total_puntos": round(total_puntos, 1),
            "ganador": ganador,
            "diferencia": round(diferencia, 1),
            "jugadores_local": lista_top_local,
            "jugadores_visitante": lista_top_visitante
        })
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
        return jsonify({"error": "Equipo no encontrado o error en cálculo"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)