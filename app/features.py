FEATURES=["temperature","vibration","pressure","flow","rpm","current","power","ambient_temperature","temperature_roll","vibration_roll","pressure_roll","flow_roll","vibration_slope","temperature_slope","load_ratio"]
def add(df):
    x=df.copy()
    for c in ["temperature","vibration","pressure","flow"]: x[c+"_roll"]=x[c].rolling(12,min_periods=1).mean()
    for c in ["temperature","vibration"]: x[c+"_slope"]=x[c].diff(6).fillna(0)/6
    x["load_ratio"]=x["power"]/(x["rpm"].abs()+1)
    return x.fillna(0)
