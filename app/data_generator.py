from datetime import datetime,timedelta,timezone
import numpy as np,pandas as pd
BASE={"pump":(62,2.0,105,100,1750,42,75),"compressor":(70,2.4,135,115,2100,55,95),"turbine":(76,2.2,150,130,3000,65,120),"generator":(68,1.8,110,90,1800,58,100)}
def generate(asset_type="pump",steps=120,scenario="normal",seed=42):
    rng=np.random.default_rng(seed); t0=datetime.now(timezone.utc)-timedelta(hours=steps); b=BASE[asset_type]; rows=[]
    for i in range(steps):
        x=i/max(1,steps-1); d=max(0,(x-.45)/.55) if scenario in {"bearing_degradation","pump_cavitation"} else (max(0,(x-.35)/.65) if scenario=="compressor_overheat" else 0)
        temp=b[0]+rng.normal(0,1.4)+d*18; vib=b[1]+rng.normal(0,.12)+d*2.8; pressure=b[2]+rng.normal(0,2); flow=b[3]+rng.normal(0,2.2); rpm=b[4]+rng.normal(0,25); current=b[5]+rng.normal(0,1.3)+d*7; power=b[6]+rng.normal(0,2)+d*10
        if scenario=="pump_cavitation": pressure+=rng.normal(0,7*d); flow-=d*18; vib+=d*2
        if scenario=="compressor_overheat": temp+=d*12; power+=d*12
        if scenario=="sensor_drift": temp+=x*8; vib+=x*.8
        rows.append([t0+timedelta(hours=i),temp,vib,pressure,flow,rpm,current,power,25+rng.normal(0,1),scenario])
    return pd.DataFrame(rows,columns=["timestamp","temperature","vibration","pressure","flow","rpm","current","power","ambient_temperature","scenario"])
def training(n=24,steps=120):
    fs=[]; scenarios=["normal","normal","normal","bearing_degradation","pump_cavitation","compressor_overheat"]; types=list(BASE)
    for i in range(n):
        s=scenarios[i%len(scenarios)]; df=generate(types[i%4],steps,s,100+i); df["failure_label"]=((s!="normal")&(df.index>steps*.60)).astype(int); fs.append(df)
    return pd.concat(fs,ignore_index=True)
