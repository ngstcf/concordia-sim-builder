"""Decide which checkpoint artifacts a bulk sweep may delete.

Clearing checkpoints is mostly free disk space, but not entirely: a run that
never reached its final save has no other resume point than a checkpoint, so a
sweep that globs every ``*_checkpoint_step*`` and ``*_EMERGENCY_*`` file
destroys the recovery path for exactly the runs that need one. This module
sorts the artifacts into the ones a completed run has made redundant and the
ones that are still somebody's only copy.

Redundancy can only be judged per run. Runs of one scenario share a filename
slug and no artifact carries a run id, so the artifacts of a slug are sorted by
timestamp and cut into runs at each final ``.metadata.json``, which is the last
file a run writes. Cutting there rather than at the final ``.state.json``
matters because states are the files a sweep removes, so a logs directory that
has already been swept has finals with no state beside them; and cutting per
run rather than pairing on a time window matters because the timestamp in a
filename is generated at write time, so a run's emergency copy and its final
copy are seconds apart under *different* stems -- matching on the stem finds
nothing, and matching on slug-plus-a-minute can straddle two runs started back
to back.

Given the runs, the rule is short:

* A run that wrote a final ``.metadata.json`` finished. Every checkpoint of it
  is redundant, including the emergency copy, whose state is a byte-for-byte
  duplicate of the final one.
* A run that did not finish keeps its single most advanced recovery point --
  its emergency or watchdog copy if it has one, else its highest-numbered step
  checkpoint -- and everything earlier is redundant.

Final artifacts are never classified as redundant.

One case stays genuinely ambiguous, and the sweep resolves it against the older
run. A step checkpoint written before a *later* successful run of the same
scenario is indistinguishable, from the filenames alone, from a checkpoint that
successful run wrote on its way through: both are a `_checkpoint_stepN` of that
slug sitting shortly before a final save. So a crashed run whose scenario was
subsequently re-run to completion loses its checkpoints, while a crashed run
that was never re-run keeps them. Distinguishing the two needs a run id in the
filename, which the current naming scheme does not carry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

# Extensions an artifact can carry. Order matters only for reporting.
_EXTS = (".state.json", ".metadata.json", ".html")

_STAMP = re.compile(r"^(\d{8}_\d{6})_(.+)$")
_CHECKPOINT = re.compile(r"^(?P<slug>.+)_checkpoint_step(?P<step>\d+)$")
_WATCHDOG = re.compile(r"^(?P<slug>.+)_WATCHDOG_EMERGENCY_step(?P<step>\d+)$")
_EMERGENCY = re.compile(r"^(?P<slug>.+)_EMERGENCY_CHECKPOINT$")

# A recovery copy is written at most this long before the final save that
# supersedes it: the gap covers HTML conversion and metadata extraction only.
CLOSE_GAP = 120.0

# Within one timestamp, recovery copies sort before finals. Without this a
# stable sort by name strands a run's own emergency copies in the next run,
# because "." sorts before "_" and so `<slug>.html` precedes
# `<slug>_EMERGENCY_CHECKPOINT.html`.
_RANK = {
    ("emergency", "state"): 0, ("emergency", "html"): 1, ("emergency", "meta"): 2,
    ("watchdog", "state"): 0, ("watchdog", "html"): 1, ("watchdog", "meta"): 2,
    ("final", "state"): 4, ("final", "html"): 5, ("final", "meta"): 6,
}


@dataclass(frozen=True)
class Artifact:
    """One log file, parsed into the fields redundancy depends on."""

    name: str
    seconds: float
    slug: str
    kind: str   # "final" | "emergency" | "watchdog" | "checkpoint"
    ext: str    # "state" | "meta" | "html"
    step: int   # -1 when the name carries no step number
    stem: str   # name without its extension

    @property
    def is_recovery(self) -> bool:
        return self.kind in ("emergency", "watchdog")


@dataclass
class Sweep:
    """The verdict on a set of names."""

    redundant: list[str] = field(default_factory=list)
    spared: list[str] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)
    unfinished_runs: int = 0


def parse(name: str) -> Artifact | None:
    """Parse a log filename, or return None if it is not a log artifact."""
    stem, ext = name, None
    for suffix, tag in ((".state.json", "state"),
                        (".metadata.json", "meta"),
                        (".html", "html")):
        if stem.endswith(suffix):
            stem, ext = stem[: -len(suffix)], tag
            break
    if ext is None:
        return None

    stamped = _STAMP.match(stem)
    if not stamped:
        return None
    stamp, rest = stamped.groups()
    try:
        seconds = datetime.strptime(stamp, "%Y%m%d_%H%M%S").timestamp()
    except ValueError:
        return None

    step = -1
    if match := _CHECKPOINT.match(rest):
        kind, slug, step = "checkpoint", match["slug"], int(match["step"])
    elif match := _WATCHDOG.match(rest):
        kind, slug, step = "watchdog", match["slug"], int(match["step"])
    elif match := _EMERGENCY.match(rest):
        kind, slug = "emergency", match["slug"]
    else:
        kind, slug = "final", rest

    return Artifact(name=name, seconds=seconds, slug=slug, kind=kind,
                    ext=ext, step=step, stem=stem)


def group_runs(artifacts: Iterable[Artifact]) -> list[list[Artifact]]:
    """Cut one slug's artifacts into runs at each final ``.metadata.json``."""
    ordered = sorted(artifacts,
                     key=lambda a: (a.seconds, _RANK.get((a.kind, a.ext), 3)))
    runs: list[list[Artifact]] = []
    current: list[Artifact] = []
    for index, artifact in enumerate(ordered):
        current.append(artifact)
        closes = artifact.kind == "final" and artifact.ext == "meta"
        if artifact.is_recovery and artifact.ext == "meta":
            # A recovery copy ends the run unless the final save follows it,
            # which it does within seconds when the run did finish.
            closes = not any(
                later.kind == "final"
                and later.seconds - artifact.seconds <= CLOSE_GAP
                for later in ordered[index + 1:index + 6]
            )
        if closes:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def partition(names: Iterable[str]) -> Sweep:
    """Split checkpoint artifacts into the redundant and the still-needed."""
    by_slug: dict[str, list[Artifact]] = {}
    sweep = Sweep()
    for name in names:
        artifact = parse(name)
        if artifact is None:
            sweep.spared.append(name)
            sweep.reasons[name] = "not a recognised log artifact"
            continue
        by_slug.setdefault(artifact.slug, []).append(artifact)

    for artifacts in by_slug.values():
        for run in group_runs(artifacts):
            finished = any(a.kind == "final" and a.ext == "meta" for a in run)
            keep_stem = None
            if not finished:
                sweep.unfinished_runs += 1
                recovery = [a for a in run if a.is_recovery]
                if recovery:
                    keep_stem = max(recovery, key=lambda a: a.seconds).stem
                else:
                    checkpoints = [a for a in run if a.kind == "checkpoint"]
                    if checkpoints:
                        keep_stem = max(
                            checkpoints, key=lambda a: (a.step, a.seconds)
                        ).stem

            for artifact in run:
                if artifact.kind == "final":
                    sweep.spared.append(artifact.name)
                    sweep.reasons[artifact.name] = "final artifact"
                elif finished:
                    sweep.redundant.append(artifact.name)
                    sweep.reasons[artifact.name] = "the run finished"
                elif artifact.stem == keep_stem:
                    sweep.spared.append(artifact.name)
                    sweep.reasons[artifact.name] = (
                        "only resume point of a run that never finished"
                    )
                else:
                    sweep.redundant.append(artifact.name)
                    sweep.reasons[artifact.name] = (
                        "superseded by a later checkpoint of the same"
                        " unfinished run"
                    )

    return sweep
