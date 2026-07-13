from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (JSON, Boolean, DateTime, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)



class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="operator")  # admin|manager|operator
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuditLog(Base):
    """Kim, ne zaman, neyi yaptı — güvenlik modülünün izleme kaydı."""
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(128))
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)



class Device(Base):
    """Depoya bağlı sensör / kamera / IoT cihazı."""
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    kind: Mapped[str] = mapped_column(String(32))  # temperature|humidity|light|camera
    zone: Mapped[str] = mapped_column(String(64), default="A")
    pos_x: Mapped[float] = mapped_column(Float, default=0.0)
    pos_y: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    readings: Mapped[list["SensorReading"]] = relationship(back_populates="device")


class SensorReading(Base):
    """Zaman serisi ölçüm kaydı."""
    __tablename__ = "sensor_readings"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    metric: Mapped[str] = mapped_column(String(32))     # temperature|humidity|light
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16), default="")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    device: Mapped[Device] = relationship(back_populates="readings")




class Product(Base):
    """Ürün — etiketlenebilir özellikleri ile (şekil, boyut, ağırlık)."""
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64), default="genel")
    weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    volume_m3: Mapped[float] = mapped_column(Float, default=0.0)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)   # şekil, kırılgan, vb.
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    storage_cost_per_day: Mapped[float] = mapped_column(Float, default=0.0)
    reorder_point: Mapped[int] = mapped_column(Integer, default=10)


class StockItem(Base):
    """ANLIK DURUM: bir ürünün belirli bir bölgedeki güncel miktarı."""
    __tablename__ = "stock_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    zone: Mapped[str] = mapped_column(String(64), default="A")
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    stored_since: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    product: Mapped[Product] = relationship()


class StockMovement(Base):
    """OLAY DEFTERİ: her giriş/çıkış/transfer. Tahminleme modülünün ana girdisi."""
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))   # in|out|transfer
    quantity: Mapped[int] = mapped_column(Integer)
    zone: Mapped[str] = mapped_column(String(64), default="A")
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    product: Mapped[Product] = relationship()


class PurchaseOrder(Base):
    """Tedarik siparişi — durum makinesi ile takip edilir."""
    __tablename__ = "purchase_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier: Mapped[str] = mapped_column(String(128))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    # draft -> ordered -> shipped -> received | cancelled
    expected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    product: Mapped[Product] = relationship()




class RiskEvent(Base):
    """Kaza Önleme ve Uyarı Modülü (2.4.1) çıktısı."""
    __tablename__ = "risk_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    risk_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))    # low|medium|high|critical
    zone: Mapped[str] = mapped_column(String(64), default="A")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class MovementTrace(Base):
    """Haritalama ve Tespit Modülü (2.4.2) çıktısı."""
    __tablename__ = "movement_traces"
    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(32))  # person|forklift|pallet|box
    grid_x: Mapped[int] = mapped_column(Integer)
    grid_y: Mapped[int] = mapped_column(Integer)
    zone: Mapped[str] = mapped_column(String(64), default="A")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Forecast(Base):
    """Analiz ve Tahminleme Modülü (2.4.3) çıktısı."""
    __tablename__ = "forecasts"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, default=7)
    predicted_demand: Mapped[float] = mapped_column(Float)
    lower_bound: Mapped[float] = mapped_column(Float, default=0.0)
    upper_bound: Mapped[float] = mapped_column(Float, default=0.0)
    model_name: Mapped[str] = mapped_column(String(64), default="linear")
    mae: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    product: Mapped[Product] = relationship()


class Recommendation(Base):
    """Raporlama ve Öneri Modülü (2.4.4) çıktısı."""
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(64))   # reorder|relocate|environment|safety
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    title: Mapped[str] = mapped_column(String(255))
    rationale: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


__all__ = [
    "User", "AuditLog", "Device", "SensorReading", "Product", "StockItem",
    "StockMovement", "PurchaseOrder", "RiskEvent", "MovementTrace",
    "Forecast", "Recommendation",
]