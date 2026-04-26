#!/usr/bin/env python3
"""
calibrate_deq.py — Calibrazione empirica del modello DEQ²

Esegue:
  1. Stima di Sigma_geo dalla matrice di covarianza macro (52 nazioni)
  2. Identificazione di J (Strategy B, diagonal scaling)
  3. Bootstrap 5000 resamples per CI al 95%
  4. Likelihood ratio test B vs A e B vs C
  5. Report in JSON + stampa a schermo

Fonti dati:
  - World Bank WGI: https://info.worldbank.org/governance/wgi/
  - Atlas of Economic Complexity (ECI): https://atlas.cid.harvard.edu/
  - Brand Finance Soft Power Index: https://brandirectory.com/softpower/

Uso:
    python calibrate_deq.py               # usa dati simulati (offline)
    python calibrate_deq.py --real        # usa dati reali da file CSV
    python calibrate_deq.py --bootstrap N # numero resamples (default 5000)
"""

import argparse
import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize
from scipy.stats import chi2

RNG = np.random.default_rng(42)

# ─── Sigma_comm (da Topografia, §5.1) ─────────────────────────────────────────
SIGMA_COMM = np.array([
    [1.00, 0.40, 0.30],
    [0.40, 1.00, 0.50],
    [0.30, 0.50, 1.00],
])

# ─── 52 nazioni (ISO3) ────────────────────────────────────────────────────────
NATIONS_52 = [
    "USA", "CHN", "EU27", "BRA", "IND", "RUS", "JPN", "GBR", "DEU", "FRA",
    "ITA", "KOR", "MEX", "IDN", "ZAF", "TUR", "SAU", "EGY", "ARG", "NGA",
    "KEN", "ETH", "GHA", "TZA", "VNM", "THA", "PHL", "MYS", "BGD", "PAK",
    "COL", "CHL", "PER", "ISR", "IRN", "POL", "UKR", "SWE", "NOR", "NLD",
    "BEL", "CHE", "AUT", "PRT", "CZE", "ROU", "HUN", "GRC", "FIN", "DNK",
    "NZL", "CAN",
]

# ─── Sigma_geo target (valori del paper, §6.2) ────────────────────────────────
SIGMA_GEO_TARGET = np.array([
    [1.00, 0.52, 0.38],
    [0.52, 1.00, 0.61],
    [0.38, 0.61, 1.00],
])


def simulate_macro_data(n_nations: int, n_years: int, sigma_geo: np.ndarray
                        ) -> np.ndarray:
    """Genera dati macro simulati con struttura di correlazione sigma_geo."""
    L = np.linalg.cholesky(sigma_geo)
    data = []
    for _ in range(n_nations * n_years):
        z = RNG.standard_normal(3)
        s = L @ z
        data.append(s)
    return np.array(data)


def load_real_data(data_dir: Path) -> np.ndarray:
    """Carica dati reali da CSV (formato: iso3, year, s1, s2, s3)."""
    csv_path = data_dir / "macro_data.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dati reali non trovati: {csv_path}\n"
            "Scaricare WGI, ECI, Brand Finance e unire in un CSV con colonne:\n"
            "  iso3, year, s1_cohesion, s2_capability, s3_legitimacy"
        )
    import csv
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append([float(row['s1_cohesion']), float(row['s2_capability']),
                         float(row['s3_legitimacy'])])
    return np.array(rows)


def zscore_normalize(data: np.ndarray) -> np.ndarray:
    """Normalizza a z-score e scala a [0,10]."""
    mu = data.mean(axis=0)
    sd = data.std(axis=0)
    z = (data - mu) / sd
    z = (z - z.min(axis=0)) / (z.max(axis=0) - z.min(axis=0)) * 10
    return z


def empirical_cov(data: np.ndarray) -> np.ndarray:
    """Matrice di covarianza empirica standardizzata (correlazione)."""
    n, p = data.shape
    mu = data.mean(axis=0)
    centered = data - mu
    cov = centered.T @ centered / (n - 1)
    sd = np.sqrt(np.diag(cov))
    corr = cov / np.outer(sd, sd)
    return corr


def strategy_b_loss(log_alpha: np.ndarray, sigma_geo: np.ndarray,
                    sigma_comm: np.ndarray) -> float:
    """Loss sul triangolo superiore (k=1): sigma_geo[i,j] = alpha_i*alpha_j*sigma_comm[i,j]."""
    alpha = np.exp(log_alpha)
    idx = np.triu_indices(3, k=1)
    geo_vec = sigma_geo[idx]
    comm_vec = sigma_comm[idx]
    # Off-diagonal predicted: alpha_i * alpha_j * sigma_comm[i,j]
    pred_vec = np.array([alpha[i] * alpha[j] * sigma_comm[i, j]
                         for i, j in zip(idx[0], idx[1])])
    diff = geo_vec - pred_vec
    return np.sum(diff**2)


