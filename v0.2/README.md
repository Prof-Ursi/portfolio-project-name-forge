# Project Structure
```
/name-generator
├── data/
│   └── sample_names.txt  # Example name list
├── static/
│   ├── images/
│   │   ├── logo.png
│   │   └── background.jpg
│   ├── styles.css     # Basic styles
│   └── script.js      # Handles UI interactions
├── templates/
│   └── index.html     # Main UI
├── app.py             # Flask backend
├── count.bin          # Binary trigram count file (generated)
├── requirements.txt   # Dependencies
└── README.md          # Project guide
```

# How to run
## 1. Install dependencies
    pip install flask numpy
    or
    pip install -r requirements.txt
## 2. Run the Flask app
    python3 app.py
## 3. Open http://127.0.0.1:5000/ in your browser.


v0.2 : basic web structure, non functional