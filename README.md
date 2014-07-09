# HiScore

HiScore is a *scoring engine* that uses *reference sets* to generate *scoring functions* that efficiently transfer knowledge from experts into algorithms.

The expert starts by labeling a set of points with scores, and how those dimensions relate to.

For instance, you may be a network security company that assess threats on two axes. You may come up with the 

It is designed for use by non-mathematical domain experts to create sophisticated scores, and maintain those scores over time.


## Usage


## Why HiScore?

In a traditional approach to scoring, a mathematically adept domain expert

While this approach is quick and intuitive, it ossifies quickly; after a certain point experts stop modifying the score even when they see mis-scored points because fiddling with coefficients begins to produce more errors than it fixes.

In contrast, **HiScore** allows domain experts to fix observed errors quickly: just add the erroneous point (with its correct score) to the reference set, and re-run the scoring engine. The result is a powerful, flexible, maintainable scoring system.

## Limits and Applications

HiScore leverages a powerful underlying algorithm. It runs quickly with hundreds or thousands of points in a reference set and dozens of dimensions.

It is suggested 

## Package Requirements

Numpy, gurobi. Gurobi is available at 

Gurobi is required to solve but not use.

## Credits
The reference set approach to scoring was originally developed while I was Scientist-in-Residence at the [US Green Building Council (USGBC)](http://www.usgbc.org/), where it forms the core of the new LEED Performance Score.

Development of the theoretical approach expressed in HiScore is credited to collaboration with [Ken Judd](http://www.hoover.org/fellows/kenneth-l-judd), with assistance in literature review from [Greg Fasshauer](http://www.math.iit.edu/~fass/). The algorithm itself is a modification of a technique originally proposed by Gleb Beliakov in a [2005 paper](http://link.springer.com/article/10.1007/s10543-005-0028-x). A short white paper describing the technique in mathematical detail is available on the arXiv.

## Need Help?
If you need help developing a score for your particular domain, need a non-free license for HiScore, or want a support contract, please contact me at <aothman@cs.cmu.edu>.