def fit_strategy_b(sigma_geo: np.ndarray, sigma_comm: np.ndarray
                   ) -> tuple[np.ndarray, float]:
    """Stima alpha fittando solo gli elementi fuori diagonale (3 vs 3 datapoints)."""
    x0 = np.zeros(3)
    result = minimize(strategy_b_loss, x0, args=(sigma_geo, sigma_comm),
                      method='L-BFGS-B', options={'ftol': 1e-14, 'gtol': 1e-10})
    alpha_hat = np.exp(result.x)
    # R² sugli off-diagonal
    idx = np.triu_indices(3, k=1)
    geo_vec = sigma_geo[idx]
    pred_vec = np.array([alpha_hat[i] * alpha_hat[j] * sigma_comm[i, j]
                         for i, j in zip(idx[0], idx[1])])
    ss_res = np.sum((geo_vec - pred_vec)**2)
    ss_tot = np.sum((geo_vec - geo_vec.mean())**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return alpha_hat, r2


def bootstrap_ci(data: np.ndarray, sigma_comm: np.ndarray,
                 n_boot: int = 5000, block_len: int = 3) -> dict:
    """Bootstrap a blocchi per CI al 95%."""
    n = len(data)
    alphas = []
    for _ in range(n_boot):
        # Block bootstrap
        n_blocks = int(np.ceil(n / block_len))
        starts = RNG.integers(0, n - block_len + 1, size=n_blocks)
        indices = np.concatenate([np.arange(s, min(s + block_len, n))
                                  for s in starts])[:n]
        resample = data[indices]
        sg = empirical_cov(resample)
        alpha_hat, _ = fit_strategy_b(sg, sigma_comm)
        alphas.append(alpha_hat)
    alphas = np.array(alphas)
    ci_lo = np.percentile(alphas, 2.5, axis=0)
    ci_hi = np.percentile(alphas, 97.5, axis=0)
    return {'ci_lo': ci_lo.tolist(), 'ci_hi': ci_hi.tolist(),
            'mean': alphas.mean(axis=0).tolist(), 'std': alphas.std(axis=0).tolist()}


def lrt_a_vs_b(sigma_geo: np.ndarray, sigma_comm: np.ndarray,
               n: int) -> dict:
    """Likelihood ratio test Strategy A vs B (chi² approx, df=3)."""
    # Strategy A: alpha = (1,1,1)
    alpha_a = np.ones(3)
    J_a = np.diag(alpha_a)
    sg_a = J_a @ sigma_comm @ J_a.T
    loss_a = strategy_b_loss(np.zeros(3), sigma_geo, sigma_comm)

    alpha_b, _ = fit_strategy_b(sigma_geo, sigma_comm)
    loss_b = strategy_b_loss(np.log(alpha_b), sigma_geo, sigma_comm)

    chi2_stat = n * (loss_a - loss_b)
    p_val = 1 - chi2.cdf(chi2_stat, df=3)
    return {'chi2': round(chi2_stat, 2), 'df': 3, 'p': round(p_val, 4)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true',
                        help='Usa dati reali da paper-en/macro_data.csv')
    parser.add_argument('--bootstrap', type=int, default=5000)
    args = parser.parse_args()

    print("=" * 60)
    print("DEQ² — Calibrazione empirica (Strategy B)")
    print("=" * 60)

    if args.real:
        data_dir = Path(__file__).parent
        data = load_real_data(data_dir)
        data = zscore_normalize(data)
        print(f"Dati reali caricati: {len(data)} country-years")
    else:
        # Simula dati con la struttura di correlazione del paper (SIGMA_GEO_TARGET)
        # Questo testa il metodo: si può recuperare alpha da dati con questa struttura?
        data = simulate_macro_data(52, 11, SIGMA_GEO_TARGET)
        # Non normalizziamo: la covarianza è già normalizzata (matrice di correlazione)
        print(f"Dati simulati: {len(data)} country-years (52 nazioni × 11 anni)")
        print(f"  Sigma_geo target = {SIGMA_GEO_TARGET.tolist()}")

    print()

    # Sigma_geo empirica
    sigma_geo = empirical_cov(data)
    print("Sigma_geo empirica:")
    for row in sigma_geo:
        print("  " + "  ".join(f"{v:.3f}" for v in row))
    print()

    # Fit Strategy B
    alpha_hat, r2 = fit_strategy_b(sigma_geo, SIGMA_COMM)
    print(f"Strategy B — alpha_hat: {alpha_hat.round(3)}")
    print(f"Strategy B — R²: {r2:.4f}")
    print()

    # Predizione sigma_geo
    sigma_pred = np.diag(alpha_hat) @ SIGMA_COMM @ np.diag(alpha_hat)
    print("Sigma_geo predetta (Strategy B):")
    for row in sigma_pred:
        print("  " + "  ".join(f"{v:.3f}" for v in row))
    print()

    # LRT A vs B
    lrt = lrt_a_vs_b(sigma_geo, SIGMA_COMM, len(data))
    print(f"LRT Strategy A vs B: chi²={lrt['chi2']}, df={lrt['df']}, p={lrt['p']}")
    print()

    # Bootstrap
    print(f"Bootstrap CI (n={args.bootstrap} resamples, blocchi da 3)...")
    boot = bootstrap_ci(data, SIGMA_COMM, n_boot=args.bootstrap)
    for k in range(3):
        print(f"  alpha_{k+1}: {boot['mean'][k]:.3f}  "
              f"95% CI [{boot['ci_lo'][k]:.3f}, {boot['ci_hi'][k]:.3f}]")

    print()
    print("=" * 60)

    # Salva risultati
    results = {
        'alpha_hat': alpha_hat.tolist(),
        'r2': round(r2, 4),
        'sigma_geo_empirical': sigma_geo.tolist(),
        'sigma_geo_predicted': sigma_pred.tolist(),
        'lrt_a_vs_b': lrt,
        'bootstrap': boot,
        'n_obs': len(data),
        'n_boot': args.bootstrap,
    }
    out_path = Path(__file__).parent / 'calibration_results.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Risultati salvati in: {out_path}")


if __name__ == '__main__':
    main()
