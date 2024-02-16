"""Utils functions."""

from copy import deepcopy

import numpy as np

from ._logs import logger


def _cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2) / (
        np.linalg.norm(vector1) * np.linalg.norm(vector2)
    )
    return dot_product


# TODO: Add test for this. Also compare speed with latest version of numpy.
# Also compared speed with a numba implementation.
def _corr_vectors(A, B, axis=0):
    """Compute correlation of multiple pairs of vectors.

    Parameters
    ----------
    A : ndarray, shape (n, m)
        The first collection of vectors
    B : ndarray, shape (n, m)
        The second collection of vectors
    axis : int
        The axis that contains the elements of each vector. Defaults to 0.

    Returns
    -------
    corr : ndarray, shape (m, )
        For each pair of vectors, the correlation between them.
    """
    if A.shape != B.shape:
        raise ValueError("All input arrays must have the same shape")

    corr = []
    for a, b in zip(A, B):
        # If maps is null, divide will not throw an error.
        if np.all(a == 0) or np.all(b == 0):
            cos = 0
        else:
            cos = _cosine_similarity(a, b)
        corr.append(cos)
    corr = np.array(corr)
    return corr


def _distance_matrix(X, Y=None):
    """Distance matrix used in metrics."""
    distances = np.abs(1 / np.corrcoef(X, Y)) - 1
    distances = np.nan_to_num(
        distances, copy=False, nan=10e300, posinf=1e300, neginf=-1e300
    )
    return distances


def _compare_infos(cluster_info, inst_info):
    """Check that channels in cluster_info are all present in inst_info."""
    for ch in cluster_info["ch_names"]:
        if ch not in inst_info["ch_names"]:
            raise ValueError(
                "Instance to segment into microstates sequence does not have "
                "the same channels as the instance used for fitting."
            )

    # Extract loc arrays
    cluster_loc = list()
    for ch in cluster_info["chs"]:
        cluster_loc.append((ch["ch_name"], deepcopy(ch["loc"])))
    inst_loc = list()
    for ch in inst_info["chs"]:
        if ch["ch_name"] in cluster_info["ch_names"]:
            inst_loc.append((ch["ch_name"], deepcopy(ch["loc"])))
    cluster_loc = [loc[1] for loc in sorted(cluster_loc, key=lambda x: x[0])]
    inst_loc = [loc[1] for loc in sorted(inst_loc, key=lambda x: x[0])]

    # Compare loc
    assert len(cluster_loc) == len(inst_loc)  # sanity-check
    for l1, l2 in zip(cluster_loc, inst_loc):
        if not np.allclose(l1, l2, equal_nan=True):
            logger.warning(
                "Instance to segment into microstates sequence does not have "
                "the same channels montage as the instance used for fitting. "
            )
            break

    # Compare attributes in chs
    cluster_kinds = []
    cluster_units = []
    cluster_coord_frame = []
    for ch in cluster_info["chs"]:
        cluster_kinds.append((ch["ch_name"], ch["kind"]))
        cluster_units.append((ch["ch_name"], ch["unit"]))
        cluster_coord_frame.append((ch["ch_name"], ch["coord_frame"]))

    inst_kinds = []
    inst_units = []
    inst_coord_frames = []
    for ch in inst_info["chs"]:
        if ch["ch_name"] in cluster_info["ch_names"]:
            inst_kinds.append((ch["ch_name"], ch["kind"]))
            inst_units.append((ch["ch_name"], ch["unit"]))
            inst_coord_frames.append((ch["ch_name"], ch["coord_frame"]))

    cluster_kinds = [elt[1] for elt in sorted(cluster_kinds, key=lambda x: x[0])]
    cluster_units = [elt[1] for elt in sorted(cluster_units, key=lambda x: x[0])]
    cluster_coord_frame = [
        elt[1] for elt in sorted(cluster_coord_frame, key=lambda x: x[0])
    ]
    inst_kinds = [elt[1] for elt in sorted(inst_kinds, key=lambda x: x[0])]
    inst_units = [elt[1] for elt in sorted(inst_units, key=lambda x: x[0])]
    inst_coord_frames = [
        elt[1] for elt in sorted(inst_coord_frames, key=lambda x: x[0])
    ]

    if not all(kind1 == kind2 for kind1, kind2 in zip(cluster_kinds, inst_kinds)):
        logger.warning(
            "Instance to segment into microstates sequence does not have "
            "the same channels kinds as the instance used for fitting. "
        )
    if not all(unit1 == unit2 for unit1, unit2 in zip(cluster_units, inst_units)):
        logger.warning(
            "Instance to segment into microstates sequence does not have "
            "the same channels units as the instance used for fitting. "
        )
    if not all(f1 == f2 for f1, f2 in zip(cluster_coord_frame, inst_coord_frames)):
        logger.warning(
            "Instance to segment into microstates sequence does not have "
            "the same coordinate frames as the instance used for fitting. "
        )
