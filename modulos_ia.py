import pandas as pd
import streamlit as st
import unicodedata
from motor import entrenar, FEATURES, cuota, UMBRAL_RIESGO

@st.cache_resource(show_spinner='Entrenando experimento independiente...')
def modelo(df):
    return entrenar(df)

def prediccion(cartera):
    st.header('Clasificador experimental independiente')
    st.warning('Etiqueta original incumplimiento de la cartera sintética; no equivale al evento MPRH a seis meses. Sin validación real ni garantía temporal.')
    if st.button('Entrenar / recuperar modelo', key='ia_train'):
        st.session_state['ia_ready']=True
    if not st.session_state.get('ia_ready'): return
    m,n,v,t=modelo(cartera[FEATURES+['incumplimiento']])
    st.write('Modelo seleccionado por AUC de validación:',n)
    st.dataframe(pd.DataFrame([v],index=['AUC validación']))
    st.dataframe(pd.DataFrame([t],index=[f'Prueba, umbral {UMBRAL_RIESGO:.2f}']))
    st.caption('División aleatoria estratificada 60/20/20; no es evaluación temporal. PR-AUC se reporta como precisión promedio.')
    labels=['Ingreso mensual MXN','Monto original MXN','Pago mensual MXN','Plazo original (años)','Tasa anual (%)']
    with st.form('ia_form'):
        values=[st.number_input(label,min_value=0.0,value=float(pd.to_numeric(cartera[f],errors='coerce').median()),key='ia_'+f) for f,label in zip(FEATURES,labels)]
        submitted=st.form_submit_button('Calcular puntuación')
    if submitted:
        if any(x<=0 for x in values[:4]): st.error('Los primeros cuatro valores deben ser positivos.'); return
        x=pd.DataFrame([values],columns=FEATURES)
        if any(not pd.to_numeric(cartera[f],errors='coerce').min()<=x[f].iloc[0]<=pd.to_numeric(cartera[f],errors='coerce').max() for f in FEATURES): st.warning('Caso fuera del rango observado; interpretación especialmente limitada.')
        p = float(m.predict_proba(x)[0,1])
        st.metric('Puntuación experimental (no calibrada)', f'{p:.2%}')
        st.write(f'Umbral de alerta: {UMBRAL_RIESGO:.0%}')

        if p >= UMBRAL_RIESGO:
            st.warning('Alerta preventiva: requiere revisión humana.')
        else:
            st.info('Sin alerta según el umbral experimental. No garantiza ausencia de riesgo.')

        st.caption('Umbral seleccionado mediante F1 en validación. No utilizar para rechazar créditos ni tomar decisiones automatizadas.')

def norm(x):
    return ''.join(c for c in unicodedata.normalize('NFD',str(x).lower()) if unicodedata.category(c)!='Mn')

