from flask import Flask, render_template, request, jsonify, send_from_directory
import numpy as np
from numpy.random import choice
import codecs
import os

app = Flask(__name__)

DATA_DIR = "data/"
COUNT_FILE = "count.bin"

# Check if the "data/" directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Fetch all the .txt files available in "data/" folder
def get_name_lists():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

# Analyse names and count each trigram letters in a 3D transition matrix
def trigram_counter(filepath):
    # Initialization of the 3D matrix
    count = np.zeros((256,256,256), dtype='int32')

    # Ensure the count file is cleared before writing
    open(COUNT_FILE, "wb").close()

    # Count each name/line in the file, counting each letter trigram present
    with codecs.open(filepath, "r", "utf-8") as lines:
        for l in lines:
            i = j = 0
            for k in [ord(c) for c in list(l)]:
                count[i, j, k] += 1
                i = j
                j = k
    count.tofile(COUNT_FILE)

# Generate and return in memory (and in a file) the names based on the transition matrix
def generate_names(target_size, quantity, filepath):
    # Dictionary to ensure we don't generate an existing name
    dico = []
    with codecs.open(filepath, "r", "utf-8") as lines:
        for l in lines:
            dico.append(l.strip())

    # The transition matrix is loaded from the file
    count = np.fromfile(COUNT_FILE, dtype="int32").reshape(256, 256, 256)
    # Calculating the sum of each plane (second dimension of the matrix)
    plane_sum = count.sum(axis=2)
    # We avoid division by zero using a double transpose with the Numpy T function
    tile_sum = np.tile(plane_sum.T, (256, 1, 1)).T
    # We calculate the probabilities of each trigram in each tile of the matrix
    tile_proba = count.astype('float') / tile_sum
    # The NaN values are replaced by 0
    tile_proba[np.isnan(tile_proba)] = 0
    # (Optionnal) Additional normalization to ensure that each distribution of p[i,j,:] sums to 1
    for i in range(256):
        for j in range(256):
            psum = tile_proba[i, j, :].sum()
            if psum > 0:
                tile_proba[i, j, :] /= psum

    outfile = "generatedNames.txt"
    
    f = codecs.open(outfile, "w", "utf-8")

    generated_names = []
    total = 0

    while total < quantity:
        i = j = 0
        result = u''
        # Generation of each character until the ASCII code 10 (end of line) is reached
        while not j == 10:
            k = choice(range(256), 1, p=tile_proba[i, j, :])[0]
            result = result + chr(k)
            i = j
            j = k

        # we check if the generated name is the right size and already in the dictionary
        if len(result) == 1 + target_size:
            candidate = result[:-1]  # we remove the end of line character
            if candidate in dico: # if the name is already in the dictionary, we skip it
                continue
            else:
                generated_names.append(candidate)
                f.write(candidate + "\n")
                total += 1

    f.close()
    generated_names.sort()
    return generated_names

@app.route("/")
def index():
    return render_template("index.html", name_lists=get_name_lists())


# Allow to load names from a .txt file
@app.route("/load_names", methods=["POST"])
def load_names():
    list_name = request.form["list_name"]
    filepath = os.path.join(DATA_DIR, list_name)
    if not os.path.exists(filepath):
        return jsonify({"error": "List not found"}), 400
    with codecs.open(filepath, "r", "utf-8") as f:
        names = [line.strip() for line in f]
    trigram_counter(filepath)
    return jsonify({"names": names})

# Allow to generate names based on the loaded list
@app.route("/generate", methods=["POST"])
def generate():
    list_name = request.form["list_name"]
    target_size = int(request.form["length"])
    quantity = int(request.form["quantity"])

    filepath = os.path.join(DATA_DIR, list_name)
    if not os.path.exists(filepath):
        return jsonify({"error": "Name list not found"}), 400

    generated_names = generate_names(target_size, quantity, filepath)

    return jsonify({"generated_names": generated_names})

# Allow to download a .txt file
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = os.path.join(DATA_DIR, file.filename)
    file.save(filename)
    return jsonify({"success": "File uploaded", "name_lists": get_name_lists()})

# Allow to fecover the generatedNames.txt file directly
@app.route('/generatedNames.txt')
def get_generated_names():
    return send_from_directory('.', 'generatedNames.txt')

if __name__ == "__main__":
    app.run()
