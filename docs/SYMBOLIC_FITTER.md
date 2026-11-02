# Symbolic fitter (P2.1 / issue #19)

## Laws (DSL)

Declared in `services/api/hypatia/symbolic_fitter.py`:

- **Period law:** \(T = 2\pi\sqrt{L/g}\) → invert for `g` from estimated period
- **SHM law:** \(\theta(t) = A\cos(\omega t + \phi)\) → `g = \omega^2 L` via SciPy `curve_fit`

`fit_pendulum_g()` blends SHM + period estimates for the pendulum winner in `science.fit_rival_hypotheses`.

## PySR

Optional: install `pysr` locally for exploratory regression (`optional_pysr_g`). **CI does not require PySR** — SciPy only.

## Tests

```bash
export PYTHONPATH=services/api
pytest services/api/tests/test_symbolic_fitter.py -q
```

DoD: recover **g ≈ 9.8 m/s²** within **0.75 m/s²** on synthetic noise; fixture track in `[8, 12]`.
