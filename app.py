"""SIGERH: tablero exploratorio de riesgo hipotecario SIMULADO."""
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="SIGERH | Panel experimental", page_icon="🏠", layout="wide")
st.markdown("""<style>
/* SIGERH v6: paleta accesible, sin reglas globales que oculten textos */
:root { --vino:#760E30; --vino-profundo:#600D2A; --hueso:#F8F3EA; --texto:#29252A; --verde:#83B796; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {background-color:#F8F3EA !important;color:#29252A !important;}
[data-testid="stHeader"] {background-color:#F8F3EA !important;}
.block-container {padding-top:1.6rem;max-width:1510px;}
/* El contenido principal siempre usa letras oscuras. No afectar iconos SVG. */
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {color:#760E30 !important;}
[data-testid="stMain"] .stMarkdown p, [data-testid="stMain"] .stCaption p {color:#3C343A !important;}
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {color:#55434C !important;opacity:1 !important;font-size:0.91rem !important;}
/* Sidebar: texto claro solamente sobre fondo vino */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {background-color:#680C2A !important;}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {color:#FFFFFF !important;opacity:1 !important;}
[data-testid="stSidebar"] hr {border-color:#B27A8B !important;}
/* Inputs: todos claros y con texto oscuro, incluso dentro del sidebar */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-baseweb="textarea"] {background-color:#FFFDF9 !important;border-color:#D3A9B6 !important;}
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div[role="combobox"],
[data-testid="stSidebar"] [data-baseweb="input"] input,
[data-testid="stSidebar"] [data-baseweb="base-input"] input,
[data-testid="stSidebar"] input::placeholder {color:#30262C !important;-webkit-text-fill-color:#30262C !important;opacity:1 !important;}
[data-testid="stSidebar"] [data-baseweb="select"] svg {fill:#760E30 !important;color:#760E30 !important;}
/* Inputs deshabilitados: legibles */
[data-testid="stSidebar"] input:disabled {opacity:1 !important;color:#4C3B43 !important;-webkit-text-fill-color:#4C3B43 !important;}
/* Pestañas */
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:10px;border-bottom:1px solid #DCCBC5;}
[data-testid="stTabs"] button[data-baseweb="tab"] {color:#4D2535 !important;font-weight:650 !important;opacity:1 !important;}
[data-testid="stTabs"] button[data-baseweb="tab"] p,
[data-testid="stTabs"] button[data-baseweb="tab"] span {color:inherit !important;opacity:1 !important;}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {color:#760E30 !important;border-bottom:3px solid #760E30 !important;}
/* Alertas: texto oscuro sobre fondos claros */
[data-testid="stAlert"] {border-radius:10px !important;}
[data-testid="stAlert"] p, [data-testid="stAlert"] span {color:#29252A !important;opacity:1 !important;}
/* Tarjetas */
[data-testid="stMetric"] {background:#FFFFFF !important;padding:19px;border:1px solid #E7D8D1;border-left:4px solid #760E30;border-radius:13px;box-shadow:0 2px 8px #4422190D;}
[data-testid="stMetricLabel"] p {color:#55434C !important;}
[data-testid="stMetricValue"] {color:#760E30 !important;font-size:clamp(1.25rem, 1.7vw, 2rem) !important;overflow-wrap:anywhere !important;}
[data-testid="stDataFrame"] {border:1px solid #E8D9D2;border-radius:10px;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#F2E5E9 !important;opacity:1 !important;}
/* Menús desplegables (renderizados fuera del sidebar) */
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] {background-color:#FFFDF9 !important;color:#29252A !important;}
/* Etiquetas experimentales */
.risk {padding:9px 15px;border-radius:10px;font-weight:700;display:inline-block;margin:5px 0 12px;}
.risk-low {background:#E4F1E7;color:#24573D;}
.risk-mid {background:#FAEBCB;color:#694A0D;}
.risk-high {background:#F7DFE2;color:#842138;}
.sigerh-header {padding:22px 26px;background:linear-gradient(105deg,#FFFDFC,#F2E3D7);border:1px solid #EAD7D0;border-radius:15px;margin-bottom:16px;}
.sigerh-header h1 {margin:0 0 6px;color:#760E30 !important;font-size:2.2rem;}
.sigerh-header p {color:#624851 !important;margin:0;font-size:.95rem;}
</style>""", unsafe_allow_html=True)
st.markdown("""<div class="sigerh-header"><h1>🏠 SIGERH | Centro de análisis hipotecario</h1><p>Sistema de Gestión y Predicción del Riesgo Hipotecario · Prototipo académico · Ciudad de México</p></div>""", unsafe_allow_html=True)
st.info("SIGERH integra una cartera de 100,000 registros simulados. Las clasificaciones del MPRH son experimentales y no equivalen a predicciones validadas con créditos reales.")

