# HiScore

**HiScore** is a python library for making *scoring functions*, which map objects (vectors of numerical attributes) to scores (a single numerical value). 

Scores are a way for domain experts to communicate the quality of a complex, multi-faceted object to a broader audience. Scores are ubiquitous; everything from [NFL Quarterbacks](http://en.wikipedia.org/wiki/Passer_rating) to the [walkability of neighborhoods](https://www.walkscore.com/) has a score.

**HiScore** provides a new way for domain experts to quickly create and improve intuitive scoring functions: by using *reference sets*, a set of representative objects that are assigned scores.

## Demonstration

We'll use a highly simplified version of the [World Health Organization safety score for water wells](http://www.ncbi.nlm.nih.gov/pubmed/22717748) to show how to use **HiScore**.

### Setup and Reference Set Creation

Let's start with a water well safety score based on only two attributes:

1. The distance from the nearest latrine, in meters. ("Distance")
2. The size of the water well platform, in square feet. ("Size")

Observe that score should be *increasing* in both of these attributes (e.g., for wells of a fixed size, the score does not decrease as the well moves farther from the nearest latrine). **HiScore requires scores to always be increasing or decreasing in each attribute**. (This is typically not restrictive, as attributes usually measure something that is either good or bad.) 

To quickly create an intelligent score, you can start by determining, low, middle, and high values for each attribute and then labeling all the combinations of these values. (Of course, you can label other objects as well!) For our water well score, distance could have a low value of 0m, a middle value of 10m, and a high value of 50m, while size could have a low value of 1 sq.ft., a middle value of 25 sq.ft., and a high value of 100 sq.ft. labeling all combinations of these values could yield the following reference set:

	Distance | Size | Score
	--------- | ---- | -----
	0  | 1  | 0
	0 | 25 | 5
	0  | 100  | 10
	10 | 1  | 20
	10  | 25 | 50
	10 | 100 | 60
	50 | 1  | 65
	50  | 25 | 90
	50 | 100 | 100


### Creating, Improving, and Querying the Scoring Function

We can generate a scoring function by calling `hiscore.create` with this reference set:

```python	
import hiscore
# The objects in the reference set are tuples so they can be hashed into a dict
reference_set = {(0,1): 0, (0,25): 5, (0,100): 10, (10,1): 20, (10,25): 50, (10,100): 60, (50,1): 65, (50,25): 90, (50,100): 100}
# [1,1] -> increasing in both attributes
score_function = hiscore.create(reference_set, [1,1], minval=0, maxval=100)
```

The resulting scoring function interpolates exactly through the reference set:

```python	
zip(reference_set.keys(), score_function.calculate(reference_set.keys()))
# Returns [((0, 1), 0.0), ((10, 100), 60.0), ((10, 1), 20.0), ((0, 100), 10.0), ((0, 25), 5.0), ((50, 25), 90.0), ((50, 1), 65.0), ((50, 100), 100.0), ((10, 25), 50.0)]
```

While producing reasonable estimates for points that are not in the reference set

```python
import numpy as np
np.round(score_function.calculate([(15,36)]))
# Returns [56.]
```

And also obeying monotonicity, so that increasing distance or size increases the score

```python
np.round(score_function.calculate([(10,5),(10,10),(10,20),(10,35)]))
# Returns [ 25.,  31.,  44.,  51.]
np.round(score_function.calculate([(5,10),(10,10),(20,10),(50,10)]))
# Returns [ 15.,  31.,  42.,  74.]
```

One of the strengths of **HiScore** is that it is easy to fix mis-scored points. Say, for instance, we were unhappy with a well with distance 15 and size 36 scoring a 56. Say we think it should score a 60 instead. We can add that to the reference set and re-create the scoring function.

```python
reference_set[(15,36)] = 60
score_function = hiscore.create(reference_set, [1,1], minval=0, maxval=100)
score_function.calculate([(15,36)])
# Returns [60.]
```

Here's a three-dimensional figure of the scoring function:

![Demonstration Score Function](http://www.cs.cmu.edu/~aothman/score_function_demo_new.png)

Observe that it is monotone increasing along both axes and piecewise linear, but also how it picks up on shape features from the reference set, increasing more steeply with Distance as opposed to Size.

### A More Complex Score

Scoring all low, middle, and high attribute combinations can result in having to score an exponential number of objects in a reference set as the number of attributes increases. Instead, you can use **HiScore** to create multi-level trees with sub-scores that percolate their values upwards. This enables the easy creation and control of scores with dozens of attributes.

To be concrete, let's extend our safety score for water wells to depend on two sub-scores:

*	Site Location
	*	Distance to nearest latrine in meters
	*	Distance to other nearest pollutant in meters
*	Platform
	*	Size in square feet
	*	Is it damaged, cracked, or eroding away?

Graphically, our water well scoring function will have the following tree shape:

![Demonstration Scoring Tree](http://www.cs.cmu.edu/~aothman/tree_score_demo.png)

We can use **HiScore** by first making scoring functions for the two-subscores, again using the low-middle-high system:

```python
# Location attributes: distance to latrine (higher=better), distance to other pollutant (higher=better)	
location_reference_set = {(0,0): 0, (10,0): 5, (50,0): 10, (0,25): 0, (10,25): 50, (50,25): 75, (0,100): 5, (10,100): 70, (50,100): 100}
location_subscore = hiscore.create(location_reference_set, [1,1], minval=0, maxval=100)

# Platform attributes: size in SF (higher=better), damaged (1=true=damaged=bad, 0=false=undamaged=good)
platform_reference_set = {(1,1): 0, (1,0): 20, (25,1): 5, (25,0): 60, (100,0): 100, (100,1): 30}
platform_subscore = hiscore.create(platform_reference_set, [1,-1], minval=0, maxval=100)
```
(Note how the binary attribute of whether the platform is damaged is handled)

We can then produce a final score by combining these two scores. The following score more heavily weights the location subscore:
```python
# Well attributes: location subscore (higher=better), platform subscore (higher=better)
well_reference_set = {(0,0): 0, (100,100): 100, (100,0): 80, (0,100): 20, (50,50): 50, (100,50): 95, (50,100): 65, (0,50): 15, (50,0): 35} 
well_score = hiscore.create(well_reference_set, [1,1], minval=0, maxval=100)
```

Now we can calculate a full example score. For instance:
```python
latrine_distance = 28.6
other_pollutant_distance = 39.0
loc_score = location_subscore.calculate([(latrine_distance, other_pollutant_distance)])
# loc_score => [59.95]
platform_size = 40.2
is_damaged = True
plat_score = platform_subscore.calculate([(platform_size,int(is_damaged))])
# plat_score => [10.97]
total = np.round(well_score.calculate([loc_score+plat_score]))
# total => [47.]
```

## API

Start by creating a `HiScoreEngine`:

*	create(reference_set_dict, monotone_relationship, minval=None, maxval=None)
	*	reference_set_dict: The reference set, keys are objects (e.g., a list of attributes) and values are scores.
	*	monotone_relationship: An iterable with entries that are +/- 1. +1 means the score function should be increasing along that attribute, -1 means the score function should be decreasing.
	*	minval, maxval: Floats, the minimum and maximum values for the function.
	*	*Returns a HiScoreEngine object that can be queried for function values.*

On that `HiScoreEngine`, you can call:

*	calculate(xs)
	*	xs: An iterable of objects.
	*	*Returns a list of score function evaluations at each of the tuples.*

*	value_bounds(object)
	* 	object: A single object.
	* 	*Returns a two-element tuple (minimum value, maximum value) based on other entries in the reference set and the initialized minimum and maximum values, if defined.*

## Installation and Requirements

To install **HiScore**, just run

```bash
$ pip install hiscore
```

In addition to `numpy`, **HiScore** requires [CVXPY](http://www.cvxpy.org/en/latest/).

## Credits and References
Development of the theoretical approach of **HiScore** is credited to a collaboration with [Ken Judd](http://www.hoover.org/fellows/kenneth-l-judd).

The algorithm itself is an extension of the quasi-Kriging technique proposed by Gleb Beliakov in a [2005 paper](http://link.springer.com/article/10.1007/s10543-005-0028-x). I explored a different algorithm for reference-set-based scoring in a [2014 AAAI paper](http://www.cs.cmu.edu/~aothman/splines.pdf).

## Contact and Support
If you're using or interested in using **HiScore** to develop scores for a specific domain I'd love to hear from you. Please contact me directly at <aothman@cs.cmu.edu>.
