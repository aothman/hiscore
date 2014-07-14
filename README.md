# HiScore

A *scoring function* maps between objects (tuples of numerical attributes) and scores (a single numerical value). Scoring functions can rank objects too; just order by score. **HiScore** is a python library for making scoring functions through *reference sets*, which are sets of objects that get assigned scores.

## Attributes
**HiScore** requires that attributes involved in a score must be **monotone**. This means that a score must always be non-decreasing or non-increasing if the value in each dimension moves in isolation. This is typically a natural restriction as the attributes of an object usually measure something that is either good or bad.

## Example Usage
For instance, you may be a network security company that assess threats on two axes:

1. Your certainty that the threat is real ("Certainty"),
2. The potential risk from the threat. ("Risk")

and you want to develop a scoring function from 0 to 100 that is increasing in certainty and risk.

Both your certainty and risk attributes are in [0,10], and you develop the following reference set that maps objects to the scores you think are appropriate:

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
	
	import hiscore
	reference_set = {(0,0): 0, (10,10): 100, (5,5): 20, (10,8): 90, (8,10): 80, (3,10): 20, (10,2): 15}
	score_function = hiscore.create(reference_set, (1,1), minval=0, maxval=100)

The resulting function interpolates exactly through the reference set:
	
	zip(reference_set.keys(), score_function.calculate(reference_set.keys())
	# Returns [((10, 8), 90.0), ((0, 0), 0.0), ((5, 5), 20.0), ((10, 10), 100.0), ((3, 10), 20.0), ((8, 10), 80.0), ((10, 2), 15.0)]

While producing reasonable estimates for points that are not in the reference set

	np.round(score_function.calculate([(9,9)]))
	# Returns [84.]

And also obeying monotonicity, so that increasing certainty or risk increases the score

	np.round(score_function.calculate([(7,7),(7,8),(7,9),(7,10)]))
	# Returns [49., 58., 62., 68.]
	np.round(score_function.calculate([(7,7),(8,7),(9,7),(10,7)]))
	# Returns [49., 59., 70., 78.]

## API

	create

	calculate

	value_bounds

## Why HiScore?

**HiScore** is designed with three qualities in mind:
+ Ease-of-Use. While **HiScore** can produce mathematically sophisticated scores with complex non-linear relationships between attributes, **HiScore** takes care of all this math internally. It requires only domain expertise, *not* mathematical expertise.
+ Performance. **HiScore** can quickly produce meaningful scores over very large domains with dozens or even hundreds of attributes.
+ Maintainability. **HiScore** is designed to make scoring functions that get better over time.

The traditional approach to scoring looks like this:

1.  A mathematically adept domain expert comes up with a set of descriptive scoring functions. (For instance, a radial function scoring a location's distance to the nearest grocery store, or an exponential  dropoff function scoring time since a credit card applicant's last credit default.)
2. The domain expert determines how to combine those functions.
3. The domain expert checks the resulting score function against a reference set of objects to see if the score of those objects "looks right".
4. The above steps are repeated until the expert is satisfied.

While this approach can be quick and intuitive, it ossifies quickly; after a certain point experts stop modifying the score even when they see mis-scored points because fiddling with coefficients introduces more errors than it fixes.

In contrast, **HiScore** allows domain experts to fix observed errors quickly: just add the erroneous point (with its correct score) to the reference set, and re-run the scoring engine.

## Requirements

In addition to `numpy`, **HiScore** requires the python libraries of the [Gurobi optimizer](http://www.gurobi.com) in order to `hiscore.create` scoring functions. Once created, further calls (e.g., to `calculate`) do not require use of the Gurobi libraries.

While Gurobi is not free software, it offers several attractive licensing options, including free academic licensing and AWS integration.

## Credits
The reference set approach to scoring was originally developed while I was Scientist-in-Residence at the [US Green Building Council (USGBC)](http://www.usgbc.org/), where it forms the core of the new LEED Performance Score.

Development of the theoretical approach of **HiScore** is credited to collaboration with [Ken Judd](http://www.hoover.org/fellows/kenneth-l-judd). The algorithm itself is a practical modification of the sup-inf approach to shape-preserving interpolation proposed by Gleb Beliakov in a [2005 paper](http://link.springer.com/article/10.1007/s10543-005-0028-x).

## Need Help?
If you're looking for help developing a score for your particular domain, I'd love to chat! Contact me directly at <aothman@cs.cmu.edu>.