BASE_DIR = Path(__file__).resolve().parent
@st.cache_data(show_spinner="Cargando archivos...")
def cargar(base_path, files):
    base = pd.read_csv(base_path, low_memory=False)
    if base.id_credito.duplicated().any():
        raise ValueError("La base contiene id_credito duplicados")
    frames = []
    for escenario, conjunto, file in files:
        df = pd.read_csv(file)
        expected = {"id_credito", "conjunto", "etiqueta_simulada", "puntuacion_experimental", "nivel_experimental"}
        if not expected.issubset(df.columns):
            raise ValueError(f"Columnas faltantes en {file}: {expected-set(df.columns)}")
        if df.id_credito.duplicated().any() or not df.conjunto.eq(conjunto).all():
            raise ValueError(f"Identificadores repetidos o conjunto incorrecto en {file}")
        if not df.etiqueta_simulada.isin([0,1]).all() or not df.nivel_experimental.isin(["Bajo","Medio","Alto"]).all():
            raise ValueError(f"Etiquetas o niveles inválidos en {file}")
        if not df.puntuacion_experimental.between(0,1).all():
            raise ValueError(f"Puntuaciones fuera de [0,1] en {file}")
        df["escenario"] = escenario
        frames.append(df)
    clases = pd.concat(frames, ignore_index=True)
    if clases.duplicated(["id_credito", "escenario"]).any():
        raise ValueError("Crédito repetido dentro de un escenario")
    missing = ~clases.id_credito.isin(base.id_credito)
    if missing.any():
        raise ValueError(f"Hay {missing.sum()} etiquetas sin crédito correspondiente")
    keep = ["id_credito", "alcaldia", "institucion", "tipo_acreditado", "ingreso_mensual_mxn", "pago_mensual_mxn", "carga_pago_pct", "meses_atraso", "saldo_actual_mxn", "monto_original_credito_mxn", "estatus_credito"]
    return clases.merge(base[keep], on="id_credito", validate="many_to_one"), len(base)


COLOR_NIVEL = {"Bajo":"#83B796", "Medio":"#EAC477", "Alto":"#BD5262"}
VINO = "#760E30"
VERDE = "#83B796"

