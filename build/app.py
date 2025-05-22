# build/app.py
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Chuck Norris Facts</title>
</head>
<body style="font-family:sans-serif; padding:2em;">
    <h1>💥 Chuck Norris Fact Generator</h1>
    <p>{{ fact }}</p>
    <form method="get">
        <button type="submit">🔁 Another one</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    try:
        response = requests.get("https://api.chucknorris.io/jokes/random", timeout=5)
        response.raise_for_status()
        joke = response.json()["value"]
    except Exception as e:
        joke = f"Error fetching fact: {e}"
    return render_template_string(TEMPLATE, fact=joke)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)