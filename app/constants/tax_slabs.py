"""Validated income tax slab thresholds and rates for supported regimes."""

from pydantic import BaseModel, ConfigDict

TaxSlab = tuple[float, float]


class TaxSlabConstants(BaseModel):
    """Progressive tax slabs for the old and new tax regimes."""

    model_config = ConfigDict(frozen=True)

    old: tuple[TaxSlab, ...] = (
        (250000, 0.00),
        (500000, 0.05),
        (1000000, 0.20),
        (float("inf"), 0.30),
    )
    new: tuple[TaxSlab, ...] = (
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float("inf"), 0.30),
    )


TAX_SLABS = TaxSlabConstants()