def respuesta(q,cartera,d,escenario,conjunto,ctx=None):
    import re
    ctx = {} if ctx is None else ctx
    qn=norm(q).strip(); conceptual=bool(re.search(r'\b(que es|que significa|define|explica|como se calcula)\b',qn))
    alcs=[a for a in cartera.alcaldia.dropna().unique() if re.search(r'\b'+re.escape(norm(a))+r'\b',qn)]
    if not alcs and re.match(r'^(¿?y\b|tambien\b)',qn): alcs=ctx.get('alcs',[])
    if 'toda la cartera' in qn or 'general' in qn: alcs=[]
    def money(n): return f'${n:,.2f} MXN'
    def num(pattern):
        m=re.search(pattern+r'\s*(?:de\s+)?\$?\s*([\d,]+(?:\.\d+)?)',qn)
        return float(m.group(1).replace(',','')) if m else None
    ingreso=num(r'(?:gano|ingreso(?: mensual)?(?: es)?)'); pago=num(r'(?:pago(?: mensual)?(?: es)?)')
    if ingreso is not None or pago is not None:
        if ingreso is not None: ctx['ingreso']=ingreso
        if pago is not None: ctx['pago']=pago
        i,p=ctx.get('ingreso'),ctx.get('pago')
        if i is not None and p is not None and i>0:
            return f'Tu carga hipotecaria hipotética es {100*p/i:.2f}%. Después del pago quedan {money(i-p)} antes de otros gastos. No es una probabilidad de incumplimiento.'
        return 'Indica ingreso mensual positivo y pago mensual en pesos, por ejemplo: gano 15000 y pago 5000.'
    if re.search(r'\buma\b',qn):
        return 'La Unidad de Medida y Actualización (UMA) es una referencia económica cuyo valor determina el INEGI cada año. En créditos denominados en UMA, los pagos y saldos en pesos pueden variar según el contrato. Consulta el simulador con el valor contractual de la unidad y su periodicidad; no se proyecta la indexación futura.'
    if any(w in qn for w in ['reestructur','condonacion','ampliacion','alternativas','simulador','mensualidad hipotetica']):
        s=num(r'saldo'); t=num(r'tasa(?: anual)?'); m=num(r'plazo(?: restante)?'); nuevo=num(r'nuevo plazo'); quita=num(r'condonacion')
        if s is not None: ctx['saldo']=s
        if t is not None: ctx['tasa']=t
        if m is not None: ctx['plazo']=m
        s,t,m=ctx.get('saldo'),ctx.get('tasa'),ctx.get('plazo')
        if s is not None and t is not None and m is not None and s>=0 and 0<=t<=100 and 1<=m<=600 and m.is_integer():
            n=nuevo if nuevo is not None else m; k=quita or 0
            if 1<=n<=600 and n.is_integer() and 0<=k<=100:
                a,b=cuota(s,t,int(m)),cuota(s*(1-k/100),t,int(n))
                return f'Cuota de referencia: {money(a)}; cuota propuesta: {money(b)}. Total futuro: {money(b*n)} frente a {money(a*m)}. Supuesto de tasa fija, sin seguros, comisiones ni indexación. No es una oferta.'
        return 'Podemos comparar ampliación del plazo, conversión a pesos y condonación parcial. Para un cálculo de cuota fija escribe: saldo 500000 tasa 8 plazo 120 nuevo plazo 180 condonación 10. Los plazos se expresan en meses; la tasa y la condonación en porcentajes. También puedes usar la pestaña Simulador.'
    if any(w in qn for w in ['auc','recall','precision','exactitud','random forest','f1','puntuacion','regresion']):
        return 'AUC-ROC mide discriminación entre etiquetas; recall mide la proporción de positivos detectados; precisión mide qué proporción de alertas son positivas; F1 combina precisión y recall. Exactitud mide aciertos totales. Random Forest combina árboles. La puntuación de Predicción IA no está calibrada como probabilidad real. Consulta las métricas vigentes en esa pestaña; no equivalen al MPRH a seis meses.'
    term=next((k for k,words in [('riesgo',['riesgo alto','mprh','nivel alto','escenario']),('incumplimiento',['incumplimiento']),('carga',['carga']),('ingreso',['ingreso']),('pago',['pago','mensualidad']),('saldo',['saldo']),('cantidad',['cuantos','creditos','cartera'])] if any(w in qn for w in words)),None)
    if term is None and (alcs or re.match(r'^¿?y\b',qn)): term=ctx.get('term')
    if term is None: return 'Puedo explicar UMA, carga financiera, incumplimiento y métricas; consultar cifras por alcaldía; comparar dos alcaldías y calcular cuotas hipotéticas. Prueba: ingreso promedio en Iztapalapa.'
    ctx.update(term=term,alcs=alcs)
    mode='promedio' if 'promedio' in qn else 'total' if 'total' in qn and term=='saldo' else ctx.get('mode','mediana') if re.match(r'^¿?y\b',qn) else 'mediana'
    if mode=='total' and term!='saldo': mode='mediana'
    ctx['mode']=mode
    defs={'riesgo':'Nivel alto MPRH: grupo superior definido mediante percentiles de validación; no es una categoría de riesgo real.','incumplimiento':'Incumplimiento hipotecario significa no cumplir las obligaciones de pago según el contrato. La etiqueta original de SIGERH es sintética y no equivale al evento MPRH a seis meses.','carga':'Carga financiera hipotecaria = pago mensual / ingreso mensual × 100. No incluye necesariamente otras deudas.'}
    lines=[defs[term]] if conceptual and term in defs else []
    for a in alcs or [None]:
        v=cartera if a is None else cartera[cartera.alcaldia.eq(a)]
        nombre=a or 'Cartera completa'; prefix=f'{nombre} (datos sintéticos, {len(v):,} registros): '
        if term=='riesgo':
            w=d if a is None else d[d.alcaldia.eq(a)]; k=w.nivel_experimental.eq('Alto').sum()
            lines.append(f'{nombre}: MPRH {escenario}/{conjunto}, filtros activos: {k:,} de {len(w):,} créditos de nivel alto'+(f' ({k/len(w):.2%}).' if len(w) else '. Sin registros.')); continue
        if term=='cantidad': lines.append(prefix+f'{len(v):,} créditos.'); continue
        col={'incumplimiento':'incumplimiento','carga':'carga_pago_pct','ingreso':'ingreso_mensual_mxn','pago':'pago_mensual_mxn','saldo':'saldo_actual_mxn'}[term]
        x=pd.to_numeric(v[col],errors='coerce').dropna()
        if not len(x): lines.append(prefix+'sin datos válidos.'); continue
        if term=='incumplimiento': lines.append(prefix+f'frecuencia de etiqueta original {x.mean():.2%}. No es un pronóstico.'); continue
        val=x.mean() if mode=='promedio' else x.sum() if mode=='total' else x.median()
        lines.append(prefix+f'{term} ({mode}, n={len(x):,}): '+(f'{val:.2f}%' if term=='carga' else money(val))+'.')
    return '\n\n'.join(lines)

