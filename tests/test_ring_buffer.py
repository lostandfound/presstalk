import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.ring_buffer import RingBuffer


class TestRingBuffer(unittest.TestCase):
    def test_capacity_and_size(self):
        rb = RingBuffer(8)
        self.assertEqual(rb.capacity(), 8)
        self.assertEqual(rb.size(), 0)

    def test_write_and_snapshot(self):
        rb = RingBuffer(8)
        rb.write(b"abcd")
        self.assertEqual(rb.size(), 4)
        self.assertEqual(rb.snapshot_tail(2), b"cd")
        self.assertEqual(rb.snapshot_tail(10), b"abcd")

    def test_trim_when_overflow(self):
        rb = RingBuffer(5)
        rb.write(b"abc")
        rb.write(b"def")  # total 6, capacity 5 -> oldest 'a' dropped
        self.assertEqual(rb.size(), 5)
        self.assertEqual(rb.snapshot_tail(5), b"bcdef")
        rb.write(b"XYZ")  # now buffer should be last 5 of 'bcdefXYZ' -> 'efXYZ'
        self.assertEqual(rb.snapshot_tail(5), b"efXYZ")

    def test_zero_and_negative_snapshot(self):
        rb = RingBuffer(4)
        rb.write(b"hi")
        self.assertEqual(rb.snapshot_tail(0), b"")
        self.assertEqual(rb.snapshot_tail(-1), b"")

    def test_write_none_or_empty(self):
        rb = RingBuffer(3)
        rb.write(None)
        rb.write(b"")
        self.assertEqual(rb.size(), 0)


if __name__ == "__main__":
    unittest.main()
