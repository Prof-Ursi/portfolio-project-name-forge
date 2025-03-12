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

# Récupère la liste des fichiers .txt disponibles dans data/
def get_name_lists():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

# Analyse names and count each trigram letters in a 3D transition matrix
def trigram_counter(filepath):
    count = np.zeros((256,256,256), dtype='int32')

    # Ensure the count file is cleared before writing
    open(COUNT_FILE, "wb").close()

    with codecs.open(filepath, "r", "utf-8") as lines:
        for l in lines:
            i = j = 0
            for k in [ord(c) for c in list(l)]:
                count[i, j, k] += 1
                i = j
                j = k
    count.tofile(COUNT_FILE)

# Génére et renvoie en mémoire (et dans un fichier) les noms
def generate_names(target_size, quantity, filepath):
    # Dictionnaire pour s'assurer qu'on ne régénère pas un nom existant
    dico = []
    with codecs.open(filepath, "r", "utf-8") as lines:
        for l in lines:
            dico.append(l.strip())

    # On charge la matrice 3D de compte
    count = np.fromfile(COUNT_FILE, dtype="int32").reshape(256, 256, 256)
    # Sommes par plan (dernière dimension)
    s = count.sum(axis=2)
    # On évite les divisions par zéro
    st = np.tile(s.T, (256, 1, 1)).T
    p = count.astype('float') / st
    # On remplace les NaN par 0
    p[np.isnan(p)] = 0
    # (Optionnel) Normalisation supplémentaire pour s'assurer que chaque distribution
    # de p[i,j,:] sum à 1 – mais en général la division ci-dessus suffit si pas d'erreur
    for i in range(256):
        for j in range(256):
            psum = p[i, j, :].sum()
            if psum > 0:
                p[i, j, :] /= psum

    # Fichier de sortie
    outfile = "generatedNames.txt"
    f = codecs.open(outfile, "w", "utf-8")

    generated_names = []
    total = 0

    while total < quantity:
        i = j = 0
        result = u''
        # On génère caractère par caractère jusqu'à rencontrer le code ASCII 10 (LF),
        # c'est le critère actuel (ex: fin de ligne).
        while not j == 10:
            k = choice(range(256), 1, p=p[i, j, :])[0]
            result = result + chr(k)
            i = j
            j = k

        # On vérifie la taille voulue et qu'il n'est pas déjà dans la liste
        if len(result) == 1 + target_size:
            candidate = result[:-1]  # on enlève le dernier char (LF)
            if candidate in dico:
                continue
            else:
                generated_names.append(candidate)
                f.write(candidate + "\n")
                total += 1

    f.close()
    return generated_names

@app.route("/")
def index():
    return render_template("index.html", name_lists=get_name_lists())

@app.route("/load_names", methods=["POST"])
def load_names():
    list_name = request.form["list_name"]
    filepath = os.path.join(DATA_DIR, list_name)
    if not os.path.exists(filepath):
        return jsonify({"error": "List not found"}), 400
    with codecs.open(filepath, "r", "utf-8") as f:
        names = [line.strip() for line in f]
    # On (re)calcule la matrice de trigrammes pour cette liste
    trigram_counter(filepath)
    return jsonify({"names": names})

@app.route("/generate", methods=["POST"])
def generate():
    list_name = request.form["list_name"]
    target_size = int(request.form["length"])
    quantity = int(request.form["quantity"])

    filepath = os.path.join(DATA_DIR, list_name)
    if not os.path.exists(filepath):
        return jsonify({"error": "Name list not found"}), 400

    # On génère 'quantity' noms
    generated_names = generate_names(target_size, quantity, filepath)

    return jsonify({"generated_names": generated_names})

# Permet de télécharger un fichier .txt
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = os.path.join(DATA_DIR, file.filename)
    file.save(filename)
    return jsonify({"success": "File uploaded", "name_lists": get_name_lists()})

# Permet de récupérer le fichier generatedNames.txt directement
@app.route('/generatedNames.txt')
def get_generated_names():
    return send_from_directory('.', 'generatedNames.txt')

if __name__ == "__main__":
    app.run()
