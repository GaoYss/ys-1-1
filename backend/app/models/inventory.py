from datetime import datetime

from ..extensions import db


WARNING_LEVEL_NORMAL = 'normal'
WARNING_LEVEL_ATTENTION = 'attention'
WARNING_LEVEL_URGENT = 'urgent'
WARNING_LEVEL_OUT_OF_STOCK = 'out_of_stock'


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    category = db.Column(db.String(40), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    stock = db.Column(db.Float, nullable=False, default=0)
    warning_threshold = db.Column(db.Float, nullable=False, default=0)
    urgent_threshold = db.Column(db.Float, nullable=False, default=0)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship("Supplier", back_populates="ingredients")

    @property
    def warning_level(self):
        if self.stock <= 0:
            return WARNING_LEVEL_OUT_OF_STOCK
        if self.stock <= self.urgent_threshold:
            return WARNING_LEVEL_URGENT
        if self.stock <= self.warning_threshold:
            return WARNING_LEVEL_ATTENTION
        return WARNING_LEVEL_NORMAL

    @property
    def warning(self):
        return self.warning_level != WARNING_LEVEL_NORMAL

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "stock": self.stock,
            "warningThreshold": self.warning_threshold,
            "urgentThreshold": self.urgent_threshold,
            "supplierId": self.supplier_id,
            "supplierName": self.supplier.name if self.supplier else None,
            "warning": self.warning,
            "warningLevel": self.warning_level,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
