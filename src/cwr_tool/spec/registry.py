from __future__ import annotations

from dataclasses import dataclass

from cwr_tool.models.input import CWRVersion


@dataclass(frozen=True, slots=True)
class VersionSpec:
    """
    Version overlay for requirements and behavior.

    We’ll fill this out with:
    - required groups/records
    - allowed record types per group
    - field lengths / layouts (fixed-width)
    - code sets and charsets per version
    """

    version: CWRVersion
    supports_spu_group: bool = True

    # For now, WRK minimal writer always exists in our pipeline.
    # Later: declare required control records etc.


class SpecRegistry:
    """
    Central place to fetch per-version rules and generation config.
    """

    _SPECS: dict[CWRVersion, VersionSpec] = {
        CWRVersion.V21: VersionSpec(version=CWRVersion.V21, supports_spu_group=True),
        CWRVersion.V22: VersionSpec(version=CWRVersion.V22, supports_spu_group=True),
        CWRVersion.V30: VersionSpec(version=CWRVersion.V30, supports_spu_group=True),
        CWRVersion.V31: VersionSpec(version=CWRVersion.V31, supports_spu_group=True),
    }

    @classmethod
    def get(cls, version: str) -> VersionSpec:
        try:
            v = CWRVersion(version)
        except ValueError:
            # Keep strict: caller can surface a clean validation error
            raise ValueError(f"Unsupported CWR version: {version}") from None
        return cls._SPECS[v]
