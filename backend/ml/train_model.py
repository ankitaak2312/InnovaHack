
import os

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from ml.features import FEATURE_NAMES, extract_features
from ml.generate_dataset import build_dataset

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pkl")


def main():
    urls, labels = build_dataset(n_per_class=600)
    X = [extract_features(u) for u in urls]
    y = labels

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.4f}\n")
    print(classification_report(y_test, preds, target_names=["safe", "phishing"]))

    bundle = {
        "model": clf,
        "feature_names": FEATURE_NAMES,
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"\nSaved model bundle to {os.path.abspath(MODEL_PATH)}")


if __name__ == "__main__":
    main()
