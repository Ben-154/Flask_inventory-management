import argparse
import json
import os
import sys

import requests

BASE_URL = os.environ.get("INVENTORY_API_URL", "http://127.0.0.1:5000")


def api_get(path):
    response = requests.get(f"{BASE_URL}{path}", timeout=10)
    return response


def api_post(path, payload):
    response = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        timeout=10,
    )
    return response


def api_patch(path, payload):
    response = requests.patch(
        f"{BASE_URL}{path}",
        json=payload,
        timeout=10,
    )
    return response


def api_delete(path):
    response = requests.delete(f"{BASE_URL}{path}", timeout=10)
    return response


def print_response(response):
    if response.status_code >= 400:
        print(f"Error ({response.status_code}): {response.text}", file=sys.stderr)
        sys.exit(1)
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)


def cmd_list(_args):
    print_response(api_get("/inventory"))


def cmd_view(args):
    print_response(api_get(f"/inventory/{args.id}"))


def cmd_add(args):
    payload = {
        "product_name": args.name,
        "price": args.price,
        "stock": args.stock,
    }
    if args.barcode:
        payload["barcode"] = args.barcode
    if args.brand:
        payload["brands"] = args.brand
    print_response(api_post("/inventory", payload))


def cmd_update(args):
    payload = {}
    if args.name:
        payload["product_name"] = args.name
    if args.price is not None:
        payload["price"] = args.price
    if args.stock is not None:
        payload["stock"] = args.stock
    if args.barcode:
        payload["barcode"] = args.barcode
    if args.brand:
        payload["brands"] = args.brand

    if not payload:
        print("Nothing to update.", file=sys.stderr)
        sys.exit(1)

    print_response(api_patch(f"/inventory/{args.id}", payload))


def cmd_delete(args):
    print_response(api_delete(f"/inventory/{args.id}"))


def cmd_find_barcode(args):
    print_response(api_get(f"/lookup/barcode/{args.barcode}"))


def cmd_find_name(args):
    print_response(api_get(f"/lookup/search?name={args.name}"))


def cmd_import(args):
    payload = {
        "barcode": args.barcode,
        "price": args.price,
        "stock": args.stock,
    }
    print_response(api_post("/inventory/import-barcode", payload))


def main():
    parser = argparse.ArgumentParser(description="Inventory Management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all inventory items").set_defaults(func=cmd_list)

    view = sub.add_parser("view", help="View one item")
    view.add_argument("id", type=int)
    view.set_defaults(func=cmd_view)

    add = sub.add_parser("add", help="Add an item")
    add.add_argument("name")
    add.add_argument("--price", type=float, default=0)
    add.add_argument("--stock", type=int, default=0)
    add.add_argument("--barcode", default="")
    add.add_argument("--brand", default="")
    add.set_defaults(func=cmd_add)

    update = sub.add_parser("update", help="Update an item")
    update.add_argument("id", type=int)
    update.add_argument("--name", default="")
    update.add_argument("--price", type=float, default=None)
    update.add_argument("--stock", type=int, default=None)
    update.add_argument("--barcode", default="")
    update.add_argument("--brand", default="")
    update.set_defaults(func=cmd_update)

    delete = sub.add_parser("delete", help="Delete an item")
    delete.add_argument("id", type=int)
    delete.set_defaults(func=cmd_delete)

    barcode = sub.add_parser("find-barcode", help="Lookup barcode on OpenFoodFacts")
    barcode.add_argument("barcode")
    barcode.set_defaults(func=cmd_find_barcode)

    search = sub.add_parser("find-name", help="Search by name on OpenFoodFacts")
    search.add_argument("name")
    search.set_defaults(func=cmd_find_name)

    imp = sub.add_parser("import", help="Import product from barcode into inventory")
    imp.add_argument("barcode")
    imp.add_argument("--price", type=float, default=0)
    imp.add_argument("--stock", type=int, default=0)
    imp.set_defaults(func=cmd_import)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()