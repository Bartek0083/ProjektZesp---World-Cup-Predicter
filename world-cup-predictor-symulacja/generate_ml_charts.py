from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix

def _to_label(name: str) -> str:
    mapping = {
        "home_win": "1 (gospodarz)",
        "draw": "X (remis)",
        "away_win": "2 (gość)",
    }
    return mapping.get(name, name)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent / "ProjektZesp---World-Cup-Predicter"
    sys.path.insert(0, str(repo_root))

    from data import load_matches, prepare_xy
    from model import evaluate_model, train_model

    output_dir = Path(__file__).resolve().parent / "docs" / "wykresy"
    output_dir.mkdir(parents=True, exist_ok=True)

    matches = load_matches(data_dir=repo_root)
    trained = train_model(matches=matches, cutoff_date="2024-01-01", random_state=0)
    evaluation = evaluate_model(trained, matches=matches)

    _, _, x_test, y_test, _, _ = prepare_xy(matches, cutoff_date=trained.cutoff_date)
    pred = trained.pipeline.predict(x_test)
    proba = trained.pipeline.predict_proba(x_test)
    classes = trained.classes_

    labels_pl = [_to_label(c) for c in classes]

    cm = confusion_matrix(y_test, pred, labels=classes)
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title("Macierz pomylek modelu ML")
    ax.set_xlabel("Predykcja")
    ax.set_ylabel("Rzeczywista klasa")
    ax.set_xticks(np.arange(len(labels_pl)))
    ax.set_yticks(np.arange(len(labels_pl)))
    ax.set_xticklabels(labels_pl, rotation=20, ha="right")
    ax.set_yticklabels(labels_pl)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                color="white" if cm[i, j] > cm.max() * 0.45 else "black",
            )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output_dir / "wykres_ml_macierz_pomylek.png", dpi=150)
    plt.close(fig)

    report = evaluation["classification_report"]
    precision = [report[c]["precision"] for c in classes]
    recall = [report[c]["recall"] for c in classes]
    f1 = [report[c]["f1-score"] for c in classes]

    x = np.arange(len(classes))
    w = 0.25
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.bar(x - w, precision, w, label="Precision")
    ax.bar(x, recall, w, label="Recall")
    ax.bar(x + w, f1, w, label="F1-score")
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels_pl)
    ax.set_ylabel("Wartosc")
    ax.set_title("Jakosc klasyfikacji modelu ML")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "wykres_ml_precision_recall_f1.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for idx, cls in enumerate(classes):
        ax.hist(
            proba[:, idx],
            bins=20,
            alpha=0.45,
            label=_to_label(cls),
        )
    ax.set_title("Rozklad prawdopodobienstw klas (test)")
    ax.set_xlabel("Prawdopodobienstwo")
    ax.set_ylabel("Liczba probek")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "wykres_ml_rozklad_prawdopodobienstw.png", dpi=150)
    plt.close(fig)

    print("ML charts generated in:", output_dir)
    print("accuracy:", round(float(evaluation["accuracy"]), 4))
    print("log_loss:", round(float(evaluation["log_loss"]), 4))
    print("train_size:", evaluation["train_size"], "test_size:", evaluation["test_size"])


if __name__ == "__main__":
    main()
