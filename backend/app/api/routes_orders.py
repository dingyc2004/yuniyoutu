from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException

from app.data.json_store import load_collection, save_collection
from app.schemas.order import OrderAction, OrderCreate

router = APIRouter()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/users/{user_id}/orders")
async def list_orders(user_id: str) -> dict:
    items = [item for item in load_collection("orders") if item.get("user_id") == user_id]
    return {"data": sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)}


@router.post("/orders", status_code=201)
async def create_order(payload: OrderCreate = Body(...)) -> dict:
    equipment = next(
        (item for item in load_collection("equipment") if item.get("id") == payload.equipment_id),
        None,
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    now = _now()
    order = {
        "id": f"order_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        "user_id": payload.user_id,
        "equipment_id": equipment["id"],
        "equipment_name": equipment["name"],
        "merchant_name": equipment.get("merchant_name"),
        "unit_price": equipment.get("price", 0),
        "quantity": payload.quantity,
        "total_amount": round(equipment.get("price", 0) * payload.quantity, 2),
        "status": "pending_payment",
        "created_at": now,
        "updated_at": now,
    }
    orders = load_collection("orders")
    orders.append(order)
    save_collection("orders", orders)
    return {"data": order}


@router.post("/orders/{order_id}/pay")
async def pay_order(order_id: str, payload: OrderAction = Body(...)) -> dict:
    orders = load_collection("orders")
    for order in orders:
        if order.get("id") == order_id and order.get("user_id") == payload.user_id:
            if order.get("status") == "cancelled":
                raise HTTPException(status_code=409, detail="Cancelled order cannot be paid")
            order["status"] = "paid_demo"
            order["paid_at"] = _now()
            order["updated_at"] = _now()
            save_collection("orders", orders)
            return {"data": order}
    raise HTTPException(status_code=404, detail="Order not found")


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, user_id: str = "demo_user") -> dict:
    orders = load_collection("orders")
    for order in orders:
        if order.get("id") == order_id and order.get("user_id") == user_id:
            order["status"] = "cancelled"
            order["updated_at"] = _now()
            save_collection("orders", orders)
            return {"data": order}
    raise HTTPException(status_code=404, detail="Order not found")
