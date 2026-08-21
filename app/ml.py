import joblib,numpy as np
from sklearn.ensemble import IsolationForest,RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
from .config import MODEL_DIR
from .data_generator import training
from .features import add,FEATURES
VERSION="1.0.0"; AP=MODEL_DIR/"anomaly.joblib"; FP=MODEL_DIR/"failure.joblib"
def train():
    df=add(training()); X=df[FEATURES]; y=df.failure_label
    xt,xv,yt,yv=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    an=IsolationForest(n_estimators=150,contamination=.12,random_state=42).fit(xt[yt==0])
    cl=RandomForestClassifier(n_estimators=150,max_depth=12,class_weight="balanced",random_state=42).fit(xt,yt)
    pr=cl.predict(xv); pp=cl.predict_proba(xv)[:,1]
    m={"version":VERSION,"samples":len(df),"accuracy":accuracy_score(yv,pr),"precision":precision_score(yv,pr,zero_division=0),"recall":recall_score(yv,pr,zero_division=0),"f1":f1_score(yv,pr,zero_division=0),"roc_auc":roc_auc_score(yv,pp)}
    joblib.dump(an,AP); joblib.dump(cl,FP); return m
def models():
    if not AP.exists() or not FP.exists(): train()
    return joblib.load(AP),joblib.load(FP)
def predict(df):
    an,cl=models(); z=add(df)[FEATURES].iloc[[-1]]
    return float(np.clip(.5-an.decision_function(z)[0],0,1)),float(cl.predict_proba(z)[0,1])
def importance():
    _,cl=models()
    return sorted([{"feature":f,"importance":float(v)} for f,v in zip(FEATURES,cl.feature_importances_)],key=lambda x:x["importance"],reverse=True)
