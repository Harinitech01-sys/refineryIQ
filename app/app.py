from flask import Flask, render_template, request, jsonify, redirect
import joblib, os, json, mysql.connector, pandas as pd
from datetime import datetime
import requests
import hashlib # Added for Audit Hashing
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# --- RAG ENGINE SETUP ---
print("Initializing Sentinel RAG Engine...")
search_model = SentenceTransformer('all-MiniLM-L6-v2')

base_path = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(base_path, 'knowledge.json')

try:
    with open(kb_path, 'r') as f:
        kb = json.load(f)
    kb_questions = [item['question'] for item in kb]
    kb_embeddings = search_model.encode(kb_questions, convert_to_tensor=True)
    print("✔ Neural Hub Online: Knowledge Base Loaded.")
except Exception as e:
    print(f"❌ Error loading knowledge.json: {e}")
    kb = []

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="harini",
        database="refinery_db"
    )

# ---------------- MODEL LOADING ----------------
model_path = os.path.join(base_path, "src", "model.pkl")
try:
    model = joblib.load(model_path)
except Exception as e:
    model = None

# ---------------- UPDATED LANDING LOGIC ----------------

@app.route("/")
def index():
    """ 🔥 UPDATED: Landing Page (Splash Screen) """
    return render_template("newlogo.html")

@app.route("/portal")
def marketplace_home():
    """ 🔥 UPDATED: Role Selection (Buyer/Seller/Predictor) """
    return render_template("login.html")

# ---------------- NEW MARKETPLACE ROUTES ----------------

@app.route("/seller")
def seller():
    """ 🔥 SELLER PAGE FROM NEW.PY """
    return render_template("seller.html")

@app.route("/buyer")
def buyer():
    """ 🔥 BUYER PAGE FROM NEW.PY """
    return render_template("buyer.html")

@app.route("/buy", methods=["POST"])
def buy():
    """ 🔥 PURCHASE API FROM NEW.PY """
    data = request.json
    quantity = float(data.get("quantity", 0))
    price = float(data.get("price", 0))
    total = quantity * price
    return jsonify({"total": total})

# ---------------- OLD REFINERY IQ ROUTES (UNTOUCHED) ----------------

@app.route('/splash')
def splash():
    return render_template("newlogo.html")

@app.route('/chatbot')
def chatbot_page():
    return render_template("chatbot.html")

@app.route('/predictor')
def predictor_home():
    """ Your original predictor home (formerly home()) """
    return render_template("index.html")


@app.route('/results')
def results_history():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM biodiesel_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        db.close()

        if row:
            status = "OPTIMAL ✅" if float(row['yield']) > 88 else "LOW YIELD ⚠️"
            return render_template(
                "results.html",
                yield_value=row['yield'],
                temperature=row['temperature'],
                catalyst=row['catalyst_ratio'],
                reaction_time=row['reaction_time'],
                status=status,
                suggestion="Feedstock quality is excellent.",
                co2_saved="N/A",
                profit="N/A",
                compliance="N/A",
                is_compliant=False,
                audit_hash="HISTORICAL_DATA",
                rupee_savings="0.0",
                now=datetime.now().strftime("%H:%M | %d %b")
            )
        return redirect('/predictor')
    except:
        return redirect('/predictor')

