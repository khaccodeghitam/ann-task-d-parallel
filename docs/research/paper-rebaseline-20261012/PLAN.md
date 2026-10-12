# Frozen blocked prospective design

Campaign `PAPER_REBASELINE_SIFT10M_20261012T144741235340Z`; PLAN SHA256 `c79e74cb5e40fe59065c8de147ba582804f7557698b90f093d912f8d85ccf205`.
**NOT EXECUTABLE.** No benchmark has started; paper binary/index identities are null.
Default OVERLAP_INIT rejects the specified mem_L0, independently of the GCC13 build failure.
This freezes intended order/statistics without claiming a complete execution protocol. Resource/observer
implementation and objective swap rule must be finalized in a **new plan** after blockers are resolved.

Primary order (36):
```
B01: PAPER_T1 → PAPER_T4 → PAPER_T8 → PAPER_T16 → MODERN_T8 → MODERN_T16
B02: PAPER_T4 → PAPER_T8 → PAPER_T16 → MODERN_T8 → MODERN_T16 → PAPER_T1
B03: PAPER_T8 → PAPER_T16 → MODERN_T8 → MODERN_T16 → PAPER_T1 → PAPER_T4
B04: PAPER_T16 → MODERN_T8 → MODERN_T16 → PAPER_T1 → PAPER_T4 → PAPER_T8
B05: MODERN_T8 → MODERN_T16 → PAPER_T1 → PAPER_T4 → PAPER_T8 → PAPER_T16
B06: MODERN_T16 → PAPER_T1 → PAPER_T4 → PAPER_T8 → PAPER_T16 → MODERN_T8
```
Recall sweep (24): L50/75/125/150 × PAPER/MODERN ×3, order exactly in JSON.
Width sweep (6): PAPER T8 L100 W16/W64 ×3, alternating order exactly in JSON.
Five seconds between cases;15 seconds between primary blocks. Native/unbound; no tuning, cache flush or exclusion.
All commands are unexecuted templates. Source/build/quality/integrity gates precede acceptance.
Block bootstrap20000/seed20261012/CI90; p*(n−1) interpolation, separate from stock tail order statistics.
This is a design record, not evidence of 66 measurements or permission to reinterpret a different build as stock.
