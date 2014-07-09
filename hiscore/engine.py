import numpy
from exceptions import MonotoneError, MonotoneBoundsError, ScoreCreationError

def create(reference_set_dict, monotone_relationship, minval=None, maxval=None):
  return HiScoreEngine(reference_set_dict, monotone_relationship, minval, maxval)

class HiScoreEngine:
  def __init__(reference_set_dict, monotone_relationship, minval, maxval):
    self.points = reference_set_dict
    self.monorel = np.array(monotone_relationship)
    if self.minval is not None:
      self.minval = float(minval)
    if self.maxval is not None:
      self.maxval = float(maxval)
    self.__check_monotonicity__()
    if not (minval is None and maxval is None):
      self.__check_bounds__()

    self.dim = len(monotone_relationship)
    sup_vals, inf_vals = self.__solve__()
    self.point_objs = []
    for ((p,v),(sp,sm),(ip,im)) in zip(self.points.iteritems, sup_vals, inf_vals):
      self.point_objs.append(Point(p,v,sp,sm,ip,im)

  def __solve__(self):
    pass

  def __monotone_rel__(self,a,b):
    # returns 1 if a > b, -1 if a < b, 0 otherwise
    adj_diff = self.monorel*(np.array(a)-np.array(b))
    if min(adj_diff) >= 0 and max(adj_diff) > 0:
      return 1
    elif max(adj_diff) > 0 and min(adj_diff) < 0:
      return 0
    else:
      return -1

  def __check_monotonicity__(self):
    for (x,v) in self.points.iteritems():
      points_greater_than = filter(lambda x: x==point or self.__monotone_rel__(x,point)==1, self.points.keys())
      for gt in points_greater_than:
        if self.points[gt] < v:
          raise MonotoneError(gt,self.points[gt],x,v)
      points_less_than = filter(lambda x: x==point or self.__monotone_rel__(point,x)==1, self.points.keys())
      for lt in points_less_than:
        if self.points[lt] > v:
          raise MonotoneError(lt,self.points[lt],x,v)

  def __check_bounds__(self):
    maxtest = 1e47 if self.maxval is None else self.maxval
    mintest = -1e47 if self.minval is None else self.minval
    for (x,v) in self.points.iteritems():
      if v > maxtest:
        raise MonotoneBoundsError(x,v,self.maxval,"maximum")
      if v < mintest:
        raise MonotoneBoundsError(x,v,self.minval,"minimum")

  class Point:
    def __init__(self, where, value, sup_plus, sup_minus, inf_plus, inf_minus):
      self.where = np.array(where)
      self.value = value
      self.sup_plus = np.array(sup_plus)
      self.sup_minus = np.array(sup_minus)
      self.inf_plus = np.array(inf_plus)
      self.inf_minus = np.array(inf_minus)

    def find_sup(self, other):
      diff = other-self.where
      sup_sum = diff*(diff > 0)*sup_plus + diff*(diff < 0)*sup_minus
      return self.value + np.sum(sup_sum)

    def find_inf(self, other):
      diff = other-self.where
      inf_sum = diff*(diff > 0)*inf_plus + diff*(diff < 0)*inf_minus
      return self.value + np.sum(inf_sum)

  def calculate(self,xs):
    retval = np.zeros_like(xs)
    for (i,x) in enumerate(xs):
      supval = min([p.find_sup(x) for p in self.point_objs])
      infval = max([p.find_inf(x) for p in self.point_objs])
      if self.maxval is not None:
        supval = min(supval,self.maxval)
      if self.minval is not None:
        infval = max(infval, self.minval)
      retval[i] = (supval+infval)/2.0
    return retval

  def value_bounds(self, point):
    points_greater_than = filter(lambda x: x==point or self.__monotone_rel__(x,point)==1, self.points.keys())
    points_less_than = filter(lambda x: x==point or self.__monotone_rel__(point,x)==1, self.points.keys())
    gtbound = 1e47 if self.maxval is None and points_greater_than else self.maxval
    ltbound = -1e47 if self.minval is None and points_less_than else self.minval
    for p in points_greater_than:
      gtbound = min(self.points[p],gtbound)
    for p in points_less_than:
      ltbound = max(self.points[p],ltbound)
    return ltbound, gtbound

  def picture(self,indices,values,labels=None):
    pass