@app.route('/dashboard')
def dashboard():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total, AVG(yield) as avg_yield FROM biodiesel_data")
        stats = cursor.fetchone()
        cursor.execute("SELECT yield FROM biodiesel_data ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        yield_history = [float(row['yield']) for row in rows][::-1]
        db.close()

        return render_template(
            "dashboard.html",
            total_batches=stats['total'] or 0,
            avg_eff=round(float(stats['avg_yield'] or 0), 1),
            history=yield_history
        )
    except:
        return render_template("dashboard.html", total_batches=0, avg_eff=0, history=[])

@app.route('/chat_query', methods=['POST'])
def chat_query():
    data = request.json
    user_msg = data.get('message', '')
    try:
        user_emb = search_model.encode(user_msg, convert_to_tensor=True)
        hits = util.semantic_search(user_emb, kb_embeddings, top_k=1)
        if hits[0][0]['score'] > 0.4:
            answer = kb[hits[0][0]['corpus_id']]['answer']
        else:
            answer = "No specific technical match in knowledge base."
    except Exception as e:
        answer = "Neural link fault."
    return jsonify({"answer": answer})

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template("index.html", error="Model not loaded.")
    try:
        db = get_db_connection()
        cursor = db.cursor()
        oil_map = {"veg": 0, "waste": 1, "animal": 2}
        oil_input = request.form.get('oil_type', 'veg')
        oil_type = oil_map.get(oil_input, 0)
        m = float(request.form.get('moisture', 0))
        f = float(request.form.get('FFA', 0))
        i = float(request.form.get('impurity', 0))
        batch_size = float(request.form.get('batch_size', 100))
        oil_price = float(request.form.get('oil_price', 65))
        meth_price = float(request.form.get('methanol_price', 40))

        if f > 4.5:
            safety_status, safety_advice, stress_status = "ACID TREATMENT REQUIRED 🧪", "FFA > 4.5 detects. Route through ACID REACTOR.", "UNSTABLE ⚠️"
        else:
            safety_status, safety_advice, stress_status = "DIRECT PRODUCTION ✅", "FFA levels within base-catalysis limits. Proceeding to EMR.", "STABLE ✅"

        input_data = pd.DataFrame([{'oil_type': oil_type, 'moisture': m, 'FFA': f, 'impurity': i}])
        pred = model.predict(input_data)[0]
        yield_val = round(float(pred[3]), 2)
        
        reagent_efficiency = 0.85 if f < 2.0 else 1.0
        rupee_savings = round(batch_size * 12.5 * (1 - reagent_efficiency), 2)
        produced_liters = batch_size * (yield_val / 100)
        net_profit = round((produced_liters * 98.5) - ((oil_price + (meth_price * 0.12 * reagent_efficiency) + 5.5) * batch_size), 2)

        impacts = {"Moisture": m * 2.5, "FFA": f * 1.8, "Impurity": i * 3.0}
        total_impact = sum(impacts.values()) if sum(impacts.values()) > 0 else 1
        top_factor = max(impacts, key=impacts.get)

        xai_data = {
            "top_factor": top_factor,
            "m_impact": round((impacts["Moisture"] / total_impact) * 100, 1),
            "f_impact": round((impacts["FFA"] / total_impact) * 100, 1),
            "i_impact": round((impacts["Impurity"] / total_impact) * 100, 1)
        }

        hash_string = f"{datetime.now()}-{oil_input}-{yield_val}-{f}"
        audit_hash = hashlib.sha256(hash_string.encode()).hexdigest()[:12].upper()

        res = {
            "temperature": round(float(pred[0]), 2), "catalyst": round(float(pred[1]), 2),
            "reaction_time": round(float(pred[2]), 2), "yield_value": yield_val,
            "co2_saved": round(produced_liters * 1.92, 2), "profit": net_profit, 
            "compliance": "PASS ✅" if yield_val >= 88.0 else "FAIL ❌",
            "is_compliant": yield_val >= 88.0, "audit_hash": audit_hash, "rupee_savings": rupee_savings,
            "safety_margin": round(100 - (f * 10), 1), "stress_status": stress_status,
            "now": datetime.now().strftime("%H:%M | %d %b"), **xai_data
        }

        cursor.execute("INSERT INTO biodiesel_data (oil_type, moisture, FFA, impurity, temperature, catalyst_ratio, reaction_time, yield) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                       (oil_input, m, f, i, res['temperature'], res['catalyst'], res['reaction_time'], res['yield_value']))
        db.commit()
        db.close()
        return render_template("results.html", **res, status=safety_status, suggestion=safety_advice)
    except Exception as e:
        return render_template("index.html", error=f"Backend Error: {str(e)}")

@app.route('/resolve_logic', methods=['POST'])
def resolve_logic():
    return jsonify({"new_yield": 92.5, "instruction": "AI PRESCRIPTION: Increase Temperature to 64.3°C."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)