# HiScore

A *scoring function* maps between objects (tuples of numerical attributes) and scores (a single numerical value). Scoring functions can rank objects too; just order by score. **HiScore** is a python library for making scoring functions through *reference sets*: a set of objects that are assigned scores. By updating and changing the reference set, domain experts can easily create and maintain sophisticated scores.

## Attributes
**HiScore** requires that **attributes involved in a score must be monotone**. This means that a score must always be non-decreasing or non-increasing if the value in each dimension moves in isolation. This is typically a natural restriction as the attributes of an object usually measure something that is either good or bad.

## Example Use
Consider a network security company that assess threats on two axes:

1. The certainty that the threat is real ("Certainty"),
2. The potential risk from the threat. ("Risk")

that wants to develop a scoring function from 0 to 100 that is increasing in certainty and risk.

Assuming that both the certainty and risk attributes are in [0,10], using their domain expertise the company develops the following reference set that maps objects to the scores they think are appropriate:

	Certainty | Risk | Score
	--------- | ---- | -----
	0  | 0  | 0
	10 | 10 | 100
	5  | 5  | 20
	10 | 8  | 90
	8  | 10 | 80
	3  | 10 | 20
	10 | 2  | 15

You can generate a scoring function by calling `hiscore.create` with this reference set:

```python	
import hiscore
reference_set = {(0,0): 0, (10,10): 100, (5,5): 20, (10,8): 90, (8,10): 80, (3,10): 20, (10,2): 15}
score_function = hiscore.create(reference_set, (1,1), minval=0, maxval=100)
```

The resulting function interpolates exactly through the reference set:

```python	
zip(reference_set.keys(), score_function.calculate(reference_set.keys()))
# Returns [((10, 8), 90.0), ((0, 0), 0.0), ((5, 5), 20.0), ((10, 10), 100.0), ((3, 10), 20.0), ((8, 10), 80.0), ((10, 2), 15.0)]
```

While producing reasonable estimates for points that are not in the reference set

```python
import numpy as np
np.round(score_function.calculate([(9,9)]))
# Returns [84.]
```

And also obeying monotonicity, so that increasing certainty or risk increases the score

```python
np.round(score_function.calculate([(7,7),(7,8),(7,9),(7,10)]))
# Returns [49., 58., 62., 68.]
np.round(score_function.calculate([(7,7),(8,7),(9,7),(10,7)]))
# Returns [49., 59., 70., 78.]
```

Here's a three-dimensional figure of the resulting scoring function:

![Demonstration Score Function](http://www.cs.cmu.edu/~aothman/score_function_demo.png)

Observe that it is monotone increasing along both axes and piecewise linear, but also how it picks up on shape features from the reference set.

## Why HiScore?

**HiScore** is designed with three qualities in mind:
+ Ease-of-Use. While **HiScore** can produce mathematically sophisticated scores with complex non-linear relationships between attributes, the code takes care of all this math internally. It requires only domain expertise, *not* mathematical expertise.
+ Performance. **HiScore** can quickly produce meaningful scores over very large domains with dozens or even hundreds of attributes.
+ Maintainability. **HiScore** is designed to make scoring functions that get better over time.

The traditional approach to scoring looks like this:

1.  A mathematically adept domain expert comes up with a set of descriptive scoring functions. (For instance, a radial function scoring a location's distance to the nearest grocery store, or an exponential  dropoff function scoring time since a credit card applicant's last credit default.)
2. The domain expert determines how to combine those functions.
3. The domain expert checks the resulting score function against a reference set of objects to see if the score of those objects "looks right".
4. The above steps are repeated until the expert is satisfied.

While this approach can be quick and intuitive, it ossifies quickly; eventually experts stop modifying the score even when they see mis-scored points because fiddling with basis functions and their coefficients introduces more errors than it fixes.

In contrast, **HiScore** allows domain experts to fix observed errors quickly: just add the erroneous point (with its correct score) to the reference set, and re-run the scoring engine.

## API

*	create(reference_set_dict, monotone_relationship, minval=None, maxval=None)
	*	reference_set_dict: The reference set, keys are objects (tuples) and values are scores.
	*	monotone_relationship: An iterable with entries that are +/- 1. +1 means the score function should be increasing along that attribute, -1 means the score function should be decreasing.
	*	minval, maxval: Floats, the minimum and maximum values for the function.
	*	Returns a HiScoreEngine object that can be queried for function values.

*	calculate(xs)
	*	xs: An iterable of tuples
	*	Returns score function evaluations at each of the tuples

*	value_bounds(object)
	* 	object: A single tuple
	* 	Returns (minimum value, maximum value) based on other entries in the reference set and defined limits.

## Installation and Requirements

To install **HiScore**, just run

```bash
$ pip install hiscore
```

In addition to `numpy`, **HiScore** requires the python libraries of the [Gurobi optimizer](http://www.gurobi.com) in order to `hiscore.create` scoring functions. Once the scoring function is created, further calls (e.g., to `calculate`) do not require use of the Gurobi libraries.

While Gurobi is not free software, it offers several attractive licensing options, including free academic licensing and full AWS integration.

## Credits
The reference set approach to scoring was developed while I was Scientist-in-Residence at the [US Green Building Council (USGBC)](http://www.usgbc.org/), where it forms the core of the new LEED Performance Score.

Development of the theoretical approach of **HiScore** is credited to collaboration with [Ken Judd](http://www.hoover.org/fellows/kenneth-l-judd). The algorithm itself is an extension of the quasi-Kriging technique proposed by Gleb Beliakov in a [2005 paper](http://link.springer.com/article/10.1007/s10543-005-0028-x).

## Contact and Support
If you're using or interested in using **HiScore** to develop scores for a specific domain I'd love to hear from you. Please contact me directly at <aothman@cs.cmu.edu>.