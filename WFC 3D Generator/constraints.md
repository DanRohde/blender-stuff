# Constraints
## Phases
### Grid Initialization Phase
All these constraints reduce entropy in grid cells:
1. Frequency constraints: frequency == 0 or percentage == 0
2. Probability constraints: weight == 0 or probability == 0
3. Region constraints
4. Noise constraints
5. Grid constraints
6. Region probability constraints: weight == 0 or probability == 0
7. Region frequency constraints: frequency == 0 or percentage == 0

### Post Initialization Phase
1. Fixed position constraints (collapse cells)
2. Distance from position constraints


### Collapse Phase
1. (Region) Probability constraints: influence collapse with weight and probability

### Propagate Phase
1. Symmetry constraints (collapse cells)
2. Frequency constraints
3. Region frequency constraints
4. Distance from object constraints: are influenced by dimensions constraints
5. Dimensions constraints (collapse cells): are influenced by symmetry (flipping)
6. Neighbor constraints
7. Connector constraints
8. Geometry constraints

### Render Phase
1. Noise constraints: replace randomness for transformations (scale, rotation, ...)
2. Transformation constraints
3. Symmetry constraints  
