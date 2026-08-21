def rul(asset,last):
    base=max(48,1200-max(0,asset.operating_hours-5000)*.04); deg=max(0,last.temperature-70)*7+max(0,last.vibration-3)*60
    return round(max(8,min(1200,base-deg)),1)
def health(a,f,r,q): return round(max(0,min(100,(1-(.45*f+.3*a+.2*max(0,1-r/720)+.05*(1-q/100)))*100)),2)
def priority(asset,f,a,r,q):
    x=(.55*f+.25*a+.15*max(0,1-r/720)+.05*(1-q/100))*.75+(asset.criticality/100)*.25
    return "CRITICAL" if x>=.7 else "HIGH" if x>=.5 else "MEDIUM" if x>=.3 else "LOW"
def reasons(last,a,f,r):
    x=[]
    if f>=.65:x.append("Elevated predicted failure probability")
    if a>=.65:x.append("Telemetry pattern is anomalous")
    if last.vibration>=4:x.append("Vibration is elevated")
    if last.temperature>=85:x.append("Temperature is elevated")
    if last.flow<80:x.append("Flow is below expected range")
    if r<168:x.append("Estimated RUL is below one week")
    return x or ["No dominant degradation indicator detected"]
