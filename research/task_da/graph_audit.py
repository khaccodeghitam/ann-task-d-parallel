"""Read-only ordered-graph audit and lossless PiPNN/NSG conversion.

Explicit little-endian uint32 contract; never guess a format from its suffix.
No third-party Python dependencies. Run with python -m research.task_da.graph_audit.
"""
from __future__ import annotations

import argparse
from array import array
from collections import Counter, deque
import hashlib
import json
import math
import mmap
from pathlib import Path
import struct

U32 = struct.Struct("<I")


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class Graph:
    """Memory mapped immutable input; offsets use 8 bytes per vertex."""

    def __init__(self, path, fmt, *, entry=None, expected_n=None):
        if fmt not in ("pipnn", "nsg"):
            raise ValueError("format must be pipnn or nsg")
        self.path, self.format = Path(path), fmt
        self._file = self.path.open("rb")
        self._data = None
        try:
            size = self.path.stat().st_size
            if size < 8 or size % 4:
                raise ValueError("truncated or unaligned graph")
            self._data = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
            if fmt == "pipnn":
                self.n, self.max_degree = self.word(0), self.word(4)
                self.entry = entry
                if not self.n or self.n > (size - 8) // 4:
                    raise ValueError("invalid vertex count/degree table")
                if expected_n is not None and expected_n != self.n:
                    raise ValueError("vertex count mismatch")
                pos = 8 + 4 * self.n
            else:
                self.max_degree, self.entry = self.word(0), self.word(4)
                if type(expected_n) is not int or not 0 < expected_n <= (size - 8) // 4:
                    raise ValueError("NSG requires a valid expected_n from base vectors")
                self.n, pos = expected_n, 8
                if entry is not None and entry != self.entry:
                    raise ValueError("cannot override NSG entry point")
            if type(self.entry) is not int or not 0 <= self.entry < self.n:
                raise ValueError("explicit in-range entry point required")
            self.offsets = array("Q")
            self.degrees = array("I")
            for node in range(self.n):
                if fmt == "nsg":
                    degree = self.word(pos)
                    pos += 4
                else:
                    degree = self.word(8 + 4 * node)
                if degree > self.max_degree or degree > (size - pos) // 4:
                    raise ValueError("invalid degree or truncated adjacency")
                self.offsets.append(pos)
                self.degrees.append(degree)
                for (neighbor,) in struct.iter_unpack("<I", self._data[pos:pos + 4 * degree]):
                    if neighbor >= self.n:
                        raise ValueError("neighbor ID out of range")
                pos += 4 * degree
            if pos != size:
                raise ValueError("trailing bytes or wrong vertex count")
        except BaseException:
            self.close()
            raise

    def word(self, offset):
        if offset + 4 > len(self._data):
            raise ValueError("truncated uint32")
        return U32.unpack_from(self._data, offset)[0]

    def neighbors(self, node):
        start = self.offsets[node]
        return [x[0] for x in struct.iter_unpack("<I", self._data[start:start + 4 * self.degrees[node]])]

    def node_bytes(self, node):
        start = self.offsets[node]
        return struct.pack("<II", node, self.degrees[node]) + self._data[start:start + 4 * self.degrees[node]]

    def ordered_digest(self):
        digest = hashlib.sha256(struct.pack("<I", self.n))
        for node in range(self.n):
            digest.update(self.node_bytes(node))
        return digest.hexdigest()

    def close(self):
        if self._data is not None:
            self._data.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def audit(graph):
    hist = Counter(graph.degrees)
    loops = duplicates = 0
    for node in range(graph.n):
        neighbors = graph.neighbors(node)
        loops += neighbors.count(node)
        duplicates += len(neighbors) - len(set(neighbors))
    seen = bytearray(graph.n)
    seen[graph.entry] = 1
    pending = deque([graph.entry])
    reachable = 1
    while pending:
        for node in graph.neighbors(pending.popleft()):
            if not seen[node]:
                seen[node] = 1
                reachable += 1
                pending.append(node)
    target, cumulative, p95 = math.ceil(.95 * graph.n), 0, 0
    for degree, count in sorted(hist.items()):
        cumulative += count
        if cumulative >= target:
            p95 = degree
            break
    return dict(scope="STRUCTURAL_ONLY_NOT_RECALL_OR_PERFORMANCE", status="PASS",
                format=graph.format, file_sha256=sha256(graph.path), vertices=graph.n,
                declared_max_degree=graph.max_degree, entry_point=graph.entry,
                arcs=sum(graph.degrees), degree_mean=sum(graph.degrees) / graph.n,
                degree_p95=p95, degree_max=max(graph.degrees), degree_histogram=dict(sorted(hist.items())),
                self_loops=loops, duplicate_arcs=duplicates, reachable_from_entry=reachable,
                strong_connectivity="NOT_MEASURED", ordered_adjacency_sha256=graph.ordered_digest(),
                topology_modified=False)


def convert(graph, output, fmt):
    if fmt not in ("pipnn", "nsg"):
        raise ValueError("unsupported output format")
    # Exclusive creation: immutable inputs and previous output are never replaced.
    with Path(output).open("xb") as stream:
        stream.write(struct.pack("<II", graph.n if fmt == "pipnn" else graph.max_degree,
                                 graph.max_degree if fmt == "pipnn" else graph.entry))
        if fmt == "pipnn":
            for degree in graph.degrees:
                stream.write(U32.pack(degree))
        for node in range(graph.n):
            if fmt == "nsg":
                stream.write(U32.pack(graph.degrees[node]))
            stream.write(graph.node_bytes(node)[8:])
    with Graph(output, fmt, entry=graph.entry, expected_n=graph.n) as after:
        return compare(graph, after)


def compare(before, after, per_node_output=None):
    if before.n != after.n:
        raise ValueError("vertex count mismatch")
    changed = []
    stream = Path(per_node_output).open("x") if per_node_output else None
    try:
        for node in range(before.n):
            left, right = before.node_bytes(node), after.node_bytes(node)
            if left != right:
                changed.append(node)
            if stream:
                stream.write(json.dumps(dict(node=node, before_sha256=hashlib.sha256(left).hexdigest(),
                                             after_sha256=hashlib.sha256(right).hexdigest())) + "\n")
    finally:
        if stream:
            stream.close()
    entry_equal = before.entry == after.entry
    return dict(status="PASS" if not changed and entry_equal else "NO-GO",
                scope="REPRESENTATION_PARITY_ONLY", changed_nodes=changed,
                entry_point_equal=entry_equal, before_sha256=sha256(before.path),
                after_sha256=sha256(after.path), before_ordered_sha256=before.ordered_digest(),
                after_ordered_sha256=after.ordered_digest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", required=True, choices=["pipnn", "nsg"])
    parser.add_argument("--entry", type=int)
    parser.add_argument("--expected-n", type=int)
    parser.add_argument("--convert-to", choices=["pipnn", "nsg"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--per-node-output", type=Path)
    args = parser.parse_args()
    if bool(args.convert_to) != bool(args.output) or (args.per_node_output and not args.output):
        parser.error("conversion requires --convert-to and --output; per-node output requires conversion")
    with Graph(args.input, args.format, entry=args.entry, expected_n=args.expected_n) as graph:
        result = audit(graph)
        if args.output:
            result["conversion"] = convert(graph, args.output, args.convert_to)
            with Graph(args.output, args.convert_to, entry=graph.entry, expected_n=graph.n) as after:
                result["conversion"] = compare(graph, after, args.per_node_output)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
