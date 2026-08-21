from pathlib import Path
from fastapi import FastAPI,Depends,HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import Base,engine,SessionLocal,get_db
from .config import APP_NAME,APP_VERSION
from .models import Asset,Telemetry,ModelRun,MaintenanceEvent,Prediction
from .service import seed_assets,seed_telemetry,df_for,predict_asset,fleet,dashboard
from .ml import train,importance,VERSION
from .monitoring import quality,drift
Base.metadata.create_all(bind=engine)
app=FastAPI(title=APP_NAME,version=APP_VERSION)
@app.on_event("startup")
def startup():
    db=SessionLocal()
    try:
        seed_assets(db);seed_telemetry(db);train()
        if db.scalar(select(Prediction.id).limit(1)) is None:fleet(db)
    finally:db.close()
@app.get("/",include_in_schema=False)
def home():return FileResponse(Path(__file__).parent/"static/index.html")
@app.get("/api/health")
def health():return {"status":"ok","service":APP_NAME,"version":APP_VERSION}
@app.get("/api/assets")
def assets(db:Session=Depends(get_db)):return db.scalars(select(Asset).order_by(Asset.id)).all()
@app.get("/api/dashboard")
def dash(db:Session=Depends(get_db)):return dashboard(db)
@app.get("/api/telemetry/latest")
def latest(db:Session=Depends(get_db)):
    out=[]
    for a in db.scalars(select(Asset).order_by(Asset.id)).all():
        r=db.scalars(select(Telemetry).where(Telemetry.asset_id==a.id).order_by(Telemetry.timestamp.desc())).first()
        if r:out.append({"asset_id":a.id,"asset_name":a.name,"timestamp":r.timestamp.isoformat(),"temperature":r.temperature,"vibration":r.vibration,"pressure":r.pressure,"flow":r.flow,"rpm":r.rpm,"power":r.power,"scenario":r.scenario})
    return out
@app.get("/api/assets/{aid}/telemetry")
def telemetry(aid:int,db:Session=Depends(get_db)):
    if not db.get(Asset,aid):raise HTTPException(404,"Asset not found")
    return [dict(timestamp=r.timestamp.isoformat(),temperature=r.temperature,vibration=r.vibration,pressure=r.pressure,flow=r.flow,rpm=r.rpm,current=r.current,power=r.power,scenario=r.scenario) for r in db.scalars(select(Telemetry).where(Telemetry.asset_id==aid).order_by(Telemetry.timestamp)).all()]
@app.post("/api/predict/{aid}")
def pred(aid:int,db:Session=Depends(get_db)):
    try:return predict_asset(db,aid)
    except ValueError as e:raise HTTPException(404,str(e))
@app.post("/api/predict/fleet")
def predfleet(db:Session=Depends(get_db)):return fleet(db)
@app.post("/api/model/train")
def modeltrain(db:Session=Depends(get_db)):
    m=train();db.add(ModelRun(version=m["version"],samples=m["samples"],accuracy=m["accuracy"],precision=m["precision"],recall=m["recall"],f1=m["f1"],roc_auc=m["roc_auc"]));db.commit();return m
@app.get("/api/model/status")
def status(db:Session=Depends(get_db)):
    r=db.scalars(select(ModelRun).order_by(ModelRun.id.desc())).first()
    return {"version":VERSION,"latest_run":None if not r else {"samples":r.samples,"accuracy":r.accuracy,"precision":r.precision,"recall":r.recall,"f1":r.f1,"roc_auc":r.roc_auc},"feature_importance":importance()[:12]}
@app.get("/api/data-quality")
def dq(db:Session=Depends(get_db)):return [{"asset_id":a.id,"asset_name":a.name,**quality(df_for(db,a.id))} for a in db.scalars(select(Asset).order_by(Asset.id)).all()]
@app.get("/api/model-monitoring")
def mm(db:Session=Depends(get_db)):return [{"asset_id":a.id,"asset_name":a.name,"drift_score":drift(df_for(db,a.id))} for a in db.scalars(select(Asset).order_by(Asset.id)).all()]
@app.get("/api/maintenance-events")
def events(db:Session=Depends(get_db)):return db.scalars(select(MaintenanceEvent).order_by(MaintenanceEvent.id.desc()).limit(100)).all()
@app.post("/api/scenarios/{scenario}")
def scenario(scenario:str,db:Session=Depends(get_db)):
    if scenario not in {"healthy_fleet","bearing_degradation","pump_cavitation","compressor_overheat","sensor_drift"}:raise HTTPException(404,"Unknown scenario")
    seed_telemetry(db,scenario,120);return {"scenario":scenario,"predictions":fleet(db)}
@app.post("/api/demo/reset")
def reset(db:Session=Depends(get_db)):
    db.query(Prediction).delete();db.query(MaintenanceEvent).delete();db.query(Telemetry).delete();db.commit();seed_assets(db);seed_telemetry(db);return {"status":"reset","predictions":fleet(db)}