def preparar_figura(fig, altura=440, horizontal=False):
    fig.update_layout(
        template="plotly_white", height=altura, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#513E46",size=12),
        margin=dict(l=12,r=28,t=22,b=50), legend=dict(orientation="h",y=-.18,x=0),
        hoverlabel=dict(bgcolor="#FFFDF9",font_color="#342B30"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#DDCFC8",automargin=True)
    fig.update_yaxes(gridcolor="#EEE4DD",zeroline=False,automargin=True)
    if horizontal:
        fig.update_layout(margin=dict(l=8,r=50,t=14,b=28),showlegend=False)
    return fig

def grafico_horizontal(tabla, x, y, color, sufijo="", altura=530):
    t=tabla.sort_values(x,ascending=True)
    fig=go.Figure(go.Bar(x=t[x],y=t[y],orientation="h",marker_color=color,
        text=[f"{v:,.1f}{sufijo}" if sufijo else f"{v:,.0f}" for v in t[x]],
        textposition="outside",cliponaxis=False))
    preparar_figura(fig,altura,horizontal=True)
    fig.update_xaxes(ticksuffix=sufijo)
    return fig

with st.sidebar:
    st.header("Configuración")
    with st.expander("Fuentes de datos", expanded=False):
        root = st.text_input("Carpeta de archivos", str(BASE_DIR / "datos"), help="Puede cambiarse por la carpeta que contenga los archivos CSV")
        root = Path(root)
        base_file = st.text_input("Archivo de cartera", str(root / "BD_hipotecarios_SIGERH_limpia.csv"))
    st.divider()
    st.caption("La cartera completa se consulta en su propia pestaña. Las clasificaciones de validación y prueba se mantienen separadas de la cartera general.")

files = [(s,c,root / f"clasificacion_{s}_{c}.csv") for s in ["variable","persistente"] for c in ["validacion","prueba"]]
required = [Path(base_file)] + [f for _,_,f in files]
missing_files = [str(f) for f in required if not f.exists()]
if missing_files:
    st.error("Faltan archivos. Colócalos en la carpeta indicada o modifica la ruta en el panel lateral.")
    st.code("\n".join(missing_files))
    st.stop()
try:
    all_data, original_count = cargar(str(base_file), [(s,c,str(f)) for s,c,f in files])
except Exception as e:
    st.error(f"Error de validación de archivos: {e}")
    st.stop()

with st.sidebar:
    st.header("Filtros de cartera")
    escenario = st.radio("Escenario", ["variable", "persistente"], format_func=str.title)
    conjunto = st.selectbox("Conjunto", ["validacion", "prueba"], format_func=str.title)
    d = all_data.query("escenario == @escenario and conjunto == @conjunto").copy()
    alcaldias = st.multiselect("Alcaldía", sorted(d.alcaldia.dropna().unique().tolist()))
    if alcaldias:
        d = d[d.alcaldia.isin(alcaldias)]
    instituciones = st.multiselect("Institución", sorted(d.institucion.dropna().unique().tolist()))
    if instituciones:
        d = d[d.institucion.isin(instituciones)]
    niveles = st.multiselect("Nivel experimental", ["Bajo", "Medio", "Alto"])
    if niveles:
        d = d[d.nivel_experimental.isin(niveles)]
    search = st.text_input("Buscar ID de crédito").strip()
    if search:
        d = d[d.id_credito.astype(str).str.contains(search, case=False, regex=False)]

st.info(f"Cartera general: {original_count:,} registros. MPRH: {all_data[all_data.escenario==escenario].id_credito.nunique():,} créditos con clasificaciones de validación o prueba. Conjunto predictivo seleccionado: {conjunto}.")
st.caption("Los niveles Bajo, Medio y Alto son percentiles de puntuaciones de validación, no categorías de riesgo real.")
t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs(["🗂️ Cartera completa", "📊 Resumen MPRH", "🔎 Explorador", "🏠 Ficha de crédito", "🗺️ Análisis por alcaldía", "💰 Análisis financiero", "🔄 Comparación de escenarios", "📖 Metodología"])
# La cartera se carga por separado para no confundirla con los resultados de evaluación.
@st.cache_data(show_spinner="Cargando cartera hipotecaria completa...")
def cargar_cartera_completa(ruta):
    df = pd.read_csv(ruta, low_memory=False)
    if df["id_credito"].isna().any() or df["id_credito"].duplicated().any():
        raise ValueError("La cartera completa debe tener identificadores únicos y no nulos")
    return df

with t0:
    st.subheader("Gestión y consulta de la cartera hipotecaria completa")
    st.caption("Vista descriptiva de la base simulada original. Los filtros de esta pestaña son independientes de los filtros predictivos del menú lateral.")
    try:
        cartera = cargar_cartera_completa(str(base_file))
    except Exception as exc:
        st.error(f"No fue posible cargar la cartera completa: {exc}")
        st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Registros de cartera", f"{len(cartera):,}")
    c2.metric("Alcaldías", f"{cartera['alcaldia'].nunique():,}")
    c3.metric("Instituciones", f"{cartera['institucion'].nunique():,}")
    c4.metric("Saldo total (millones MXN)", f"${pd.to_numeric(cartera['saldo_actual_mxn'],errors='coerce').sum()/1_000_000:,.1f}")

    # Los grupos son una partición de los créditos originales, no de filas escenario-crédito.
    elegibles = 56449
    if len(cartera) == 100000:
        st.caption("Cohorte del experimento previamente documentada: 56,449 elegibles y 43,551 excluidos. Estas cantidades son globales y no se recalculan con los filtros de esta pestaña.")
    else:
        st.caption("Las cantidades de elegibilidad históricas deben verificarse frente a los archivos del motor MPRH.")

    fa,fb,fc = st.columns(3)
    with fa:
        alcs = st.multiselect("Filtrar alcaldías (cartera completa)", sorted(cartera['alcaldia'].dropna().astype(str).unique()), key="cartera_alcs")
    with fb:
        insts = st.multiselect("Filtrar instituciones (cartera completa)", sorted(cartera['institucion'].dropna().astype(str).unique()), key="cartera_insts")
    with fc:
        ests = st.multiselect("Filtrar estatus actual", sorted(cartera['estatus_credito'].dropna().astype(str).unique()), key="cartera_estatus")
    vista = cartera
    if alcs: vista = vista[vista['alcaldia'].isin(alcs)]
    if insts: vista = vista[vista['institucion'].isin(insts)]
    if ests: vista = vista[vista['estatus_credito'].isin(ests)]
    busqueda_cartera = st.text_input("Buscar identificador en los 100,000 créditos", key="busqueda_cartera").strip()
    if busqueda_cartera:
        vista = vista[vista['id_credito'].astype(str).str.contains(busqueda_cartera,case=False,regex=False)]

    k1,k2,k3 = st.columns(3)
    k1.metric("Créditos tras filtrar", f"{len(vista):,}")
    k2.metric("Ingreso mediano (MXN)", f"${pd.to_numeric(vista['ingreso_mensual_mxn'],errors='coerce').median():,.0f}" if len(vista) else "—")
    k3.metric("Carga de pago mediana", f"{pd.to_numeric(vista['carga_pago_pct'],errors='coerce').median():.1f}%" if len(vista) else "—")

    if not vista.empty:
        g1,g2=st.columns(2)
        with g1:
            st.subheader("Créditos por alcaldía")
            por_alc=vista['alcaldia'].value_counts().rename_axis('alcaldia').reset_index(name='creditos')
            st.plotly_chart(grafico_horizontal(por_alc,'creditos','alcaldia',VERDE,altura=520),use_container_width=True)
        with g2:
            st.subheader("Estado actual del crédito")
            por_est=vista['estatus_credito'].fillna('Sin dato').value_counts().rename_axis('estatus').reset_index(name='creditos')
            st.plotly_chart(grafico_horizontal(por_est,'creditos','estatus',VINO,altura=520),use_container_width=True)
        st.subheader("Explorador de cartera original")
        columnas=['id_credito','alcaldia','institucion','estatus_credito','meses_atraso','ingreso_mensual_mxn','pago_mensual_mxn','carga_pago_pct','saldo_actual_mxn']
        st.dataframe(vista[columnas],hide_index=True,use_container_width=True,height=410)
        st.download_button("Descargar cartera filtrada (CSV)",vista[columnas].to_csv(index=False).encode('utf-8-sig'),file_name='SIGERH_cartera_completa_filtrada.csv',mime='text/csv')
    else:
        st.info("No hay créditos con los filtros seleccionados.")
    st.caption("La variable original 'probabilidad_incumplimiento' no se presenta como predicción futura del MPRH. Los créditos excluidos no reciben automáticamente una puntuación experimental.")

with t1:
    a,b,c,dcol = st.columns(4)
    a.metric("Créditos visibles", f"{len(d):,}")
    b.metric("Nivel alto", f"{(d.nivel_experimental=='Alto').sum():,}")
    c.metric("Eventos simulados", f"{int(d.etiqueta_simulada.sum()):,}")
    dcol.metric("Frecuencia simulada", f"{d.etiqueta_simulada.mean():.2%}" if len(d) else "—")
    left,right = st.columns(2)
    with left:
        st.subheader("Créditos según nivel de riesgo experimental")
        counts = d.nivel_experimental.value_counts().reindex(["Bajo","Medio","Alto"], fill_value=0)
        fig=go.Figure(go.Bar(x=counts.index,y=counts.values,marker_color=[COLOR_NIVEL[n] for n in counts.index],
            text=[f"{n:,}" for n in counts.values],textposition="outside"))
        preparar_figura(fig,390)
        fig.update_layout(showlegend=False,yaxis_title="Cantidad de créditos")
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.subheader("Cantidad de créditos analizados por alcaldía")
        cantidad=d.alcaldia.value_counts().rename_axis("alcaldia").reset_index(name="creditos")
        st.plotly_chart(grafico_horizontal(cantidad,"creditos","alcaldia",VERDE,altura=520),use_container_width=True)
    st.subheader("Composición y frecuencia por nivel")
    if not d.empty:
        resumen = (d.groupby("nivel_experimental", observed=True)
                   .agg(creditos=("id_credito", "size"), eventos=("etiqueta_simulada", "sum"))
                   .reindex(["Bajo", "Medio", "Alto"]).fillna(0))
        resumen["frecuencia_simulada_%"] = (100 * resumen["eventos"] / resumen["creditos"].replace(0, float("nan"))).round(2)
        st.dataframe(resumen.reset_index().rename(columns={"nivel_experimental":"Nivel", "creditos":"Créditos", "eventos":"Eventos simulados", "frecuencia_simulada_%":"Frecuencia simulada (%)"}), hide_index=True, use_container_width=True)
    st.caption("Las frecuencias son de eventos simulados. El conjunto de prueba se ha utilizado previamente en análisis exploratorios.")
with t2:
    st.subheader("Explorador de cartera")
    cols = ["id_credito","alcaldia","institucion","meses_atraso","carga_pago_pct","puntuacion_experimental","nivel_experimental","etiqueta_simulada"]
    st.dataframe(d[cols].sort_values("puntuacion_experimental", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Exportar vista filtrada (CSV)", data=d[cols].to_csv(index=False).encode("utf-8-sig"), file_name=f"SIGERH_{escenario}_{conjunto}_filtrado.csv", mime="text/csv")
with t3:
    if d.empty:
        st.info("No hay créditos con los filtros seleccionados.")
    else:
        chosen = st.selectbox("Crédito", d.id_credito.sort_values().tolist())
        r = d.loc[d.id_credito==chosen].iloc[0]
        st.subheader(f"Crédito {chosen}")
        clase = {"Bajo":"risk-low", "Medio":"risk-mid", "Alto":"risk-high"}[r.nivel_experimental]
        st.markdown(f'<span class="risk {clase}">Nivel experimental: {r.nivel_experimental}</span>', unsafe_allow_html=True)
        x,y,z = st.columns(3)
        x.metric("Puntuación experimental", f"{float(r.puntuacion_experimental):.1%}")
        y.metric("Meses de atraso inicial", str(r.meses_atraso))
        z.metric("Carga de pago (%)", f"{float(r.carga_pago_pct):.1f}" if pd.notna(r.carga_pago_pct) else "—")
        st.write({"Escenario": escenario.title(), "Conjunto": conjunto.title(), "Nivel experimental": r.nivel_experimental, "Puntuación simulada": round(float(r.puntuacion_experimental),4), "Etiqueta simulada": int(r.etiqueta_simulada)})
        st.write({"Alcaldía": r.alcaldia, "Institución": r.institucion, "Meses de atraso inicial": r.meses_atraso, "Carga de pago (%)": r.carga_pago_pct, "Ingreso mensual (MXN)": r.ingreso_mensual_mxn, "Saldo actual (MXN)": r.saldo_actual_mxn})
        st.caption("Ficha descriptiva; no constituye recomendación de crédito ni reestructuración.")

with t4:
    st.subheader("Análisis comparativo por alcaldía")
    st.caption("Resultados descriptivos de créditos simulados, sujetos a los filtros de la barra lateral. No representan riesgo hipotecario real de las alcaldías.")
    if d.empty:
        st.info("No hay créditos para analizar con los filtros actuales. Ajusta los filtros de la barra lateral.")
    else:
        tabla = (d.groupby("alcaldia", dropna=False)
                 .agg(creditos=("id_credito", "size"),
                      eventos_simulados=("etiqueta_simulada", "sum"),
                      puntuacion_media=("puntuacion_experimental", "mean"))
                 .reset_index())
        distribucion = pd.crosstab(d["alcaldia"], d["nivel_experimental"])
        distribucion = distribucion.reindex(columns=["Bajo", "Medio", "Alto"], fill_value=0)
        tabla = tabla.merge(distribucion.reset_index(), on="alcaldia", how="left")
        for nivel in ["Bajo", "Medio", "Alto"]:
            tabla[nivel] = tabla[nivel].fillna(0).astype(int)
            tabla[f"porcentaje_{nivel.lower()}"] = (100 * tabla[nivel] / tabla["creditos"]).round(2)
        tabla["frecuencia_simulada_pct"] = (100 * tabla["eventos_simulados"] / tabla["creditos"]).round(2)
        tabla["puntuacion_media"] = tabla["puntuacion_media"].round(4)
        tabla = tabla.sort_values("creditos", ascending=False).reset_index(drop=True)
        total_alcaldias = len(tabla)
        c1, c2, c3 = st.columns(3)
        c1.metric("Alcaldías representadas", f"{total_alcaldias}")
        c2.metric("Créditos analizados", f"{len(d):,}")
        c3.metric("Créditos de nivel alto", f"{int((d.nivel_experimental == 'Alto').sum()):,}")
        st.divider()
        minimo = st.number_input("Mínimo de créditos por alcaldía para mostrar porcentajes comparativos", min_value=1, max_value=10000, value=30, step=10,
                                 help="Umbral descriptivo para evitar destacar tasas basadas en grupos muy pequeños; no es una prueba estadística.")
        comparables = tabla.loc[tabla["creditos"] >= minimo].copy()
        if comparables.empty:
            st.warning("Ninguna alcaldía cumple el mínimo de registros. Reduce el umbral o elimina algunos filtros.")
        else:
            st.subheader("Composición porcentual de créditos por nivel de riesgo")
            st.caption("Cada alcaldía suma aproximadamente 100%. Los niveles proceden de percentiles experimentales de validación.")
            porcentajes = (comparables.set_index("alcaldia")[["porcentaje_bajo", "porcentaje_medio", "porcentaje_alto"]]
                           .rename(columns={"porcentaje_bajo": "Bajo (%)", "porcentaje_medio": "Medio (%)", "porcentaje_alto": "Alto (%)"}))
            fig=go.Figure()
            for nombre, columna in [("Bajo","Bajo (%)"),("Medio","Medio (%)"),("Alto","Alto (%)")]:
                fig.add_trace(go.Bar(name=f"Nivel {nombre.lower()}",y=porcentajes.index,x=porcentajes[columna],
                    orientation="h",marker_color=COLOR_NIVEL[nombre],hovertemplate="%{y}<br>%{x:.2f}%<extra>"+nombre+"</extra>"))
            preparar_figura(fig,max(490,len(porcentajes)*33+120))
            fig.update_layout(barmode="stack",xaxis_title="Porcentaje de créditos",yaxis_title="",legend=dict(orientation="h",y=-.12,x=0))
            fig.update_xaxes(range=[0,100],ticksuffix="%")
            fig.update_yaxes(categoryorder="array",categoryarray=list(reversed(porcentajes.index.tolist())))
            st.plotly_chart(fig,use_container_width=True)
            izq, der = st.columns(2)
            with izq:
                st.subheader("Porcentaje de créditos de nivel alto por alcaldía")
                st.plotly_chart(grafico_horizontal(comparables,"porcentaje_alto","alcaldia",COLOR_NIVEL["Alto"],"%",altura=530),use_container_width=True)
            with der:
                st.subheader("Frecuencia de incumplimiento simulado por alcaldía")
                st.plotly_chart(grafico_horizontal(comparables,"frecuencia_simulada_pct","alcaldia",VERDE,"%",altura=530),use_container_width=True)
            st.caption("Las diferencias pueden deberse a la composición de los datos simulados y al tamaño de cada grupo; no establecen causalidad ni comparaciones poblacionales representativas.")
        st.subheader("Tabla comparativa descargable")
        vista = tabla.rename(columns={
            "alcaldia": "Alcaldía", "creditos": "Créditos", "eventos_simulados": "Eventos simulados",
            "Bajo": "Créditos bajo", "Medio": "Créditos medio", "Alto": "Créditos alto",
            "porcentaje_bajo": "Bajo (%)", "porcentaje_medio": "Medio (%)", "porcentaje_alto": "Alto (%)",
            "frecuencia_simulada_pct": "Frecuencia simulada (%)", "puntuacion_media": "Puntuación media experimental"
        })
        st.dataframe(vista, use_container_width=True, hide_index=True)
        st.download_button("Descargar comparación por alcaldía (CSV)",
                           data=vista.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"SIGERH_alcaldias_{escenario}_{conjunto}.csv", mime="text/csv")
        st.subheader("Detalle de una alcaldía")
        seleccion = st.selectbox("Selecciona una alcaldía para consultar su composición", tabla["alcaldia"].dropna().sort_values().tolist(), key="detalle_alcaldia")
        if seleccion:
            r_alc = tabla.loc[tabla["alcaldia"] == seleccion].iloc[0]
            a1, a2, a3 = st.columns(3)
            a1.metric("Créditos", f"{int(r_alc['creditos']):,}")
            a2.metric("Nivel alto", f"{r_alc['porcentaje_alto']:.2f}%")
            a3.metric("Frecuencia simulada", f"{r_alc['frecuencia_simulada_pct']:.2f}%")
            if r_alc["creditos"] < minimo:
                st.warning("Esta alcaldía tiene menos registros que el mínimo seleccionado: interpreta sus porcentajes con especial cautela.")
        st.caption("Cobertura limitada a los créditos de validación o prueba con puntuaciones disponibles. No incluye todos los 100,000 registros originales.")


with t5:
    st.subheader("Análisis financiero de la cartera simulada")
    st.caption("Estadísticas descriptivas de los créditos visibles con los filtros actuales. Los importes son pesos mexicanos (MXN). No constituyen asesoría financiera ni estimaciones de riesgo real.")
    if d.empty:
        st.info("No hay créditos para analizar con los filtros seleccionados.")
    else:
        fin_cols = ["ingreso_mensual_mxn", "pago_mensual_mxn", "carga_pago_pct", "saldo_actual_mxn", "monto_original_credito_mxn"]
        fin = d.copy()
        for col in fin_cols:
            fin[col] = pd.to_numeric(fin[col], errors="coerce")
        st.caption(f"Cobertura financiera de esta vista: {len(fin):,} créditos clasificados ({escenario}, {conjunto}). Los valores faltantes se omiten de cada cálculo.")
        m1,m2,m3,m4 = st.columns(4)
        def moneda(valor):
            return f"${valor:,.0f} MXN" if pd.notna(valor) else "—"
        def porcentaje(valor):
            return f"{valor:,.1f}%" if pd.notna(valor) else "—"
        m1.metric("Ingreso mensual mediano", moneda(fin["ingreso_mensual_mxn"].median()))
        m2.metric("Pago mensual mediano", moneda(fin["pago_mensual_mxn"].median()))
        m3.metric("Carga de pago mediana", porcentaje(fin["carga_pago_pct"].median()))
        saldo_total = fin["saldo_actual_mxn"].sum(min_count=1)
        # Mostrar millones para evitar que la tarjeta trunque cifras largas.
        m4.metric("Saldo pendiente total (millones MXN)",
                  f"${saldo_total / 1_000_000:,.1f} M" if pd.notna(saldo_total) else "—")
        st.caption(f"Saldo pendiente total exacto de los créditos visibles: {moneda(saldo_total)}.")
        st.info("**Cómo leer los indicadores:** la **mediana** es el valor central al ordenar los créditos; "
                "el **promedio** sería la suma de valores dividida entre el número de registros. "
                "El saldo total corresponde únicamente a los créditos visibles con saldo disponible.")
        f1,f2 = st.columns(2)
        with f1:
            st.subheader("Ingresos y pagos mensuales")
            largo = fin[["ingreso_mensual_mxn","pago_mensual_mxn"]].melt(var_name="Concepto",value_name="Monto (MXN)").dropna()
            largo["Concepto"] = largo["Concepto"].map({"ingreso_mensual_mxn":"Ingreso mensual", "pago_mensual_mxn":"Pago mensual"})
            fig = px.box(largo,x="Concepto",y="Monto (MXN)",color="Concepto",
                         color_discrete_map={"Ingreso mensual":"#83B796","Pago mensual":"#760E30"},points=False)
            preparar_figura(fig,410)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        with f2:
            st.subheader("Distribución de la carga de pago")
            fig=go.Figure(go.Histogram(x=fin["carga_pago_pct"].dropna(),nbinsx=28,marker_color="#760E30",name="Créditos"))
            preparar_figura(fig,410)
            fig.update_layout(showlegend=False,xaxis_title="Carga de pago (%)",yaxis_title="Cantidad de créditos")
            st.plotly_chart(fig,use_container_width=True)
        st.subheader("Indicadores financieros por nivel de riesgo experimental")
        nivel_fin = (fin.groupby("nivel_experimental",observed=True)
                     .agg(creditos=("id_credito","size"),
                          ingreso_mediano_mxn=("ingreso_mensual_mxn","median"),
                          pago_mediano_mxn=("pago_mensual_mxn","median"),
                          carga_mediana_pct=("carga_pago_pct","median"),
                          saldo_mediano_mxn=("saldo_actual_mxn","median"),
                          saldo_total_mxn=("saldo_actual_mxn","sum"))
                     .reindex(["Bajo","Medio","Alto"]).dropna(subset=["creditos"]).reset_index())
        for col in ["ingreso_mediano_mxn","pago_mediano_mxn","carga_mediana_pct","saldo_mediano_mxn","saldo_total_mxn"]:
            nivel_fin[col] = nivel_fin[col].round(2)
        fig = go.Figure(go.Bar(x=nivel_fin["nivel_experimental"],y=nivel_fin["carga_mediana_pct"],
             marker_color=[COLOR_NIVEL[n] for n in nivel_fin["nivel_experimental"]],
             text=[f"{x:.1f}%" for x in nivel_fin["carga_mediana_pct"]],textposition="outside"))
        preparar_figura(fig,340)
        fig.update_layout(showlegend=False,xaxis_title="Nivel experimental",yaxis_title="Carga de pago mediana (%)")
        st.plotly_chart(fig,use_container_width=True)
        nivel_tabla = nivel_fin.rename(columns={"nivel_experimental":"Nivel experimental","creditos":"Créditos",
            "ingreso_mediano_mxn":"Ingreso mediano (MXN)","pago_mediano_mxn":"Pago mediano (MXN)",
            "carga_mediana_pct":"Carga mediana (%)","saldo_mediano_mxn":"Saldo mediano (MXN)",
            "saldo_total_mxn":"Saldo total (MXN)"})
        st.dataframe(nivel_tabla.style.format({
            "Créditos":"{:,.0f}","Ingreso mediano (MXN)":"${:,.2f}",
            "Pago mediano (MXN)":"${:,.2f}","Carga mediana (%)":"{:.2f}%",
            "Saldo mediano (MXN)":"${:,.2f}","Saldo total (MXN)":"${:,.2f}"
        }, na_rep="—"), hide_index=True, use_container_width=True)
        st.subheader("Comparación financiera por alcaldía")
        alc_fin = (fin.groupby("alcaldia",dropna=False)
            .agg(creditos=("id_credito","size"),ingreso_mediano_mxn=("ingreso_mensual_mxn","median"),
                 pago_mediano_mxn=("pago_mensual_mxn","median"),carga_mediana_pct=("carga_pago_pct","median"),
                 saldo_total_mxn=("saldo_actual_mxn","sum"))
            .reset_index().sort_values("creditos",ascending=False))
        minimo_fin = st.number_input("Mínimo de créditos para comparar alcaldías",min_value=1,max_value=10000,value=30,step=10,key="minimo_fin")
        alc_comp = alc_fin.loc[alc_fin["creditos"] >= minimo_fin]
        if alc_comp.empty:
            st.warning("Ninguna alcaldía cumple el mínimo de registros. Ajusta el umbral o los filtros.")
        else:
            st.plotly_chart(grafico_horizontal(alc_comp,"carga_mediana_pct","alcaldia",VERDE,"%",altura=max(380,len(alc_comp)*32+100)),use_container_width=True)
        alcaldias_tabla = alc_fin.rename(columns={"alcaldia":"Alcaldía","creditos":"Créditos",
            "ingreso_mediano_mxn":"Ingreso mediano (MXN)","pago_mediano_mxn":"Pago mediano (MXN)",
            "carga_mediana_pct":"Carga mediana (%)","saldo_total_mxn":"Saldo total (MXN)"})
        st.dataframe(alcaldias_tabla.style.format({
            "Créditos":"{:,.0f}","Ingreso mediano (MXN)":"${:,.2f}",
            "Pago mediano (MXN)":"${:,.2f}","Carga mediana (%)":"{:.2f}%",
            "Saldo total (MXN)":"${:,.2f}"
        }, na_rep="—"), hide_index=True, use_container_width=True)
        st.download_button("Descargar análisis financiero por alcaldía (CSV)",
            data=alc_fin.round(2).to_csv(index=False).encode("utf-8-sig"),
            file_name=f"SIGERH_financiero_alcaldias_{escenario}_{conjunto}.csv",mime="text/csv")
        st.download_button("Descargar análisis financiero por nivel (CSV)",
            data=nivel_fin.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"SIGERH_financiero_niveles_{escenario}_{conjunto}.csv",mime="text/csv")
        st.caption("Las diferencias entre niveles o alcaldías son asociaciones descriptivas dentro de datos simulados. No prueban causalidad ni permiten inferencias sobre la población real de Ciudad de México.")


with t6:
    st.subheader("Comparación de escenarios del MPRH")
    st.caption("Se comparan los mismos créditos en los escenarios variable y persistente. Las etiquetas y puntuaciones son experimentales, no predicciones validadas sobre una cartera real.")
    st.info("Los filtros de alcaldía, institución e ID se aplican a ambos escenarios. Si seleccionaste niveles en la barra lateral, se interpretan respecto al escenario activo para evitar mezclar criterios.")
    # Partir del conjunto seleccionado, pero sin restringir inicialmente por escenario.
    universo = all_data.loc[all_data["conjunto"].eq(conjunto)].copy()
    if alcaldias:
        universo = universo.loc[universo["alcaldia"].isin(alcaldias)]
    if instituciones:
        universo = universo.loc[universo["institucion"].isin(instituciones)]
    if search:
        universo = universo.loc[universo["id_credito"].astype(str).str.contains(search, case=False, regex=False)]
    columnas_comparacion = ["id_credito", "etiqueta_simulada", "puntuacion_experimental", "nivel_experimental"]
    variable = universo.loc[universo["escenario"].eq("variable"), columnas_comparacion].copy()
    persistente = universo.loc[universo["escenario"].eq("persistente"), columnas_comparacion].copy()
    pares = variable.merge(persistente, on="id_credito", how="inner", validate="one_to_one", suffixes=("_variable", "_persistente"))
    if niveles:
        pares = pares.loc[pares[f"nivel_experimental_{escenario}"].isin(niveles)].copy()
    sin_pareja = len(variable) + len(persistente) - 2 * len(variable.merge(persistente, on="id_credito", how="inner"))
    if sin_pareja:
        st.warning(f"Hay {sin_pareja:,} registros de escenario sin pareja en el conjunto filtrado. Se excluyen de esta comparación.")
    if pares.empty:
        st.warning("No hay créditos emparejados con los filtros actuales. Modifica los filtros para continuar.")
    else:
        pares["cambia_nivel"] = pares["nivel_experimental_variable"].ne(pares["nivel_experimental_persistente"])
        pares["cambia_etiqueta"] = pares["etiqueta_simulada_variable"].ne(pares["etiqueta_simulada_persistente"])
        pares["diferencia_puntuacion"] = pares["puntuacion_experimental_persistente"] - pares["puntuacion_experimental_variable"]
        a,b,c,e = st.columns(4)
        a.metric("Créditos emparejados", f"{len(pares):,}")
        b.metric("Cambio de nivel", f"{int(pares['cambia_nivel'].sum()):,}", help="Créditos cuyo nivel experimental es distinto entre escenarios")
        c.metric("Cambio de etiqueta", f"{int(pares['cambia_etiqueta'].sum()):,}", help="Créditos con distinto evento simulado a seis meses")
        e.metric("Puntuación: diferencia mediana", f"{pares['diferencia_puntuacion'].median():+.2%}", help="Puntuación persistente menos variable; no es una diferencia de riesgo real")
        st.subheader("Eventos simulados a seis meses")
        resumen_esc = pd.DataFrame({
            "Escenario": ["Variable", "Persistente"],
            "Créditos": [len(pares), len(pares)],
            "Eventos simulados": [int(pares["etiqueta_simulada_variable"].sum()), int(pares["etiqueta_simulada_persistente"].sum())],
        })
        resumen_esc["Frecuencia simulada (%)"] = (100 * resumen_esc["Eventos simulados"] / resumen_esc["Créditos"]).round(2)
        fig = go.Figure(go.Bar(x=resumen_esc["Escenario"], y=resumen_esc["Frecuencia simulada (%)"],
                               marker_color=["#83B796", "#760E30"],
                               text=[f"{x:.2f}%" for x in resumen_esc["Frecuencia simulada (%)"]], textposition="outside"))
        preparar_figura(fig, 330)
        fig.update_layout(showlegend=False, yaxis_title="Frecuencia de evento simulado (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(resumen_esc.style.format({"Créditos":"{:,.0f}", "Eventos simulados":"{:,.0f}", "Frecuencia simulada (%)":"{:.2f}%"}),
                     hide_index=True, use_container_width=True)
        izq, der = st.columns(2)
        with izq:
            st.subheader("Distribución por nivel y escenario")
            distrib = pd.DataFrame({
                "Nivel": ["Bajo", "Medio", "Alto"],
                "Variable": [int(pares["nivel_experimental_variable"].eq(n).sum()) for n in ["Bajo", "Medio", "Alto"]],
                "Persistente": [int(pares["nivel_experimental_persistente"].eq(n).sum()) for n in ["Bajo", "Medio", "Alto"]],
            })
            fig = go.Figure()
            for nombre, color in [("Variable", "#83B796"), ("Persistente", "#760E30")]:
                fig.add_trace(go.Bar(name=nombre, x=distrib["Nivel"], y=distrib[nombre], marker_color=color))
            preparar_figura(fig, 370)
            fig.update_layout(barmode="group", yaxis_title="Créditos")
            st.plotly_chart(fig, use_container_width=True)
        with der:
            st.subheader("Transiciones de nivel entre escenarios")
            matriz = pd.crosstab(pares["nivel_experimental_variable"], pares["nivel_experimental_persistente"])
            matriz = matriz.reindex(index=["Bajo", "Medio", "Alto"], columns=["Bajo", "Medio", "Alto"], fill_value=0)
            fig = go.Figure(go.Heatmap(z=matriz.values, x=["Persistente: " + n for n in matriz.columns],
                y=["Variable: " + n for n in matriz.index], colorscale=[[0,"#FFF9F2"],[1,"#760E30"]],
                text=matriz.values, texttemplate="%{text:,}", hovertemplate="%{y}<br>%{x}<br>Créditos: %{z:,}<extra></extra>"))
            preparar_figura(fig, 370)
            fig.update_layout(margin=dict(l=5,r=12,t=16,b=40), xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        st.caption("Una transición entre niveles no equivale necesariamente a que cambie la etiqueta simulada. Los niveles se calcularon con umbrales específicos de cada escenario.")
        st.subheader("Consulta y exportación de créditos emparejados")
        vista_pares = pares.rename(columns={
            "id_credito":"ID de crédito", "nivel_experimental_variable":"Nivel variable",
            "nivel_experimental_persistente":"Nivel persistente", "etiqueta_simulada_variable":"Evento variable",
            "etiqueta_simulada_persistente":"Evento persistente", "puntuacion_experimental_variable":"Puntuación variable",
            "puntuacion_experimental_persistente":"Puntuación persistente", "diferencia_puntuacion":"Diferencia de puntuación",
            "cambia_nivel":"Cambió de nivel", "cambia_etiqueta":"Cambió evento simulado"
        })
        st.dataframe(vista_pares, hide_index=True, use_container_width=True)
        st.download_button("Descargar comparación individual (CSV)",
            data=vista_pares.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"SIGERH_comparacion_escenarios_{conjunto}.csv", mime="text/csv")
        st.caption("Resultados exploratorios de una simulación. No interpretarlos como efectos causales ni utilizarlos para decisiones crediticias reales.")

with t7:
    st.subheader("Alcance del prototipo")
    st.markdown("""**Origen:** cartera de 100,000 créditos simulados. El MPRH genera etiquetas experimentales de incumplimiento a seis meses bajo dos escenarios.

**Clasificación:** los niveles se fijaron a partir de percentiles de puntuaciones del conjunto de validación (aproximadamente 50% bajo, 30% medio y 20% alto). No representan umbrales de aprobación crediticia.

**Cobertura:** se visualizan únicamente registros con puntuaciones disponibles en validación o prueba; no incluye entrenamiento ni todos los créditos originales.

**Análisis financiero:** se presentan medianas, distribuciones y saldos de créditos simulados con clasificación disponible. No son estimaciones poblacionales ni relaciones causales.

**Comparación de escenarios:** se emparejan los mismos créditos por identificador y conjunto; se comparan etiquetas, puntuaciones y niveles simulados. Las diferencias no son efectos causales de intervenciones ni probabilidades de incumplimiento real.

**Limitaciones:** la evaluación de prueba fue utilizada exploratoriamente en etapas anteriores; no constituye validación independiente. Las puntuaciones no están calibradas contra incumplimientos reales. No utilizar para otorgar, rechazar o reestructurar créditos.""")
