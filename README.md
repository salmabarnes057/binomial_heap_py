# binomial_heap_py

A small, zero-dependency Python implementation of the binomial heap: a
priority queue whose distinguishing feature is fast worst-case union.

```python
from binomial_heap_py import BinomialHeap

a = BinomialHeap([3, 1, 4])
b = BinomialHeap([2, 1, 5])
a.union(b)          # b is now empty; a holds all six values

print(a.peek())     # 1
print(a.pop())      # 1
print(len(a))       # 5
```

Exported names: `BinomialHeap`, `HeapNode`, `HeapEmptyError`.

## Why this exists

When you need to merge two priority queues repeatedly, a plain binary heap
forces you to pop every element from one and push it into the other —
O(n log n). A binomial heap does the same merge in O(log n + log m) by
splicing two forests of binomial trees together, the way you would add two
binary numbers. This library exists for that case.

The trade-off: binomial heaps have higher constant factors than binary
heaps on plain insert and pop. If you never call `union`, use `heapq`
instead.

## Edge cases worth knowing

* `union(self, self)` raises `ValueError`. The operation is only meaningful
  between two distinct heaps; passing the same object would double-count
  nodes and corrupt the size counter.
* `union` with heaps built under different comparators raises `ValueError`.
  The library does not attempt to reconcile two orderings; pick one and use
  it consistently.
* `pop` and `peek` raise `HeapEmptyError` when the heap has no elements —
  they do not return a sentinel.
* `union` mutates `other`, leaving it empty. If you need to keep `other`,
  build a second heap and union that instead.
