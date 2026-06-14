from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Ingredient, Supplier
from ..models.inventory import (
    WARNING_LEVEL_ATTENTION,
    WARNING_LEVEL_NORMAL,
    WARNING_LEVEL_OUT_OF_STOCK,
    WARNING_LEVEL_URGENT,
)

inventory_bp = Blueprint("inventory", __name__)


def _validate_ingredient(stock, warning_threshold, urgent_threshold):
    if stock < 0:
        return {"error": "当前库存必须大于等于零"}, 400
    if warning_threshold < 0:
        return {"error": "关注阈值必须大于等于零"}, 400
    if urgent_threshold < 0:
        return {"error": "紧急阈值必须大于等于零"}, 400
    if urgent_threshold > warning_threshold:
        return {"error": "紧急阈值不能大于关注阈值"}, 400
    return None


def _matches_warning_levels(item, levels):
    if not levels:
        return True
    return item.warning_level in levels


@inventory_bp.get("")
def list_ingredients():
    keyword = request.args.get("keyword", "").strip()
    warning = request.args.get("warning")
    warning_levels = request.args.getlist("warningLevel")

    if warning == "true" and not warning_levels:
        warning_levels = [
            WARNING_LEVEL_ATTENTION,
            WARNING_LEVEL_URGENT,
            WARNING_LEVEL_OUT_OF_STOCK,
        ]

    ingredients = Ingredient.query.order_by(
        Ingredient.warning_threshold.desc(), Ingredient.name
    ).all()

    if keyword:
        ingredients = [item for item in ingredients if keyword in item.name]

    if warning_levels:
        ingredients = [
            item for item in ingredients if _matches_warning_levels(item, warning_levels)
        ]

    return jsonify([item.to_dict() for item in ingredients])


@inventory_bp.get("/summary")
def inventory_summary():
    ingredients = Ingredient.query.all()
    warning_count = sum(1 for item in ingredients if item.warning)
    attention_count = sum(
        1 for item in ingredients if item.warning_level == WARNING_LEVEL_ATTENTION
    )
    urgent_count = sum(
        1 for item in ingredients if item.warning_level == WARNING_LEVEL_URGENT
    )
    out_of_stock_count = sum(
        1 for item in ingredients if item.warning_level == WARNING_LEVEL_OUT_OF_STOCK
    )
    stock_value = sum(item.stock for item in ingredients)
    return {
        "ingredientCount": len(ingredients),
        "warningCount": warning_count,
        "attentionCount": attention_count,
        "urgentCount": urgent_count,
        "outOfStockCount": out_of_stock_count,
        "totalStock": stock_value,
    }


@inventory_bp.post("")
def create_ingredient():
    data = request.get_json() or {}
    stock = float(data.get("stock", 0))
    warning_threshold = float(data.get("warningThreshold", 0))
    urgent_threshold = float(data.get("urgentThreshold", 0))

    validation_error = _validate_ingredient(stock, warning_threshold, urgent_threshold)
    if validation_error:
        return validation_error

    ingredient = Ingredient(
        name=data["name"],
        category=data["category"],
        unit=data["unit"],
        stock=stock,
        warning_threshold=warning_threshold,
        urgent_threshold=urgent_threshold,
        supplier_id=data.get("supplierId"),
    )
    db.session.add(ingredient)
    db.session.commit()
    return ingredient.to_dict(), 201


@inventory_bp.put("/<int:ingredient_id>")
def update_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    data = request.get_json() or {}

    stock = float(data.get("stock", ingredient.stock))
    warning_threshold = float(data.get("warningThreshold", ingredient.warning_threshold))
    urgent_threshold = float(data.get("urgentThreshold", ingredient.urgent_threshold))

    validation_error = _validate_ingredient(stock, warning_threshold, urgent_threshold)
    if validation_error:
        return validation_error

    ingredient.name = data.get("name", ingredient.name)
    ingredient.category = data.get("category", ingredient.category)
    ingredient.unit = data.get("unit", ingredient.unit)
    ingredient.stock = stock
    ingredient.warning_threshold = warning_threshold
    ingredient.urgent_threshold = urgent_threshold
    ingredient.supplier_id = data.get("supplierId", ingredient.supplier_id)

    db.session.commit()
    return ingredient.to_dict()


@inventory_bp.get("/options")
def ingredient_options():
    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return {
        "ingredients": [item.to_dict() for item in ingredients],
        "suppliers": [item.to_dict() for item in suppliers],
    }
