from __future__ import annotations
from typing import Callable, List, Optional, Generic, TypeVar, Iterable

T = TypeVar("T")


class HeapEmptyError(Exception):
    """Raised when pop/peek is called on a heap with no elements."""


def _default_cmp(a: T, b: T) -> int:
    """Total-order fallback comparator using ``<`` and ``>``.

    We avoid subtraction because not every ordered type supports it (strings,
    tuples). Using the rich comparisons is general and works for any type that
    defines ``__lt__`` and ``__gt__``.
    """
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


class HeapNode(Generic[T]):
    __slots__ = ("value", "children", "order")

    def __init__(self, value: T) -> None:
        self.value: T = value
        self.children: List["HeapNode[T]"] = []
        self.order: int = 0

    @staticmethod
    def link(a: "HeapNode[T]", b: "HeapNode[T]") -> "HeapNode[T]":
        a.children.append(b)
        a.order += 1
        return a


def _merge_forests(
    a: List[HeapNode[T]], b: List[HeapNode[T]]
) -> List[HeapNode[T]]:
    out: List[HeapNode[T]] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i].order <= b[j].order:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def _carry_reduce(roots: List[HeapNode[T]], cmp: Callable[[T, T], int]) -> List[HeapNode[T]]:
    if not roots:
        return []
    result: List[HeapNode[T]] = [roots[0]]
    for nxt in roots[1:]:
        cur = result.pop()
        if cur.order == nxt.order:
            if cmp(cur.value, nxt.value) <= 0:
                merged = HeapNode.link(cur, nxt)
            else:
                merged = HeapNode.link(nxt, cur)
            result.append(merged)
        else:
            result.append(cur)
            result.append(nxt)
    return result


class BinomialHeap(Generic[T]):
    __slots__ = ("_roots", "_cmp", "_size")

    def __init__(
        self,
        values: Optional[Iterable[T]] = None,
        *,
        cmp: Callable[[T, T], int] = _default_cmp,
    ) -> None:
        self._cmp = cmp
        self._roots: List[HeapNode[T]] = []
        self._size = 0
        if values is not None:
            for v in values:
                self.insert(v)

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def insert(self, value: T) -> None:
        node = HeapNode(value)
        self._roots = _carry_reduce(_merge_forests(self._roots, [node]), self._cmp)
        self._size += 1

    def peek(self) -> T:
        if not self._roots:
            raise HeapEmptyError("peek from empty heap")
        idx = self._argmin_root()
        return self._roots[idx].value

    def pop(self) -> T:
        if not self._roots:
            raise HeapEmptyError("pop from empty heap")
        idx = self._argmin_root()
        node = self._roots[idx]
        rest = self._roots[:idx] + self._roots[idx + 1:]
        self._roots = _carry_reduce(_merge_forests(rest, node.children), self._cmp)
        self._size -= 1
        return node.value

    def union(self, other: "BinomialHeap[T]") -> None:
        if self is other:
            raise ValueError("cannot union a heap with itself")
        if self._cmp is not other._cmp:
            raise ValueError("cannot union heaps with different comparators")
        merged = _merge_forests(self._roots, other._roots)
        self._roots = _carry_reduce(merged, self._cmp)
        self._size += other._size
        other._roots = []
        other._size = 0

    def _argmin_root(self) -> int:
        best = 0
        for i in range(1, len(self._roots)):
            if self._cmp(self._roots[i].value, self._roots[best].value) < 0:
                best = i
        return best
