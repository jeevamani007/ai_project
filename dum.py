# 1️⃣ Import libraries
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
import pandas as pd

# 2️⃣ Load data (CSV / Excel)
df = pd.read_csv("dumy.csv")  # 100 rows data irukku

# 3️⃣ Separate input(X) and output(y)
X = df[["salary", "age"]]  # Input features
y = df["result"]                       # Output (PASS / FAIL)

# 4️⃣ Split train & test (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5️⃣ Create Decision Tree model
model = DecisionTreeClassifier(criterion="gini", max_depth=3)

# 6️⃣ Train the model
model.fit(X_train, y_train)

# 7️⃣ Make a prediction
sample = [[88, 2]]  # attendance = 88, late_count = 2
prediction = model.predict(sample)
print("Prediction:", prediction)

# 8️⃣ Extract tree rules
rules = export_text(model, feature_names=list(X.columns))
print("Decision Rules:\n", rules)
