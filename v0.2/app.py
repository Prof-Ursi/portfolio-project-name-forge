from flask import Flask, render_template, request, jsonify
import numpy as np
import codecs
import os

app = Flask(__name__)

DATA_DIR = "data/"
COUNT_FILE = "count.bin"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load available name lists
def get_name_lists():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

# Trains the trigram Markov model
def train_markov_model(filepath):
    count = np.zeros((256, 256, 256), dtype="int32")
    with codecs.open(filepath, "r", "utf-8") as file:
        for line in file:
            i = j = 0
            for k in [ord(c) for c in line.strip()]:
                count[i, j, k] += 1
                i, j = j, k
    count.tofile(COUNT_FILE)

# Generate names using Markov model
def generate_names(target_size, quantity, reference_list):
    count = np.fromfile(COUNT_FILE, dtype="int32").reshape(256, 256, 256)
    s = count.sum(axis=2)
    st = np.tile(s.T, (256, 1, 1)).T
    p = count.astype("float") / st
    p[np.isnan(p)] = 0

    generated_names = []
    while len(generated_names) < quantity:
        i = j = 0
        result = ""
        while not j == 10:
            k = np.random.choice(range(256), 1, p=p[i, j, :])[0]
            result += chr(k)
            i, j = j, k
        if len(result) == 1 + target_size and result[:-1] not in reference_list:
            generated_names.append(result[:-1])
    
    return generated_names

@app.route("/")
def index():
    return render_template("index.html", name_lists=get_name_lists())

@app.route("/load_names", methods=["POST"])
def load_names():
    list_name = request.form["list_name"]
    filepath = os.path.join(DATA_DIR, list_name)
    with open(filepath, "r", encoding="utf-8") as f:
        names = f.read().splitlines()
    return jsonify({"names": names})

@app.route("/generate", methods=["POST"])
def generate():
    list_name = request.form["list_name"]
    target_size = int(request.form["length"])
    quantity = int(request.form["quantity"])

    filepath = os.path.join(DATA_DIR, list_name)
    if not os.path.exists(filepath):
        return jsonify({"error": "Name list not found"}), 400

    with open(filepath, "r", encoding="utf-8") as f:
        reference_list = set(f.read().splitlines())

    train_markov_model(filepath)
    generated_names = generate_names(target_size, quantity, reference_list)

    return jsonify({"generated_names": generated_names})

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = os.path.join(DATA_DIR, file.filename)
    file.save(filename)
    return jsonify({"success": "File uploaded", "name_lists": get_name_lists()})

if __name__ == "__main__":
    app.run(debug=True)