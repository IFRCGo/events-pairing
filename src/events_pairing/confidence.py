"""Per-cluster confidence scores for the events pairing output."""

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import silhouette_samples

NOISE_LABEL = -1

# Weights of the confidence components (sum to 1)
COHESION_WEIGHT = 0.5
SEPARATION_WEIGHT = 0.25
CORROBORATION_WEIGHT = 0.25


@dataclass
class ClusterConfidence:
    """Confidence of a cluster and the components it is built from (all in [0, 1])."""

    confidence: float
    # Mean pairwise similarity (1 - distance) of cross-source pairs in the cluster
    # (all pairs if the cluster has a single source)
    cohesion: float
    # Mean silhouette of the members rescaled from [-1, 1] to [0, 1]: how much closer members are
    # to their own cluster than to the nearest other cluster / noise event
    separation: float
    # 1 - 0.5^n_sources: more independent sources reporting the event -> more confidence
    corroboration: float
    n_sources: int


def _separation_per_event(D: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Silhouette per event; noise events are treated as singleton clusters."""
    relabelled = labels.copy()
    noise = np.where(labels == NOISE_LABEL)[0]
    relabelled[noise] = labels.max() + 1 + np.arange(len(noise))
    n_labels = len(np.unique(relabelled))
    if n_labels < 2 or n_labels >= len(labels):
        # silhouette is undefined for a single cluster or when every point is its own cluster
        return np.zeros(len(labels))
    return silhouette_samples(D, relabelled, metric="precomputed")


def compute_cluster_confidence(D: np.ndarray, labels: list | np.ndarray, sources: list[str]) -> dict:
    """
    Compute the confidence of every cluster.

    D: precomputed distance matrix (0 = identical, 1 = unrelated) used for the clustering
    labels: cluster label per event (-1 = noise)
    sources: source name per event

    Returns {label: ClusterConfidence}; noise is not included.
    """
    labels = np.asarray(labels)
    sources = np.asarray(sources)
    silhouette = _separation_per_event(D, labels)

    result = {}
    for label in np.unique(labels):
        if label == NOISE_LABEL:
            continue
        idx = np.where(labels == label)[0]
        sub_d = D[np.ix_(idx, idx)]
        sub_src = sources[idx]

        iu = np.triu_indices(len(idx), k=1)
        pair_sim = 1.0 - sub_d[iu]
        cross = sub_src[iu[0]] != sub_src[iu[1]]
        cohesion = float(pair_sim[cross].mean() if cross.any() else pair_sim.mean()) if len(pair_sim) else 0.0

        separation = float((silhouette[idx].mean() + 1.0) / 2.0)
        n_sources = len(set(sub_src))
        corroboration = 1.0 - 0.5**n_sources

        confidence = COHESION_WEIGHT * cohesion + SEPARATION_WEIGHT * separation + CORROBORATION_WEIGHT * corroboration
        result[int(label)] = ClusterConfidence(
            confidence=round(float(np.clip(confidence, 0.0, 1.0)), 3),
            cohesion=round(cohesion, 3),
            separation=round(separation, 3),
            corroboration=round(corroboration, 3),
            n_sources=n_sources,
        )
    return result
