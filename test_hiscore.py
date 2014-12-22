""" Tests for HiScore """
import numpy as np
import unittest
import hiscore
import pytest
from hiscore.engine import create
from hiscore.errors import MonotoneError, MonotoneBoundsError, ScoreCreationError
import pickle


class EngineTestCase(unittest.TestCase):
	def test_bad_monotone_vector(self):
		mydict = {(0,0,0): 100, (1,1,1): 0}
		with pytest.raises(ScoreCreationError):
			create(mydict,[-1,-1,0])

	def test_non_monotone_mixed(self):
		mydict = {(0,0,5): 100, (5,5,0): 0}
		with pytest.raises(MonotoneError):
			create(mydict,[1,1,-1])

	def test_non_monotone_all_increasing(self):
		mydict = {(0,0,0): 100, (1,1,1): 0}
		with pytest.raises(MonotoneError):
			create(mydict,[1,1,1])

	def test_non_monotone_all_decreasing(self):
		mydict = {(1,1,1): 100, (0,0,0): 0}
		with pytest.raises(MonotoneError):
			create(mydict,[-1,-1,-1])

	def test_min_bounds(self):
		mydict = {(1,1,1): 100, (0,0,0): 0}
		with pytest.raises(MonotoneBoundsError):
			create(mydict,[1,1,1],minval=10)
	
	def test_max_bounds(self):
		mydict = {(100,100,100): 100, (0,0,0): 0}
		with pytest.raises(MonotoneBoundsError):
			create(mydict,[1,1,1],maxval=90)
	
	def test_interpolation(self):
		mydict = {(50,1,1): 100, (0,0,0): 0}
		myfunc = create(mydict,[1,1,1],maxval=100,minval=0)
		self.assertTrue(np.allclose(myfunc.calculate([(0,0,0),(50,1,1)]),[0,100]))
	
	def test_min_and_max(self):
		mydict = {(1,1,1): 100, (0,0,0): 0}
		myfunc = create(mydict,(1,1,1),maxval=100,minval=0.0)
		self.assertEqual(myfunc.calculate([(-1,-1,-1)])[0],0.0)
		self.assertEqual(myfunc.calculate([(2,2,2)])[0],100.0)

	def test_value_bounds(self):
		mydict = {(10,10,1): 50, (0,0,0): 20}
		myfunc = create(mydict,[1,1,1],maxval=100,minval=0.0)
		self.assertEqual(myfunc.value_bounds((5,5,0.5)),(20,50))
		self.assertEqual(myfunc.value_bounds((10,10,1)),(50,50))
		self.assertEqual(myfunc.value_bounds((20,20,2)),(50,100))
		self.assertEqual(myfunc.value_bounds((0,0,1)),(20,50))
		self.assertEqual(myfunc.value_bounds((0,0,0)),(20,20))
		self.assertEqual(myfunc.value_bounds((-1,0,0)),(0,20))

	def test_value_bounds_min_max(self):
		mydict = {(100,100,100): 50, (0,200,0): 50}
		myfunc = create(mydict,[1,1,1],maxval=100,minval=0.0)
		self.assertEqual(myfunc.value_bounds((50,50,50)),(0,50))
		myfunc = create(mydict,[-1,-1,-1],maxval=100,minval=0.0)
		self.assertEqual(myfunc.value_bounds((50,50,50)),(50,100))

	def test_pickling(self):
		mydict = {(0,0): 0, (100,100): 100}
		myfunc = create(mydict,[1,1])
		self.assertEqual(myfunc.calculate([5,10]),pickle.loads(pickle.dumps(myfunc)).calculate([5,10]))