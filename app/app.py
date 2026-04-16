from flask import Flask, render_template, request, jsonify, redirect
import joblib, os, json, pandas as pd
from datetime import datetime
import hashlib

# OPTIONAL imports (wrapped safely)
try:
    import mysql.connector
except:
    mysql = None

try:
    from sentence_transformers import SentenceTransformer, util
except:
    SentenceTransformer = None
    util = None

app = Flask(__name__)

# ---------------- SAFE RAG SETUP ----------------
print("Initializing Sentinel RAG Engine...")

search_model = None
kb = []
kb_embeddings = None

base_path = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(base_path, 'knowledge.json')

def load_rag():
    global search_model, kb, kb_embeddings

    if search_model is not None:
        return  # already loaded

    try:
        if SentenceTransformer is None:
            print("⚠️ SentenceTransformer not available")
            return

        search_model = SentenceTransformer('all-MiniLM-L6-v2')

        with open(kb_path, 'r') as f:
            kb = json.load(f)

        kb_questions = [item['question'] for item in kb]
        kb_embeddings = search_model.encode(kb_questions, convert_to_tensor=True)

        print("✔ Neural Hub Online: Knowledge Base Loaded.")

    except Exception as e:
        print(f"❌ RAG Load Error: {e}")

# ---------------- SAFE DB CONNECTION ----------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASS", ""),
            database=os.environ.get("DB_NAME", "refinery_db")
        )
    except Exception as e:
        print(f"DB Error: {e}")
        return None

# ---------------- MODEL LOADING ----------------
model_path = os.path.join(base_path, "src", "model.pkl")
try:
    model = joblib.load(model_path)
except Exception as e:
    print("Model load error:", e)
    model = None

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("newlogo.html")

@app.route("/portal")
def marketplace_home():
    return render_template("login.html")

@app.route("/seller")
def seller():
    return render_template("seller.html")

@app.route("/buyer")
def buyer():
    return render_template("buyer.html")

@app.route("/buy", methods=["POST"])
def buy():
    data = request.json
    quantity = float(data.get("quantity", 0))
    price = float(data.get("price", 0))
    total = quantity * price
    return jsonify({"total": total})

@app.route('/chatbot')
def chatbot_page():
    return render_template("chatbot.html")

@app.route('/predictor')
def predictor_home():
    return render_template("index.html")

# ---------------- CHATBOT ----------------
@app.route('/chat_query', methods=['POST'])
def chat_query():
    load_rag()  # lazy load

    data = request.json
    user_msg = data.get('message', '')

    try:
        # ✅ FIXED SAFE CHECK (NO LOGIC CHANGE)
        if search_model is None or kb_embeddings is None:
            return jsonify({"answer": "AI module not ready."})

        user_emb = search_model.encode(user_msg, convert_to_tensor=True)
        hits = util.semantic_search(user_emb, kb_embeddings, top_k=1)

        if hits[0][0]['score'] > 0.4:
            answer = kb[hits[0][0]['corpus_id']]['answer']
        else:
            answer = "No specific technical match in knowledge base."

    except Exception as e:
        answer = "Neural link fault."

    return jsonify({"answer": answer})

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template("index.html", error="Model not loaded.")

    try:
        db = get_db_connection()
        cursor = db.cursor() if db else None

        oil_map = {"veg": 0, "waste": 1, "animal": 2}
        oil_input = request.form.get('oil_type', 'veg')
        oil_type = oil_map.get(oil_input, 0)

        m = float(request.form.get('moisture', 0))
        f = float(request.form.get('FFA', 0))
        i = float(request.form.get('impurity', 0))

        input_data = pd.DataFrame([{
            'oil_type': oil_type,
            'moisture': m,
            'FFA': f,
            'impurity': i
        }])

        pred = model.predict(input_data)[0]
        yield_val = round(float(pred[3]), 2)

        hash_string = f"{datetime.now()}-{oil_input}-{yield_val}-{f}"
        audit_hash = hashlib.sha256(hash_string.encode()).hexdigest()[:12].upper()

        res = {
            "yield_value": yield_val,
            "audit_hash": audit_hash,
            "now": datetime.now().strftime("%H:%M | %d %b")
        }

        if cursor:
            cursor.execute(
                "INSERT INTO biodiesel_data (oil_type, moisture, FFA, impurity, temperature, catalyst_ratio, reaction_time, yield) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (oil_input, m, f, i, pred[0], pred[1], pred[2], yield_val)
            )
            db.commit()
            db.close()

        return render_template("results.html", **res)

    except Exception as e:
        return render_template("index.html", error=str(e))

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)