"""Flask ダミーECサイト — TechShop

v1/v2のUI切替機能を持つローカルECサイト。
Scraplingのスクレイピング対象として使用する。
"""

import csv
import io
import json
import os

from flask import Flask, Response, jsonify, redirect, render_template, session

app = Flask(__name__)
app.secret_key = "scrapling-demo-secret-key"

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "products.json")


def load_products() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    version = session.get("version", "v1")
    products = load_products()
    return render_template(f"{version}.html", products=products)


@app.route("/switch")
def switch_version():
    current = session.get("version", "v1")
    session["version"] = "v2" if current == "v1" else "v1"
    return redirect("/")


@app.route("/csv")
def download_csv():
    products = load_products()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "price", "category", "rating", "reviews", "description"])
    writer.writeheader()
    writer.writerows(products)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )


@app.route("/api/products")
def api_products():
    return jsonify(load_products())


@app.route("/version")
def version():
    return jsonify({"version": session.get("version", "v1")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
