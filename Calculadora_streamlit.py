import streamlit as st
from datetime import datetime, timedelta
import requests

# Obtener feriados desde la API para varios años
@st.cache_data
def obtener_feriados_api(anios):
    feriados = {}
    for anio in anios:
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{anio}/AR"
            resp = requests.get(url)
            resp.raise_for_status()
            datos = resp.json()
            for feriado in datos:
                fecha = datetime.strptime(feriado["date"], "%Y-%m-%d")
                feriados[fecha] = feriado["localName"]
        except Exception as e:
            st.error(f"Error al obtener feriados para {anio}: {e}")
    return feriados

# Contar días hábiles
def contar_dias_habiles(fecha_inicio, fecha_fin, feriados):
    dias = (fecha_fin - fecha_inicio).days
    return sum(
        1 for i in range(dias)
        if (fecha_inicio + timedelta(days=i)).weekday() < 5 and (fecha_inicio + timedelta(days=i)) not in feriados
    )

#  Configuración de la app
st.set_page_config(page_title="Calculadora de Días Hábiles", layout="centered")
st.title("📅 Calculadora de Días Hábiles")

#  Selección de opción 
opcion = st.radio(
    "¿Qué desea calcular?",
    (
        "Hasta vacaciones de invierno (18/07/2025)",
        "Desde fin de vacaciones (01/08/2025) hasta fin de año",
        "Entre dos fechas personalizadas"
    )
)

# Entrada de fechas según opción 
if opcion == "Hasta vacaciones de invierno (18/07/2025)":
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime.today())
    fecha_fin = datetime(2025, 7, 18).date()

elif opcion == "Desde fin de vacaciones (01/08/2025) hasta fin de año":
    fecha_inicio = datetime(2025, 8, 1).date()
    fecha_fin = datetime(2025, 12, 31).date()
    st.info(f"Se calculará desde el {fecha_inicio.strftime('%d/%m/%Y')} hasta el {fecha_fin.strftime('%d/%m/%Y')}.")

else:
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=datetime.today())
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=datetime.today() + timedelta(days=30))

    if fecha_fin <= fecha_inicio:
        st.warning("⚠️ La fecha de fin debe ser posterior a la fecha de inicio.")
        st.stop()

# Botón de cálculo 
if st.button("Calcular"):
    # Detectar años involucrados
    anios = list(range(fecha_inicio.year, fecha_fin.year + 1))
    feriados = obtener_feriados_api(anios)

    # Cálculos
    dias_corridos = (fecha_fin - fecha_inicio).days
    dias_habiles = contar_dias_habiles(fecha_inicio, fecha_fin, feriados)

    st.success(f"📆 Días corridos: **{dias_corridos}**\n\n💼 Días hábiles: **{dias_habiles}**")

    # Feriados en el rango
    feriados_en_rango = {
        fecha.date(): nombre
        for fecha, nombre in feriados.items()
        if fecha_inicio <= fecha.date() < fecha_fin
    }

    if feriados_en_rango:
        st.subheader("📌 Feriados dentro del rango:")
        for fecha, nombre in sorted(feriados_en_rango.items()):
            st.markdown(f"- {fecha.strftime('%d/%m/%Y')}: {nombre}")
    else:
        st.info("No hay feriados dentro del rango seleccionado.")
    
        # Mostrar feriados como calendario visual
    import plotly.graph_objects as go
    from calendar import monthrange

    st.subheader("📆 Calendario visual del año")

    for anio in anios:
        meses = list(range(1, 13))
        for mes in meses:
            dias_mes = monthrange(anio, mes)[1]
            dias = []
            colores = []

            for dia in range(1, dias_mes + 1):
                fecha = datetime(anio, mes, dia)
                if fecha.date() < fecha_inicio or fecha.date() >= fecha_fin:
                    continue
                dias.append(fecha.strftime("%d/%m"))
                if fecha in feriados:
                    colores.append("red")
                elif fecha.weekday() >= 5:
                    colores.append("lightgray")
                else:
                    colores.append("green")

            if dias:
                fig = go.Figure(data=[go.Bar(
                    x=dias,
                    y=[1]*len(dias),
                    marker_color=colores,
                    text=[feriados.get(fecha, "") for fecha in [datetime(anio, mes, int(d.split("/")[0])) for d in dias]],
                    hoverinfo="text"
                )])
                fig.update_layout(
                    title=f"{anio} - {mes:02d}",
                    xaxis_title="Día",
                    yaxis=dict(showticklabels=False),
                    height=200,
                    margin=dict(t=30, b=30)
                )
                st.plotly_chart(fig, use_container_width=True)

        
#Para ejecutar --> streamlit run calculadora_streamlit.py en la terminal

