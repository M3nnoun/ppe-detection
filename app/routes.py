from flask import Blueprint, render_template, request
import os
from src.detector import detect

app_routes = Blueprint("app_routes", __name__)

@app_routes.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        path = os.path.join("static/uploads", file.filename)
        file.save(path)

        results = detect(path)
        output_path = "static/uploads/result.jpg"
        results[0].save(filename=output_path)

        return render_template("result.html", image=output_path)

    return render_template("index.html")
