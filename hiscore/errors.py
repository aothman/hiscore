"""
hiscore.errors

Errors that can arise from creating scores.

:copyright: (c) 2014 by Abraham Othman.
:license: AGPL, see LICENSE for details.
"""
import numpy as np

class MonotoneError(Exception):
  def __init__(self, a, va, b, vb):
    self.a = np.array(a)
    self.va = float(va)
    self.b = np.array(b)
    self.vb = float(vb)

  def __str__(self):
    return "Monotonicty Constraint Violated: (%s,%f) is inconsistent with (%s,%f)" % (np.array_str(self.a),self.va,np.array_str(self.b),self.vb)

class MonotoneBoundsError(Exception):
  def __init__(self,x,v,bound,kind):
    self.x = np.array(x)
    self.v = float(v)
    self.bound = bound
    self.kind = kind

  def __str__(self):
    return "Bounds Violated: %s has a value of %f but the %s was specified as %f" % (np.array_str(self.x),self.v,self.kind,self.bound)

class ScoreCreationError(Exception):
  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return self.msg