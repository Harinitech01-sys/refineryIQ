import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# Load dataset (use the dataset I gave)
df = pd.read_csv("../data/dataset.csv")

# Input features
X = df[['oil_type', 'moisture', 'FFA', 'impurity']]

# Output targets (multiple outputs)
y = df[['temperature', 'catalyst_ratio', 'reaction_time', 'yield']]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model (REGRESSOR ✅)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Evaluation (use MAE instead of accuracy)
mae = mean_absolute_error(y_test, y_pred)
print("Mean Absolute Error:", mae)

# Save model
joblib.dump(model, "model.pkl")

print("✅ Biodiesel Model Trained & Saved")