"""
hiscore.engine

Core methods for creating and calculating scoring functions.

:copyright: (c) 2014 by Abraham Othman.
:license: AGPL, see LICENSE for details.
"""
import numpy as np
from errors import MonotoneError, MonotoneBoundsError, ScoreCreationError
import cvxpy as cvx

def create(reference_set_dict, monotone_relationship, minval=None, maxval=None):
  """
  Create a scoring function that maps objects with N attributes to scores.

  Required arguments:
  reference_set_dict -- A reference set mapping objects to scores.
  monotone_relationship -- A length-N vector with +1/-1 entries. +1 indicates scores should be increasing in that attribute, -1 decreasing.

  Keyword arguments:
  minval -- The smallest allowed value for the scoring function Defaults to None, meaning no lower bound.
  maxval -- The largest allowed value for the scoring function. Defaults to None, meaning no upper bound.
  """
  return HiScoreEngine(reference_set_dict, monotone_relationship, minval, maxval)

class HiScoreEngine:
  """ Main scoring function class. """
  def __init__(self,reference_set_dict, monotone_relationship, minval, maxval):
    """ Initialize a scoring function. Called through create() above. """
    np_input = np.array(reference_set_dict.keys(), dtype=float)
    self.monorel = np.array(monotone_relationship)
    if not np.sum(np.absolute(self.monorel)) == len(monotone_relationship):
      raise ScoreCreationError("Entries in monotone_relationship vector must be 1 or -1 exclusively.")
    # Scale all values to fall in unit length
    self.scale = self.monorel*(np.clip(np.amax(np_input, axis=0)-np.amin(np_input, axis=0),.001,1000))
    # Create new structure to hold the scaled reference set
    self.points = {}
    for (p,v) in reference_set_dict.iteritems():
      key = np.array(p)/self.scale
      self.points[tuple(key.tolist())]=v
    # minval/maxval intelligent handling
    if minval is not None:
      self.minval = float(minval)
    else:
      self.minval = None
    if maxval is not None:
      self.maxval = float(maxval)
    else:
      self.maxval = None
    self.__check_monotonicity__()
    if not (minval is None and maxval is None):
      self.__check_bounds__()

    self.dim = len(monotone_relationship)
    # Solve the optimization
    plus_vals, minus_vals = self.__solve__()
    # point_objs holds the cones emanating from each point
    self.point_objs = []
    for ((p,v),plusv,minusv) in zip(self.points.iteritems(), plus_vals, minus_vals):
      sp,ip = zip(*plusv)
      sm,im = zip(*minusv)
      self.point_objs.append(Point(p,v,sp,sm,ip,im))

  def __solve__(self):
    """ Solve the optimization problem associated with each point """
    
    # Cones on the plus and minus side
    sup_plus_vars = cvx.Variable(len(self.points), self.dim)
    inf_plus_vars = cvx.Variable(len(self.points), self.dim)
    sup_minus_vars = cvx.Variable(len(self.points), self.dim)
    inf_minus_vars = cvx.Variable(len(self.points), self.dim)
    constraints = [sup_plus_vars >= 0, inf_plus_vars >= 0, sup_minus_vars >= 0, sup_plus_vars >= 0]

    # inf/sup relational constraints
    constraints += [sup_plus_vars >= inf_plus_vars]
    constraints += [sup_minus_vars <= inf_minus_vars]

    # Cone constraints
    for (i,(pone,vone)) in enumerate(self.points.iteritems()):
      # point i has to be able to project into point j
      for (j,(ptwo,vtwo)) in enumerate(self.points.iteritems()):
        if i==j: continue
        lhs_sup = 0.0
        lhs_inf = 0.0
        for (di,(poned,ptwod)) in enumerate(zip(pone,ptwo)):
          run = ptwod - poned
          supvar = 0.0
          infvar = 0.0
          if ptwod > poned:
            supvar = sup_plus_vars[i,di]
            infvar = inf_plus_vars[i,di]
          elif ptwod < poned:
            supvar = sup_minus_vars[i,di]
            infvar = inf_minus_vars[i,di]
          lhs_sup += run*supvar
          lhs_inf += run*infvar
        constraints += [lhs_sup >= vtwo-vone, lhs_inf <= vtwo-vone]

    # Optimization : minimize cone width
    objective = cvx.Minimize(cvx.norm(sup_plus_vars-inf_plus_vars)+cvx.norm(inf_minus_vars-sup_minus_vars))
    p = cvx.Problem(objective, constraints)
    # Run it!
    try:
      p.solve(verbose=False, solver=cvx.CVXOPT, kktsolver='robust', refinement=3)
    except Exception as e:
      print e
    # Post-mortem...
    if p.status != 'optimal' and p.status != 'optimal_inaccurate':
      raise ScoreCreationError("Could not create scoring function: Optimization Failed")
      return None
    # Pull out the coefficients from the variables
    plus_vars = [[(sup_plus_vars[i,j].value,inf_plus_vars[i,j].value) for j in xrange(self.dim)] for i in xrange(len(self.points))]
    minus_vars = [[(sup_minus_vars[i,j].value,inf_minus_vars[i,j].value) for j in xrange(self.dim)] for i in xrange(len(self.points))]
    return plus_vars, minus_vars

  def __monotone_rel__(self,a,b):
    """ 
    Returns 1 if a > b, -1 if a < b, 0 otherwise
    Assumes self.scale adjustment has already been made
    """
    adj_diff = np.array(a)-np.array(b)
    if min(adj_diff) >= 0 and max(adj_diff) > 0:
      return 1
    elif max(adj_diff) > 0 and min(adj_diff) < 0:
      return 0
    else:
      return -1

  def __check_monotonicity__(self):
    """ Check monotone relationships of points. Raises MonotoneError on failure. """
    for (x,v) in self.points.iteritems():
      points_greater_than = filter(lambda point: x==point or self.__monotone_rel__(point,x)==1, self.points.keys())
      for gt in points_greater_than:
        if self.points[gt] < v:
          raise MonotoneError(np.array(gt)*self.scale,self.points[gt],np.array(x)*self.scale,v)
      points_less_than = filter(lambda point: x==point or self.__monotone_rel__(x,point)==1, self.points.keys())
      for lt in points_less_than:
        if self.points[lt] > v:
          raise MonotoneError(np.array(lt)*self.scale,self.points[lt],np.array(x)*self.scale,v)

  def __check_bounds__(self):
    """ Check that all (adjusted) points are within bounds. Raises MonotoneBoundsError on failure. """
    maxtest = 1e47 if self.maxval is None else self.maxval
    mintest = -1e47 if self.minval is None else self.minval
    for (x,v) in self.points.iteritems():
      if v > maxtest:
        raise MonotoneBoundsError(x*self.scale,v,self.maxval,"maximum")
      if v < mintest:
        raise MonotoneBoundsError(x*self.scale,v,self.minval,"minimum")

  def value_bounds(self, point):
    """
    Returns the (lower_bound, upper_bound) tuple of a point implied by the reference set and the monotone relationship vector.
    Use it to improve and understand the reference set without triggering a MonotoneError.
    Returns np.inf as the second argument if there is no upper bound and np.NINF as the first argument if there is no lower bound.

    Required argument:
    point -- Point at which to assess upper and lower bounds.
    """
    padj = point/self.scale
    points_greater_than = filter(lambda x: np.allclose(x,padj) or self.__monotone_rel__(x,padj)==1, self.points.keys())
    points_less_than = filter(lambda x: np.allclose(x,padj) or self.__monotone_rel__(padj,x)==1, self.points.keys())
    gtbound = np.inf if self.maxval is None else self.maxval
    ltbound = np.NINF if self.minval is None else self.minval
    for p in points_greater_than:
      gtbound = min(self.points[p],gtbound)
    for p in points_less_than:
      ltbound = max(self.points[p],ltbound)
    return ltbound, gtbound
  
  def calculate(self,xs):
    """
    Calculate the scoring function at an iterable of points.
    Returns a list of scalars, the evaluations at each point.

    Required argument:
    xs -- iterable, points at which to evaluate the scoring function.
    """
    retval = []
    for x in xs:
      # Bound value between sup and infs implied by point object cones
      xadj = np.array(x)/self.scale
      supval = min([p.find_sup(xadj) for p in self.point_objs])
      infval = max([p.find_inf(xadj) for p in self.point_objs])
      if self.maxval is not None:
        supval = min(supval,self.maxval)
        infval = min(infval,self.maxval)
      if self.minval is not None:
        supval = max(supval, self.minval)
        infval = max(infval, self.minval)
      # Value is halfway in-between these bounds
      retval.append((supval+infval)/2.0)
    return retval

class Point:
    """ Point objects are used internally to represent a reference set point and a cone """
    def __init__(self, where, value, sup_plus, sup_minus, inf_plus, inf_minus):
      self.where = np.array(where)
      self.value = value
      self.sup_plus = np.array(sup_plus)
      self.sup_minus = np.array(sup_minus)
      self.inf_plus = np.array(inf_plus)
      self.inf_minus = np.array(inf_minus)

    def find_sup(self, other):
      """ Largest possible value other can have based on the emanating cone from this point """
      diff = other-self.where
      sup_sum = diff*(diff > 0)*self.sup_plus + diff*(diff < 0)*self.sup_minus
      return self.value + np.sum(sup_sum)

    def find_inf(self, other):
      """ Smallest possible value other can have based on the emanating cone from this point """
      diff = other-self.where
      inf_sum = diff*(diff > 0)*self.inf_plus + diff*(diff < 0)*self.inf_minus
      return self.value + np.sum(inf_sum)