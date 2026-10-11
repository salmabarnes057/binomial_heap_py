import unittest

from binomial_heap_py import BinomialHeap, HeapNode, HeapEmptyError


class TestInsertionAndPeek(unittest.TestCase):
    def test_empty_heap_peek_raises(self):
        h = BinomialHeap()
        with self.assertRaises(HeapEmptyError):
            h.peek()

    def test_empty_heap_pop_raises(self):
        h = BinomialHeap()
        with self.assertRaises(HeapEmptyError):
            h.pop()

    def test_single_element(self):
        h = BinomialHeap()
        h.insert(5)
        self.assertEqual(len(h), 1)
        self.assertEqual(h.peek(), 5)

    def test_insert_in_descending_order_yields_ascending_pop(self):
        h = BinomialHeap()
        for v in [9, 7, 5, 3, 1]:
            h.insert(v)
        out = [h.pop() for _ in range(5)]
        self.assertEqual(out, [1, 3, 5, 7, 9])

    def test_insert_duplicates(self):
        h = BinomialHeap()
        for v in [3, 1, 3, 1, 2]:
            h.insert(v)
        out = [h.pop() for _ in range(5)]
        self.assertEqual(out, [1, 1, 2, 3, 3])

    def test_insert_with_custom_comparator(self):
        # max-heap via inverted comparator
        h = BinomialHeap(cmp=lambda a, b: (a < b) - (a > b))
        for v in [1, 5, 3, 9, 7]:
            h.insert(v)
        out = [h.pop() for _ in range(5)]
        self.assertEqual(out, [9, 7, 5, 3, 1])


class TestPopBehaviour(unittest.TestCase):
    def test_pop_all_then_empty(self):
        h = BinomialHeap()
        for v in range(20):
            h.insert(v)
        for expected in range(20):
            self.assertEqual(h.pop(), expected)
        self.assertEqual(len(h), 0)
        with self.assertRaises(HeapEmptyError):
            h.pop()

    def test_pop_on_single_returns_value(self):
        h = BinomialHeap([42])
        self.assertEqual(h.pop(), 42)
        self.assertEqual(len(h), 0)

    def test_interleaved_insert_and_pop(self):
        h = BinomialHeap()
        h.insert(5)
        h.insert(2)
        self.assertEqual(h.pop(), 2)
        h.insert(1)
        h.insert(8)
        self.assertEqual(h.pop(), 1)
        self.assertEqual(h.pop(), 5)
        self.assertEqual(h.pop(), 8)
        self.assertEqual(len(h), 0)


class TestUnion(unittest.TestCase):
    def test_union_two_nonempty_heaps(self):
        a = BinomialHeap([1, 4, 7])
        b = BinomialHeap([2, 3, 5, 8])
        a.union(b)
        self.assertEqual(len(a), 7)
        self.assertEqual(len(b), 0)
        self.assertEqual([a.pop() for _ in range(7)], [1, 2, 3, 4, 5, 7, 8])

    def test_union_leaves_other_empty(self):
        a = BinomialHeap([1])
        b = BinomialHeap([2])
        a.union(b)
        self.assertEqual(len(b), 0)
        self.assertFalse(b)

    def test_union_into_empty(self):
        a = BinomialHeap()
        b = BinomialHeap([3, 1, 2])
        a.union(b)
        self.assertEqual([a.pop() for _ in range(3)], [1, 2, 3])

    def test_union_empty_into_nonempty(self):
        a = BinomialHeap([3, 1, 2])
        b = BinomialHeap()
        a.union(b)
        self.assertEqual([a.pop() for _ in range(3)], [1, 2, 3])

    def test_union_self_raises(self):
        a = BinomialHeap([1, 2])
        with self.assertRaises(ValueError):
            a.union(a)
        # Heap should be unchanged by the rejected union
        self.assertEqual(len(a), 2)

    def test_union_mismatched_comparators_raises(self):
        a = BinomialHeap(cmp=lambda x, y: (x > y) - (x < y))  # max-heap cmp
        b = BinomialHeap()  # default min cmp
        a.insert(1)
        b.insert(2)
        with self.assertRaises(ValueError):
            a.union(b)


class TestStructure(unittest.TestCase):
    def test_roots_have_distinct_orders_after_inserts(self):
        # After inserting n elements, the binomial forest has at most one tree
        # per order, mirroring the binary representation of n.
        h = BinomialHeap()
        for _ in range(15):
            h.insert(0)
        orders = sorted(r.order for r in h._roots)
        self.assertEqual(orders, [0, 1, 2, 3])  # 15 = 0b1111

    def test_heap_node_link_invariants(self):
        a = HeapNode(1)
        b = HeapNode(2)
        c = HeapNode.link(a, b)
        self.assertEqual(c.order, 1)
        self.assertEqual(len(c.children), 1)
        self.assertEqual(c.children[0].value, 2)

    def test_constructor_takes_iterable(self):
        h = BinomialHeap([5, 1, 3])
        self.assertEqual(len(h), 3)
        self.assertEqual(h.peek(), 1)

    def test_bool_protocol_matches_len(self):
        h = BinomialHeap()
        self.assertFalse(bool(h))
        h.insert(1)
        self.assertTrue(bool(h))
        h.pop()
        self.assertFalse(bool(h))


if __name__ == "__main__":
    unittest.main()
