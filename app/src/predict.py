import joblib

# Load model
model = joblib.load("../model/model.pkl")

# Sample input (change values)
sample = [[300, 310, 1500, 40, 10, 1]]

result = model.predict(sample)

if result[0] == 1:
    print("⚠️ Refinery Issue Detected")
else:
    print("✅ System Normal")