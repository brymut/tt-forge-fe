# SPDX-FileCopyrightText: © 2024 Tenstorrent AI ULC

# SPDX-License-Identifier: Apache-2.0
from ..tensor import Tensor
from .common import ForgeOp as op


def Constant(name: str, *, constant: float) -> Tensor:
    """
    Op representing user-defined constant

    Parameters
    ----------
    name: str
        Op name, unique to the module, or leave blank to autoset

    constant: float
        Constant value

    Returns
    -------
    Tensor
        Forge tensor
    """
    return op("constant", name, **{"c": constant}).get_tensor()