def chatbot(cartera,d,escenario,conjunto):
    st.header('SIGERH IA — asistente hipotecario')
    st.caption('Asistente por reglas, sin API. Datos sintéticos; no es asesoría financiera. Las consultas MPRH respetan filtros activos.')
    h=st.session_state.setdefault('ia_chat',[])
    ctx=st.session_state.setdefault('ia_context_v11',{})
    if st.button('Limpiar conversación',key='chat_v11_clear'):
        h.clear(); ctx.clear(); st.rerun()
    for rol,msg in h:
        with st.chat_message(rol): st.write(msg)
    # En un contenedor, el campo no se fija al pie oscuro de Streamlit.
    with st.container():
        q=st.chat_input('Ej. Compara ingreso promedio en Iztapalapa y Coyoacán',key='chat_v11_input')
    if q:
        r=respuesta(q,cartera,d,escenario,conjunto,ctx); h.extend([('user',q),('assistant',r)])
        st.rerun()

def simulador():
    st.header('Simulador financiero hipotético')
    st.caption('Amortización fija en pesos, sin comisiones, seguros ni indexación futura. No constituye oferta ni recomendación.')
    unidad=st.radio('Unidad del saldo',['MXN','UMA'],key='sim_unidad')
    saldo=st.number_input('Saldo en unidad seleccionada',min_value=0.,value=500000. if unidad=='MXN' else 150.)
    if unidad=='UMA': saldo*=st.number_input('Valor en MXN de la unidad UMA contractual (misma periodicidad)',min_value=0.01,value=3000.)
    tasa=st.number_input('Tasa anual nominal actual (%)',0.,100.,8.)
    meses=st.number_input('Meses restantes',1,600,120)
    nueva=st.number_input('Tasa anual nominal propuesta (%)',0.,100.,8.)
    plazo=st.number_input('Nuevo plazo (meses)',1,600,180)
    quita=st.slider('Condonación hipotética del saldo (%)',0,100,0)
    ingreso=st.number_input('Ingreso mensual MXN',min_value=1.,value=15000.)
    casos=[('Referencia fija en pesos',saldo,tasa,meses),('Conversión a pesos',saldo,nueva,meses),('Conversión y ampliación',saldo,nueva,plazo),('Conversión, plazo y condonación',saldo*(1-quita/100),nueva,plazo)]
    rows=[]
    for nombre,s,t,m in casos:
        c=cuota(s,t,m); rows.append([nombre,s,c,c*m,c*m-s,100*c/ingreso])
    st.dataframe(pd.DataFrame(rows,columns=['Escenario','Saldo MXN','Mensualidad MXN','Total futuro MXN','Intereses MXN','Carga %']).round(2),hide_index=True)
    st.caption('La referencia no proyecta la evolución de UMA. Una mensualidad menor puede aumentar el costo total. La condonación requiere autorización institucional.')
