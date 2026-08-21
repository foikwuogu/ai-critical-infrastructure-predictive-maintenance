from datetime import datetime,timezone
from sqlalchemy import DateTime,Float,Integer,String,Text,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base
def now(): return datetime.now(timezone.utc)
class Asset(Base):
    __tablename__="assets"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(120),unique=True)
    asset_type:Mapped[str]=mapped_column(String(40))
    location:Mapped[str]=mapped_column(String(80))
    criticality:Mapped[int]=mapped_column(Integer)
    operating_hours:Mapped[float]=mapped_column(Float)
    installed_year:Mapped[int]=mapped_column(Integer)
    status:Mapped[str]=mapped_column(String(30),default="operational")
class Telemetry(Base):
    __tablename__="telemetry"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    asset_id:Mapped[int]=mapped_column(Integer,index=True)
    timestamp:Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True)
    temperature:Mapped[float]=mapped_column(Float); vibration:Mapped[float]=mapped_column(Float)
    pressure:Mapped[float]=mapped_column(Float); flow:Mapped[float]=mapped_column(Float)
    rpm:Mapped[float]=mapped_column(Float); current:Mapped[float]=mapped_column(Float)
    power:Mapped[float]=mapped_column(Float); ambient_temperature:Mapped[float]=mapped_column(Float)
    scenario:Mapped[str]=mapped_column(String(50),default="normal")
class Prediction(Base):
    __tablename__="predictions"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); asset_id:Mapped[int]=mapped_column(Integer,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    model_version:Mapped[str]=mapped_column(String(30)); anomaly_score:Mapped[float]=mapped_column(Float)
    failure_probability:Mapped[float]=mapped_column(Float); rul_hours:Mapped[float]=mapped_column(Float)
    health_index:Mapped[float]=mapped_column(Float); priority:Mapped[str]=mapped_column(String(20))
    confidence:Mapped[float]=mapped_column(Float); data_quality:Mapped[float]=mapped_column(Float)
    drift_score:Mapped[float]=mapped_column(Float); reasons:Mapped[str]=mapped_column(Text)
class ModelRun(Base):
    __tablename__="model_runs"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    version:Mapped[str]=mapped_column(String(30)); samples:Mapped[int]=mapped_column(Integer)
    accuracy:Mapped[float]=mapped_column(Float); precision:Mapped[float]=mapped_column(Float)
    recall:Mapped[float]=mapped_column(Float); f1:Mapped[float]=mapped_column(Float); roc_auc:Mapped[float]=mapped_column(Float)
class MaintenanceEvent(Base):
    __tablename__="maintenance_events"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    asset_id:Mapped[int]=mapped_column(Integer); event_type:Mapped[str]=mapped_column(String(50))
    action:Mapped[str]=mapped_column(String(200)); human_reviewed:Mapped[bool]=mapped_column(Boolean,default=False)
