import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, accuracy_score
FEATURES=['ingreso_mensual_mxn','monto_original_credito_mxn','pago_mensual_mxn','plazo_original_años','tasa_interes_anual']
UMBRAL_RIESGO = 0.27

def entrenar(df):
    x=df[FEATURES].apply(pd.to_numeric,errors='coerce'); y=pd.to_numeric(df.incumplimiento,errors='coerce'); ok=y.isin([0,1]); x=x[ok]; y=y[ok].astype(int)
    a,b,c,d=train_test_split(x,y,test_size=.2,random_state=42,stratify=y)
    a,v,c,w=train_test_split(a,c,test_size=.25,random_state=42,stratify=c)
    models={'Logística':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(max_iter=500)), 'Random Forest':make_pipeline(SimpleImputer(strategy='median'),RandomForestClassifier(n_estimators=80,max_depth=10,min_samples_leaf=30,n_jobs=2,random_state=42))}
    scores={}
    for k,m in models.items():
        m.fit(a,c); scores[k]=roc_auc_score(w,m.predict_proba(v)[:,1])
    best=max(scores,key=scores.get); m=models[best]; p=m.predict_proba(b)[:,1]; z=p>=UMBRAL_RIESGO
    return m, best, scores, {'AUC-ROC':roc_auc_score(d,p),'PR-AUC':average_precision_score(d,p),'Precisión':precision_score(d,z,zero_division=0),'Recall':recall_score(d,z,zero_division=0),'F1':f1_score(d,z,zero_division=0),'Exactitud':accuracy_score(d,z)}
def cuota(saldo,tasa,meses):
    r=tasa/1200
    return saldo/meses if r==0 else saldo*r/(1-(1+r)**(-meses))
