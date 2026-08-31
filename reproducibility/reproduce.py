"""Run the focused paper checks and verify the exact q=3 certificate."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from expected_certificate import EXPECTED_Q3_CERTIFICATE


ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
TESTS = ROOT / "tests"
def main() -> int:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join((str(CODE), str(ROOT)))
    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(TESTS),
        "-v",
    ]
    completed = subprocess.run(command, env=environment, check=False)
    if completed.returncode:
        return completed.returncode

    sys.path.insert(0, str(CODE))
    from run_mixed_abelian_uds_audit import audit

    observed = audit((2, 2, 3), 5)
    if observed != EXPECTED_Q3_CERTIFICATE:
        print("Exact certificate differs from the source expectations.", file=sys.stderr)
        for key in sorted(set(observed) | set(EXPECTED_Q3_CERTIFICATE)):
            expected_value = EXPECTED_Q3_CERTIFICATE.get(key)
            observed_value = observed.get(key)
            if observed_value != expected_value:
                print(
                    f"  {key}: expected {expected_value!r}, observed {observed_value!r}",
                    file=sys.stderr,
                )
        return 1

    print(
        "Verified exact certificate: "
        f"{observed['positive_vectors_checked']} vectors, "
        f"{observed['unit_count']} units, "
        f"digest {observed['enumeration_residue_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
