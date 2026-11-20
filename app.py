from flask import Flask, jsonify, request

import openfood
import storage

app = Flask(__name__)


@app.route("/inventory", methods=["GET"])
def list_inventory():
    return jsonify(storage.get_all())


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = storage.get_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json()
    if not data or not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    item = storage.create_item(data)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    item = storage.update_item(item_id, data)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    if storage.delete_item(item_id):
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404


@app.route("/lookup/barcode/<barcode>", methods=["GET"])
def lookup_barcode(barcode):
    try:
        product = openfood.fetch_by_barcode(barcode)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


@app.route("/lookup/search", methods=["GET"])
def lookup_search():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "name query parameter is required"}), 400

    try:
        results = openfood.search_by_name(name)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(results)


@app.route("/inventory/import-barcode", methods=["POST"])
def import_from_barcode():
    data = request.get_json() or {}
    barcode = data.get("barcode", "").strip()
    if not barcode:
        return jsonify({"error": "barcode is required"}), 400

    try:
        product = openfood.fetch_by_barcode(barcode)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

    if not product:
        return jsonify({"error": "Product not found"}), 404

    item = storage.create_item({
        "product_name": product.get("product_name") or "Unknown product",
        "barcode": product.get("barcode", barcode),
        "brands": product.get("brands", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
    })
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)