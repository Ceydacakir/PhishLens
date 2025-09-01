
import csv, os, joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from .features import extract_features, FEAT_ORDER

def _to_matrix(feat_list):
    return np.array([[f[k] for k in FEAT_ORDER] for f in feat_list], dtype=float)

def load_csv(csv_path: str):
    urls, labels = [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            urls.append(r["url"].strip())
            labels.append(int(r["label"]))
    return urls, labels

def train(csv_path: str, model_out: str):
    urls, y = load_csv(csv_path)
    feats = [extract_features(u) for u in urls]
    X = _to_matrix(feats)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])
    pipe.fit(X, y)
    prob = pipe.predict_proba(X)[:,1]
    yhat = (prob>=0.5).astype(int)
    os.makedirs(os.path.dirname(model_out) or ".", exist_ok=True)
    joblib.dump({"model": pipe, "feat_order": FEAT_ORDER}, model_out)
    return {"n": len(y), "acc": float((yhat==y).mean()), "auc": float(roc_auc_score(y, prob)), "f1": float(f1_score(y, yhat))}

def predict(model_path: str, urls):
    obj = joblib.load(model_path)
    pipe = obj["model"]
    feats = [extract_features(u) for u in urls]
    X = _to_matrix(feats)
    prob = pipe.predict_proba(X)[:,1]
    preds = (prob>=0.5).astype(int).tolist()
    out = []
    for u, p, pr, f in zip(urls, preds, prob.tolist(), feats):
        out.append({"url": u, "pred": int(p), "prob": float(pr), "features": f})
    return out
