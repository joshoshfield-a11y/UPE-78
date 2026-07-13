"""
UPE-78 Stochastic Engine
Probabilistic process modeling and Monte Carlo simulation
"""

import numpy as np
from typing import List, Tuple, Callable, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class ProcessParams:
    """Parameters for stochastic process"""
    drift: float = 0.0
    volatility: float = 0.1
    mean_reversion: float = 0.0
    long_term_mean: float = 0.0
    jump_intensity: float = 0.0
    jump_mean: float = 0.0
    jump_std: float = 0.1


class StochasticEngine:
    """
    General-purpose stochastic process engine.

    Supports: Brownian motion, Geometric Brownian motion,
    Ornstein-Uhlenbeck, Jump-diffusion, and custom processes.
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.RandomState(seed)
        self._history = deque(maxlen=10000)

    def brownian_motion(self, n_steps: int, dt: float = 0.01) -> np.ndarray:
        """
        Standard Brownian motion W(t).

        dW ~ N(0, dt)
        """
        dW = self.rng.normal(0, np.sqrt(dt), n_steps)
        W = np.cumsum(dW)
        self._history.extend(W)
        return W

    def geometric_brownian(self, S0: float, params: ProcessParams, 
                            n_steps: int, dt: float = 0.01) -> np.ndarray:
        """
        Geometric Brownian motion for modeling.

        dS = μS dt + σS dW
        """
        S = np.zeros(n_steps)
        S[0] = S0

        for t in range(1, n_steps):
            dW = self.rng.normal(0, np.sqrt(dt))
            dS = params.drift * S[t-1] * dt + params.volatility * S[t-1] * dW
            S[t] = S[t-1] + dS

        self._history.extend(S)
        return S

    def ornstein_uhlenbeck(self, x0: float, params: ProcessParams,
                           n_steps: int, dt: float = 0.01) -> np.ndarray:
        """
        Ornstein-Uhlenbeck process (mean-reverting).

        dx = θ(μ - x)dt + σ dW
        """
        x = np.zeros(n_steps)
        x[0] = x0

        for t in range(1, n_steps):
            dW = self.rng.normal(0, np.sqrt(dt))
            dx = params.mean_reversion * (params.long_term_mean - x[t-1]) * dt +                  params.volatility * dW
            x[t] = x[t-1] + dx

        self._history.extend(x)
        return x

    def jump_diffusion(self, S0: float, params: ProcessParams,
                       n_steps: int, dt: float = 0.01) -> np.ndarray:
        """
        Merton jump-diffusion process.

        dS = μS dt + σS dW + S dJ
        where dJ is compound Poisson process.
        """
        S = np.zeros(n_steps)
        S[0] = S0

        for t in range(1, n_steps):
            dW = self.rng.normal(0, np.sqrt(dt))

            # Diffusion part
            dS_diff = params.drift * S[t-1] * dt + params.volatility * S[t-1] * dW

            # Jump part
            n_jumps = self.rng.poisson(params.jump_intensity * dt)
            if n_jumps > 0:
                jump_sizes = self.rng.normal(params.jump_mean, params.jump_std, n_jumps)
                dS_jump = S[t-1] * (np.prod(1 + jump_sizes) - 1)
            else:
                dS_jump = 0

            S[t] = S[t-1] + dS_diff + dS_jump

        self._history.extend(S)
        return S

    def fractional_brownian(self, n_steps: int, hurst: float = 0.75, 
                           dt: float = 0.01) -> np.ndarray:
        """
        Fractional Brownian motion with Hurst exponent H.

        H = 0.5: standard Brownian
        H > 0.5: persistent (long memory)
        H < 0.5: anti-persistent
        """
        # Davies-Harte method approximation
        n = n_steps
        r = np.zeros(n)
        r[0] = 1
        for k in range(1, n):
            r[k] = 0.5 * (abs(k+1)**(2*hurst) - 2*abs(k)**(2*hurst) + abs(k-1)**(2*hurst))

        # Circulant embedding
        m = 2 * n
        c = np.zeros(m)
        c[:n] = r
        c[n+1:] = r[1:n][::-1]

        # Eigenvalues
        eigvals = np.fft.fft(c).real
        eigvals = np.maximum(eigvals, 0)  # Ensure non-negative

        # Generate complex Gaussian
        z = self.rng.normal(0, 1, m) + 1j * self.rng.normal(0, 1, m)
        z[0] = z[0].real * np.sqrt(2)
        if m % 2 == 0:
            z[m//2] = z[m//2].real * np.sqrt(2)

        # Construct fBM
        w = np.fft.ifft(np.sqrt(eigvals) * z).real[:n]
        fbm = np.cumsum(w) * (dt ** hurst)

        self._history.extend(fbm)
        return fbm

    def get_autocorrelation(self, lag: int = 1) -> float:
        """Compute autocorrelation of history"""
        if len(self._history) < lag + 1:
            return 0.0

        data = np.array(list(self._history))
        mean = np.mean(data)
        c0 = np.mean((data - mean) ** 2)
        c_lag = np.mean((data[:-lag] - mean) * (data[lag:] - mean))

        return c_lag / c0 if c0 > 0 else 0.0


class MonteCarlo:
    """Monte Carlo simulation engine"""

    def __init__(self, n_paths: int = 10000, seed: Optional[int] = None):
        self.n_paths = n_paths
        self.rng = np.random.RandomState(seed)

    def simulate(self, process_fn: Callable, n_steps: int, 
                 **kwargs) -> np.ndarray:
        """
        Run Monte Carlo simulation.

        Args:
            process_fn: Function that returns a path given rng and steps
            n_steps: Number of time steps
            **kwargs: Additional arguments for process_fn

        Returns:
            Array of shape (n_paths, n_steps)
        """
        paths = np.zeros((self.n_paths, n_steps))

        for i in range(self.n_paths):
            paths[i] = process_fn(self.rng, n_steps, **kwargs)

        return paths

    def estimate_expectation(self, paths: np.ndarray, 
                             payoff_fn: Callable) -> Tuple[float, float]:
        """
        Estimate expectation and standard error.

        Returns:
            (mean, standard_error)
        """
        payoffs = np.array([payoff_fn(path) for path in paths])
        mean = np.mean(payoffs)
        std_err = np.std(payoffs) / np.sqrt(len(payoffs))

        return mean, std_err

    def estimate_quantile(self, paths: np.ndarray, 
                          payoff_fn: Callable, q: float = 0.95) -> float:
        """Estimate quantile of payoff distribution"""
        payoffs = np.array([payoff_fn(path) for path in paths])
        return np.quantile(payoffs, q)

    def convergence_analysis(self, process_fn: Callable, n_steps: int,
                             payoff_fn: Callable, max_paths: int = 100000) -> dict:
        """Analyze convergence as function of path count"""
        path_counts = [100, 500, 1000, 5000, 10000, 50000, 100000]
        path_counts = [p for p in path_counts if p <= max_paths]

        results = {"paths": [], "means": [], "std_errs": []}

        for n in path_counts:
            self.n_paths = n
            paths = self.simulate(process_fn, n_steps)
            mean, std_err = self.estimate_expectation(paths, payoff_fn)

            results["paths"].append(n)
            results["means"].append(mean)
            results["std_errs"].append(std_err)

        return results


class ProcessModel:
    """High-level process model for system dynamics"""

    def __init__(self, n_dimensions: int = 936):
        self.n_dimensions = n_dimensions
        self.engine = StochasticEngine()
        self._models = {}

    def add_model(self, name: str, process_type: str, params: ProcessParams):
        """Add a stochastic process model"""
        self._models[name] = {
            "type": process_type,
            "params": params,
            "history": []
        }

    def simulate(self, name: str, n_steps: int, dt: float = 0.01) -> np.ndarray:
        """Simulate named process"""
        if name not in self._models:
            raise ValueError(f"Unknown model: {name}")

        model = self._models[name]
        params = model["params"]

        if model["type"] == "brownian":
            result = self.engine.brownian_motion(n_steps, dt)
        elif model["type"] == "geometric":
            result = self.engine.geometric_brownian(1.0, params, n_steps, dt)
        elif model["type"] == "ornstein_uhlenbeck":
            result = self.engine.ornstein_uhlenbeck(0.0, params, n_steps, dt)
        elif model["type"] == "jump_diffusion":
            result = self.engine.jump_diffusion(1.0, params, n_steps, dt)
        elif model["type"] == "fractional":
            result = self.engine.fractional_brownian(n_steps, params.drift, dt)
        else:
            raise ValueError(f"Unknown process type: {model['type']}")

        model["history"].append(result)
        return result

    def cross_correlation(self, name1: str, name2: str) -> float:
        """Compute cross-correlation between two processes"""
        if name1 not in self._models or name2 not in self._models:
            return 0.0

        h1 = self._models[name1]["history"]
        h2 = self._models[name2]["history"]

        if not h1 or not h2:
            return 0.0

        # Use last simulation
        a, b = h1[-1], h2[-1]
        min_len = min(len(a), len(b))
        a, b = a[:min_len], b[:min_len]

        a_norm = a - np.mean(a)
        b_norm = b - np.mean(b)

        return np.sum(a_norm * b_norm) / (np.sqrt(np.sum(a_norm**2)) * np.sqrt(np.sum(b_norm**2)))
