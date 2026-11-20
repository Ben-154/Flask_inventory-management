import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "inventory.json")


def _ensure_file():
    folder = os.path.dirname(DATA_FILE)
    os.makedirs(folder, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_items():
    _ensure_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_items(items):
    _ensure_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def get_all():
    return load_items()


def get_by_id(item_id):
    items = load_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def create_item(data):
    items = load_items()
    next_id = 1
    if items:
        next_id = max(i["id"] for i in items) + 1

    item = {
        "id": next_id,
        "product_name": data["product_name"],
        "barcode": data.get("barcode", ""),
        "brands": data.get("brands", ""),
        "price": float(data.get("price", 0)),
        "stock": int(data.get("stock", 0)),
    }
    items.append(item)
    save_items(items)
    return item


def update_item(item_id, changes):
    items = load_items()
    for item in items:
        if item["id"] == item_id:
            if "product_name" in changes:
                item["product_name"] = changes["product_name"]
            if "barcode" in changes:
                item["barcode"] = changes["barcode"]
            if "brands" in changes:
                item["brands"] = changes["brands"]
            if "price" in changes:
                item["price"] = float(changes["price"])
            if "stock" in changes:
                item["stock"] = int(changes["stock"])
            save_items(items)
            return item
    return None


def delete_item(item_id):
    items = load_items()
    new_items = [i for i in items if i["id"] != item_id]
    if len(new_items) == len(items):
        return False
    save_items(new_items)
    return True