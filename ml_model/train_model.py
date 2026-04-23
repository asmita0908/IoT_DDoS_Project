import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
import joblib

data = []
labels = []

# Normal traffic
for _ in range(200):
    requests = random.randint(10, 100)
    data.append([requests])
    labels.append(0)  # normal

# Attack traffic
for _ in range(200):
    requests = random.randint(500, 1500)
    data.append([requests])
    labels.append(1)  # attack

df = pd.DataFrame(data, columns=["requests"])

# Train model
model = RandomForestClassifier()
model.fit(df, labels)

# Save model
joblib.dump(model, "model.pkl")

print("New Model trained ✅")