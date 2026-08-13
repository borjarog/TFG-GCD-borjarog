"""Métricas y umbral F1."""

import numpy as np

from src.modeling.evaluate import metricas_baseline_prevalencia, metricas_binarias, umbral_optimo_f1


def test_umbral_optimo_f1_maximiza_f1():
    y_true = np.array([0, 0, 0, 1, 1, 1])
    y_proba = np.array([0.05, 0.15, 0.25, 0.75, 0.85, 0.95])
    umbral = umbral_optimo_f1(y_true, y_proba)

    pred = (y_proba >= umbral).astype(int)
    from sklearn.metrics import f1_score

    f1_optimo = f1_score(y_true, pred, zero_division=0)

    for u in np.linspace(0.05, 0.95, 37):
        pred_u = (y_proba >= u).astype(int)
        if pred_u.sum() == 0:
            continue
        assert f1_score(y_true, pred_u, zero_division=0) <= f1_optimo + 1e-9


def test_metricas_binarias_clasificador_perfecto():
    y = np.array([0, 0, 1, 1])
    proba = np.array([0.0, 0.1, 0.9, 1.0])
    m = metricas_binarias(y, y, proba)

    assert m["roc_auc"] == 1.0
    assert m["pr_auc"] == 1.0
    assert m["f1"] == 1.0
    assert m["balanced_accuracy"] == 1.0


def test_metricas_baseline_prevalencia_estructura():
    y_train = np.array([0, 0, 0, 1])
    y_test = np.array([0, 1, 0, 1])
    m = metricas_baseline_prevalencia(y_train, y_test)

    assert m["prevalencia_train"] == 0.25
    assert m["filas_entreno"] == 4
    assert m["mejores_hiperparametros"]["strategy"] == "score_constante_prevalencia"
    assert 0.0 <= m["pr_auc"] <= 1.0
    assert m["roc_auc"] == 0.5
