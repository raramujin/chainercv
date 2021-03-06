import numpy as np
import six
import unittest

from chainer import testing

from chainercv.chainer_experimental.datasets.sliceable import SliceableDataset


class SampleDataset(SliceableDataset):

    def __len__(self):
        return 10

    @property
    def keys(self):
        return ('item0', 'item1', 'item2')

    def get_example_by_keys(self, i, key_indices):
        return tuple(
            '{:s}({:d})'.format(self.keys[key_index], i)
            for key_index in key_indices)


@testing.parameterize(
    {'iterable': tuple},
    {'iterable': list},
    {'iterable': np.array},
)
class TestSliceableDataset(unittest.TestCase):

    def setUp(self):
        self.dataset = SampleDataset()

    def test_base(self):
        self.assertEqual(
            self.dataset[0], ('item0(0)', 'item1(0)', 'item2(0)'))

    def test_slice_keys_single_name(self):
        dataset = self.dataset.slice[:, 'item0']
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, 'item0')
        self.assertEqual(dataset[1], 'item0(1)')

    def test_slice_keys_single_index(self):
        dataset = self.dataset.slice[:, 0]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, 'item0')
        self.assertEqual(dataset[1], 'item0(1)')

    def test_slice_keys_single_tuple_name(self):
        if self.iterable is np.array:
            self.skipTest('ndarray of strings is not supported')
        dataset = self.dataset.slice[:, self.iterable(('item1',))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, ('item1',))
        self.assertEqual(dataset[2], ('item1(2)',))

    def test_slice_keys_single_tuple_index(self):
        dataset = self.dataset.slice[:, self.iterable((1,))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, ('item1',))
        self.assertEqual(dataset[2], ('item1(2)',))

    def test_slice_keys_multiple_name(self):
        if self.iterable is np.array:
            self.skipTest('ndarray of strings is not supported')
        dataset = self.dataset.slice[:, self.iterable(('item0', 'item2'))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, ('item0', 'item2'))
        self.assertEqual(dataset[3], ('item0(3)', 'item2(3)'))

    def test_slice_keys_multiple_index(self):
        dataset = self.dataset.slice[:, self.iterable((0, 2))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, ('item0', 'item2'))
        self.assertEqual(dataset[3], ('item0(3)', 'item2(3)'))

    def test_slice_keys_multiple_bool(self):
        dataset = self.dataset.slice[:, self.iterable((True, False, True))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, ('item0', 'item2'))
        self.assertEqual(dataset[3], ('item0(3)', 'item2(3)'))

    def test_slice_keys_multiple_mixed(self):
        if self.iterable is np.array:
            self.skipTest('ndarray of strings is not supported')
        dataset = self.dataset.slice[:, self.iterable(('item0', 2))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), len(self.dataset))
        self.assertEqual(dataset.keys, ('item0', 'item2'))
        self.assertEqual(dataset[3], ('item0(3)', 'item2(3)'))

    def test_slice_keys_invalid_name(self):
        with self.assertRaises(KeyError):
            self.dataset.slice[:, 'invalid']

    def test_slice_keys_invalid_index(self):
        with self.assertRaises(IndexError):
            self.dataset.slice[:, 3]

    def test_slice_keys_invalid_bool(self):
        with self.assertRaises(ValueError):
            self.dataset.slice[:, (True, False)]

    def test_slice_indices_slice(self):
        dataset = self.dataset.slice[3:8:2]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), 3)
        self.assertEqual(dataset.keys, self.dataset.keys)
        self.assertEqual(
            dataset[1], ('item0(5)', 'item1(5)', 'item2(5)'))

    def test_slice_indices_list(self):
        if self.iterable is tuple:
            self.skipTest('tuple indices is not supported')
        dataset = self.dataset.slice[self.iterable((2, 1, 5))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), 3)
        self.assertEqual(dataset.keys, self.dataset.keys)
        self.assertEqual(
            dataset[0], ('item0(2)', 'item1(2)', 'item2(2)'))

    def test_slice_indices_bool(self):
        if self.iterable is tuple:
            self.skipTest('tuple indices is not supported')
        dataset = self.dataset.slice[self.iterable(
            (False, True, False, False, True,
             True, False, False, True, False))]
        self.assertIsInstance(dataset, SliceableDataset)
        self.assertEqual(len(dataset), 4)
        self.assertEqual(dataset.keys, self.dataset.keys)
        self.assertEqual(
            dataset[1], ('item0(4)', 'item1(4)', 'item2(4)'))

    def test_slice_indices_invalid_bool(self):
        with self.assertRaises(ValueError):
            self.dataset.slice[[False, True]]

    def test_iter(self):
        it = iter(self.dataset)
        for i in six.moves.range(len(self.dataset)):
            self.assertEqual(
                next(it), (
                    'item0({:d})'.format(i),
                    'item1({:d})'.format(i),
                    'item2({:d})'.format(i),
                ))
        with self.assertRaises(StopIteration):
            next(it)


testing.run_module(__name__, __file__)
