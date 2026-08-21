import numpy as np
def quality(df):
    if df.empty:return {"score":0,"missing_rate":1,"range_issues":1}
    miss=float(df[["temperature","vibration","pressure","flow","rpm","power"]].isna().mean().mean())
    bad=float(((df.rpm<=0)|(df.flow<0)|(df.power<0)).mean())
    return {"score":round(max(0,min(100,100-miss*100-bad*50)),2),"missing_rate":round(miss,4),"range_issues":round(bad,4)}
def drift(df):
    if len(df)<10:return 0
    vals=[]
    for c in ["temperature","vibration","pressure","flow","power"]:
        a,b=np.array_split(df[c].to_numpy(),2); vals.append(min(1,abs(np.mean(a)-np.mean(b))/(np.std(a)+np.std(b)+1e-6)))
    return round(float(np.mean(vals)),3)
