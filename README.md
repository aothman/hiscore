# HiScore

A *scoring function* maps between objects (tuples of numerical attributes) and scores (a single numerical value). Scoring functions can rank objects too; just order by score. **HiScore** is a python library for making scoring functions through *reference sets*: a set of objects that are assigned scores. By updating and changing the reference set, domain experts can easily create and maintain sophisticated scores.


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

## Attributes
**HiScore** requires that **attributes involved in a score must be monotone**. This means that a score must always be non-decreasing or non-increasing if the value in each dimension moves in isolation. This is typically a natural restriction as the attributes of an object usually measure something that is either good or bad.

## Simple Example Use
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

Observe that it is monotone increasing along both axes and piecewise linear, but also how it picks up on shape features from the reference set, increasing more steeply as certainty and risk both increase.

## More Complex Example

You can also use **HiScore** to make multi-levels scores by creating sub-scores that pass their inputs up a tree. This enables the easy creation of reference sets for scores with dozens of attributes.

Consider a simplified version of the [World Health Organization safety score for water wells](http://www.ncbi.nlm.nih.gov/pubmed/22717748), which depends on two sub-scores:

*	Site Location
	*	Distance to nearest latrine in meters
	*	Distance to other nearest pollutant in meters
*	Platform
	*	Size in square feet
	*	Is it damaged, cracked, or eroding away?

Graphically, our water well function has the following tree shape:

![Demonstration Scoring Tree](http://www.cs.cmu.edu/~aothman/tree_score_demo.png)

We can use **HiScore** by first making scoring functions for the two-subscores:

```python	
location_reference_set = {(0,100): 0, (100,0): 0, (10,10): 50, (10,100): 60, (100, 10): 70, (20,20): 60, (50,50): 85, (100,100): 100}
location_subscore = hiscore.create(location_reference_set, [1,1], minval=0, maxval=100)

platform_reference_set = {(0,1): 0, (0,0): 0, (25,1): 15, (25,0): 80, (50,0): 100, (50,1): 20, (15,1): 5, (20,0): 15}
platform_subscore = hiscore.create(platform_reference_set, [1,-1], minval=0, maxval=100)
```
(Note how the binary attribute of whether the platform is damaged is handled)

We can then produce a final score by combining these two scores. The following score more heavily weights the location subscore:
```python	
well_reference_set = {(0,0): 0, (100,100): 100, (100,0): 80, (0,100): 20, (50,50): 50, (100,50): 95, (50,100): 65, (0,50): 15, (50,0): 35} 
well_score = hiscore.create(well_reference_set, [1,1], minval=0, maxval=100)
```

Now we can calculate a full example score:
```python
latrine_distance = 17.2
other_pollutant_distance = 31.1
loc_score = location_subscore.calculate([(latrine_distance, other_pollutant_distance)])
# loc_score => [55.58]
platform_size = 40.2
is_damaged = True
plat_score = platform_subscore.calculate([(platform_size,int(is_damaged))])
# plat_score => [18.04]
total = well_score.calculate([loc_score+plat_score])
# total => [48.14]
```

## API

Start by creating a `HiScoreEngine` object:

*	create(reference_set_dict, monotone_relationship, minval=None, maxval=None)
	*	reference_set_dict: The reference set, keys are objects (tuples) and values are scores.
	*	monotone_relationship: An iterable with entries that are +/- 1. +1 means the score function should be increasing along that attribute, -1 means the score function should be decreasing.
	*	minval, maxval: Floats, the minimum and maximum values for the function.
	*	Returns a HiScoreEngine object that can be queried for function values.

On that returned object, you can call:

*	calculate(xs)
	*	xs: An iterable of tuples
	*	Returns score function evaluations at each of the tuples

*	value_bounds(object)
	* 	object: A single tuple
	* 	Returns (minimum value, maximum value) based on other entries in the reference set and the initialized minimum and maximum values, if defined.

## Installation and Requirements

To install **HiScore**, just run

```bash
$ pip install hiscore
```

In addition to `numpy`, **HiScore** requires the python libraries of the [Gurobi optimizer](http://www.gurobi.com) in order to `hiscore.create` scoring functions. Once the scoring function is created, further calls (e.g., to `calculate`) do not require use of the Gurobi libraries.

While Gurobi is not free software, it offers several attractive licensing options, including free academic licensing, a free evaluation license, and full AWS integration.

## Credits
Development of the theoretical approach of **HiScore** is credited to a collaboration with [Ken Judd](http://www.hoover.org/fellows/kenneth-l-judd). The algorithm itself is an extension of the quasi-Kriging technique proposed by Gleb Beliakov in a [2005 paper](http://link.springer.com/article/10.1007/s10543-005-0028-x).

## Contact and Support
If you're using or interested in using **HiScore** to develop scores for a specific domain I'd love to hear from you. Please contact me directly at <aothman@cs.cmu.edu>.