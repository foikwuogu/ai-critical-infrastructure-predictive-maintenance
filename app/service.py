import json,pandas as pd
from sqlalchemy import select
from .models import Asset,Telemetry,Prediction,ModelRun,MaintenanceEvent
from .data_generator import generate,BASE
from .ml import train,predict,importance,VERSION
from .monitoring import quality,drift
from .decision import rul,health,priority,reasons
def seed_assets(db):
    if db.scalar(select(Asset.id).limit(1)) is not None:return
    vals=[("Pump-101","pump","Plant-A",95,6200,2018),("Pump-102","pump","Plant-A",75,4100,2020),("Compressor-201","compressor","Plant-B",98,8400,2016),("Turbine-301","turbine","Plant-C",100,11200,2014),("Generator-401","generator","Plant-C",90,7200,2017),("Pump-103","pump","Plant-B",70,2800,2021),("Compressor-202","compressor","Plant-B",88,5300,2019),("Generator-402","generator","Plant-A",80,4600,2020)]
    db.add_all([Asset(name=n,asset_type=t,location=l,criticality=c,operating_hours=h,installed_year=y) for n,t,l,c,h,y in vals]);db.commit()
def seed_telemetry(db,scenario="healthy_fleet",steps=120):
    sm={"healthy_fleet":"normal","bearing_degradation":"bearing_degradation","pump_cavitation":"pump_cavitation","compressor_overheat":"compressor_overheat","sensor_drift":"sensor_drift"}; s=sm[scenario]
    for i,a in enumerate(db.scalars(select(Asset).order_by(Asset.id)).all()):
        local="normal"
        if scenario=="bearing_degradation" and a.asset_type in {"pump","generator"}:local=s
        if scenario=="pump_cavitation" and a.asset_type=="pump":local=s
        if scenario=="compressor_overheat" and a.asset_type=="compressor":local=s
        if scenario=="sensor_drift":local=s
        db.query(Telemetry).filter(Telemetry.asset_id==a.id).delete()
        df=generate(a.asset_type,steps,local,900+i)
        db.add_all([Telemetry(asset_id=a.id,timestamp=r.timestamp,temperature=r.temperature,vibration=r.vibration,pressure=r.pressure,flow=r.flow,rpm=r.rpm,current=r.current,power=r.power,ambient_temperature=r.ambient_temperature,scenario=r.scenario) for _,r in df.iterrows()])
    db.commit()
def df_for(db,aid):
    rs=db.scalars(select(Telemetry).where(Telemetry.asset_id==aid).order_by(Telemetry.timestamp)).all()
    return pd.DataFrame([{"timestamp":r.timestamp,"temperature":r.temperature,"vibration":r.vibration,"pressure":r.pressure,"flow":r.flow,"rpm":r.rpm,"current":r.current,"power":r.power,"ambient_temperature":r.ambient_temperature} for r in rs])
def predict_asset(db,aid):
    a=db.get(Asset,aid); df=df_for(db,aid)
    if not a or df.empty:raise ValueError("Asset or telemetry not found")
    an,f=predict(df); q=quality(df); d=drift(df); rr=rul(a,df.iloc[-1]); h=health(an,f,rr,q["score"]); p=priority(a,f,an,rr,q["score"]); rs=reasons(df.iloc[-1],an,f,rr); conf=round(max(0,min(1,1-d*.3-abs(f-.5)*.2)),3)
    db.add(Prediction(asset_id=aid,model_version=VERSION,anomaly_score=an,failure_probability=f,rul_hours=rr,health_index=h,priority=p,confidence=conf,data_quality=q["score"],drift_score=d,reasons=json.dumps(rs)))
    if p in {"HIGH","CRITICAL"}:db.add(MaintenanceEvent(asset_id=aid,event_type="prediction",action=f"Review predictive-maintenance recommendation: {p}"))
    db.commit()
    return {"asset_id":aid,"asset_name":a.name,"model_version":VERSION,"anomaly_score":round(an,4),"failure_probability":round(f,4),"rul_hours":rr,"health_index":h,"priority":p,"confidence":conf,"data_quality":q["score"],"drift_score":d,"reasons":rs}
def fleet(db):return [predict_asset(db,a.id) for a in db.scalars(select(Asset).order_by(Asset.id)).all()]
def dashboard(db):
    out=[]
    for a in db.scalars(select(Asset).order_by(Asset.id)).all():
        p=db.scalars(select(Prediction).where(Prediction.asset_id==a.id).order_by(Prediction.id.desc())).first()
        out.append({"id":a.id,"name":a.name,"type":a.asset_type,"location":a.location,"criticality":a.criticality,"health_index":p.health_index if p else None,"failure_probability":p.failure_probability if p else None,"rul_hours":p.rul_hours if p else None,"priority":p.priority if p else "NOT_RUN","anomaly_score":p.anomaly_score if p else None,"data_quality":p.data_quality if p else None,"drift_score":p.drift_score if p else None})
    ps=[x for x in out if x["health_index"] is not None]
    return {"metrics":{"assets":len(out),"predicted":len(ps),"critical":sum(x["priority"]=="CRITICAL" for x in ps),"high":sum(x["priority"]=="HIGH" for x in ps),"average_health":round(sum(x["health_index"] for x in ps)/len(ps),2) if ps else 0,"average_failure_probability":round(sum(x["failure_probability"] for x in ps)/len(ps),4) if ps else 0},"assets":out}
