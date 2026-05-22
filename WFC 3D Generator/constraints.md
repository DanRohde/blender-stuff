# Constraints
## Neighbor Constraints
Allows you to define a list of allowed neighbors for all possible directions (at once). 

| **Parameter**                        | **Description**                                                                                                                 |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Direction                            | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                      |
| Neighbors | Neighbors restrict neighbors to a given list of building blocks. If no neighbor is selected, all are permitted.                  |
| No Neighbor allowed                  | prohibits all neighbors                                                                                                         |
| Allow neighbor constraint violations | If no suitable neighbors can be found, all building blocks that also have this paremeter set can be used as possible neighbors. |

- More information: [Adjacency Constraints Comparison](#adjacency-constraints-comparison)

## Connector Constraints
You can define a connector name for any direction that match with the connector name of possible neighbors with the same connector name in the opposite direction.

| **Parameter**                  | **Description**                                                                                                                  |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Direction | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                       |
| Name | The connector name to restrict the possible neighbors. Only neighbors with the same name in the opposite direction can be used. Empty names or unspecified directions allow any neighbor. |

- More information: [Adjacency Constraints Comparison](#adjacency-constraints-comparison)

## Connector Exclusion Constraints
You can define a list of prohibited connector names for a specific direction. This works with connector constraints and multiple connector constraints.

| **Parameter**                  | **Description**                                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Direction | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                      |
| Name | The connector name to restrict the possible neighbors. |

- More information: [Adjacency Constraints Comparison](#adjacency-constraints-comparison)

## Multiple Connector Constraints
You can define a list of allowed connector names for a specific direction. It's possible to combine connector constraints with multiple connector constraints.

| **Parameter**                  | **Description**                                                                            |
|--------------------------------|--------------------------------------------------------------------------------------------|
| Direction | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected |
| Name | The connector name to restrict the possible neighbors. Only neighbors with the same name in the opposite direction can be used. Empty names or unspecified directions allow any neighbor.                                    |

- More information: [Adjacency Constraints Comparison](#adjacency-constraints-comparison)


## Geometry Constraints
Edges or faces are used to determine whether two objects can be placed next to each other.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Faces         | Only edges or faces of selected faces will be compared.                    |
| Match Edges   | Use edges for comparison.                                                  |
| Match Faces   | Use faces for comparison.                                                  |
| Tolerance     | Maximum distance between vertices during edge/face vector comparison.      |
| Threshold     | Maximum distance between grid cell face and building block faces or edges. |

- More information: [Adjacency Constraints Comparison](#adjacency-constraints-comparison)

## Empty Neighbor Constraints
These constraints prohibit empty neighbors.

| **Parameter** | **Description**                                                    |
|---------------|--------------------------------------------------------------------|
| Empty Neighbor | Prohibits empty immediate neighbors in the selected directions. |
| Empty Any Neighbor | Generally prohibits empty neighbors in the selected directions.    |

## Dimensions Constraints
This enables building blocks that are larger than a cell.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Dimensions | Extension of the building block across multiple cells. |

## Fixed Position Constraints
This allows you to set a fixed starting position within the grid in order to achieve a more predictable result.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Fixed Position | A fixed position within the grid allows for more predictable results. ([more](#positions-and-regions)) |

## Grid Constraints
Allows you to specify where an object may be located within the grid.

| **Parameter** | **Description**                                                                                                           |
|---------------|---------------------------------------------------------------------------------------------------------------------------|
| Corners       | Only selected grid corners may be occupied by the building block. If nothing is selected, all grid corners are permitted. |
| Edges         | Only selected grid edges may be occupied by the building block. If nothing is selected, all grid edges are permitted.     |
| Faces         | Only selected grid faces may be occupied by the building block. If nothing is selected, all grid faces are permitted.     |
| Inside | The inner area of the grid can be prohibited for the building block.                                                      |

## Region Constraints
Allows you to specify where an object may be located within the grid.

| **Parameter** | **Description**                                                                                                                                    |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| min | Smallest position in the grid for the permitted region. ```(-1,-1,-1) => (0,0,0)```                                                                |
| max | Largest position in the grid for the permitted region. ```(-1,-1,-1) => (max. X, max. Y, max. Z)```                                                   |
| Quadrant | The grid is divided into eight quadrants and only selected quadrants can be occupied by the building block: fbl, fbr, ftl, ftr, bbl, bbr, btl, btr |
| Level | Only selected levels (floors) can be occupied by the building block.                                                                               |

## Distance Constraints
Rules that restrict the placement of building blocks based on their distance from a specific point or another building block.

| **Parameter** | **Description**                                                             |
|---------------|-----------------------------------------------------------------------------|
| Distance | The distance to a position or object in the grid.                           |
| From | Defines whether the distance from a position or from a specific building block must be maintained. |
| Object | A link to the building block                                                |
| Position | This defines the position within the grid. ([more](#positions-and-regions)) |
| Type | This sets the distance type.                                                |                                                                                                                                                                         |

## Frequency Constraints
Define how often the same object or any other object may occur in the immediate vicinity or on one of the 3 axes XYZ.

| **Parameter** | **Description**                                                                                                     |
|---------------|---------------------------------------------------------------------------------------------------------------------|
| *Same Object* | In these constraints, settings for the frequency of a building block itself can be configured.                      |
| Grid          | Frequency of the building block itself within the Grid.                                                             |
| Grid %        | Frequency as a percentage of the building block itself within the Grid.                                            |
| Neighbor      | Frequency in the direct neighborhood (26 directions) of the building block itself.                                 |
| Face          | Frequency in all six face directions of the building block itself.                                                 |
| Corner        | Frequency at all eight corners of the building block itself.                                                       |
| Edge          | Frequency at all twelve edges of the building block itself.                                                         |
| Axes          | Frequency along the three axes (XYZ) of the building block itself.                                                 |
| Direction     | Direction for the direction frequency of the selected bulding block.                 |
| Direction Frequency | Frequency in the selected direction of the selected building block. |  
| *Any Object*  | In these constraints, the frequency of all building blocks from the Source Collection can be set.                   |
| Any Neighbor  | Frequency of building blocks in the direct neighborhood (26 directions).                                           |
| Any Face      | Frequency of building blocks in the six face directions.                                                           |
| Any Corner    | Frequency of building blocks at the eight corners.                                                                |
| Any Edge      | Frequency of building blocks at the twelve edges.                                                                  |
| Any Axes      | Frequency of building blocks along the three axes (XYZ).                                                           |
| Direction     | Direction for the direction frequency of the selected bulding block.                 |
| Direction Frequency | Frequency in the selected direction of the selected building block. |  

## Region Frequency Constraints
Define how often the same object may occur in a specific region.

| **Parameter** | **Description**                                                                     |
|---------------|-------------------------------------------------------------------------------------|
| Name          | Optional name of the region for easier identification of the region.                |
| min           | Lower point of the region as a vector ([more](#positions-and-regions)).             |
| max           | Upper point of the region as a vector ([more](#positions-and-regions)).                                             |
| Frequency     | Frequency of the building block itself within the region (min-max).                 |
| Frequency %   | Frequency as a percentage of the building block itself within the region (min-max). |

## Object Frequency Constraints
Define how often a defined object may occur in the immediate vicinity, on one of the 3 axes, or in a specific direction.

| **Parameter** | **Description**                                                                      |
|---------------|--------------------------------------------------------------------------------------|
| Object        | Building block (an empty building block means any neighbor)                          | 
| Neighbor      | Frequency in the direct neighborhood (26 directions) of the selected building block. |
| Face          | Frequency in all six face directions of the selected building block.                 |
| Corner        | Frequency at all eight corners of the selected building block.                       |
| Edge          | Frequency at all twelve edges of the selected building block.                        |
| Axes          | Frequency along the three axes (XYZ) of the selected building block.                 |
| Direction     | Direction for the direction frequency of the selected bulding block.                 |
| Direction Frequency | Frequency in the selected direction of the selected building block. |  

## Symmetry Constraints
These constraints allow mirror-symmetric and/or rotation-symmetric objects to be generated.

| **Parameter**                  | **Description**                                                                                                                                                                                                 |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Mirror Symmetry*              | Settings for mirror symmetry can be configured here.                                                                                                                                                           |
| Axes                           | The selected axes determine the mirroring behavior. If multiple axes are selected, all possible mirror combinations (up to 8) are automatically generated.                                                              |
| Partner                        | Depending on the selected axis, optional building blocks can be specified to serve as mirror-symmetric counterparts instead of the building block itself.                                                               |
| Flip Mirror Partner            | Instead of a mirror partner, the object itself can be mirrored (flipped).                                                                                                                                      |
| Transfer Random Transformation | If random transformations are defined, the same transformations can be transferred to the mirror partners.                                                                                                      |
| *Rotational Symmetry*          | Settings for rotational symmetry can be configured here.                                                                                                                                                       |
| Axis                           | A vector is defined here to specify the rotation point.                                                                                                                                                         |
| Number                         | This number serves as a divisor for the 360° rotation. For example, a value of 4 generates 4 rotations of 90 degrees each.                                                                                     |

## Probability Constraints
These constraints increase or decrease the probability of an object being selected at random.

| **Parameter**                  | **Description**                                                                                                                                                                                                 |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Probability                    | The probability with which a building block should be selected from all possible building block options.                                                                                                       |
| Weight                         | A weight greater than 1 increases the probability of being selected for a cell, depending on the available options.                                                                                           |
| Automatic weight determination | The weight is automatically determined based on the number of constraints: The more constraints a building block has, the lower its weight.                                                                    |

## Region Probability Constraints 
These constraints increase or decrease the probability of an object being selected at random in a specific region.

| **Parameter** | **Description**                                                                                                                            |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Name | Optional name for easier identification of the region.                                                                                     |
| min | Lowest point of the region as a vector ([more](#positions-and-regions)).                                                                   |
| max | Highest point of the region as a vector ([more](#positions-and-regions)).                                                                                                  |
| Probability | Probability with which a building block is chosen from the possible options in this region.                                                |
| Weight | A weight greater than 1 increases the probability of a building block being chosen for a cell in the region depending on possible options. |

## Transformations
These are not really restrictions. This allows you to randomize the position, size, rotation, and flipping of building blocks.

| **Parameter**      | **Description**                                                                                                                     |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| Translation Offset | This allows a building block to be randomly shifted in its position depending on its position in the grid.                          |
| *Rotation*         | With these parameters, a building block can be randomly rotated as desired.                                                         |
| *Scale*            | These parameters allow random scaling of building blocks.                                                                       |
| *Flipping*         | Here, for each axis, the probability can be set with which a building block is randomly mirrored (flipped).                         |


## Noise Constraints 
Noise constraints either influence the probability of an object occurring or replace random values in transformations with noise values.

| **Parameter**                       | **Description**                                                                                                                                                         |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Noise on probability of occurance* | Instead of randomly selecting an object, the selection of objects can be influenced by a selectable noise function.                                                     |
| Function                            | Noise function                                                                                                                                                          |
| Noise Basis                         | Noise function to influence the appearance of a building block.                                                                                                         |
| Threshold                           | Threshold that must be exceeded by the noise function for an object to be allowed to appear in a specific cell of the grid.                                             |
| Scale                               | Scaling factor for the position to calculate the noise function value.                                                                                                  |
| H                                   | The fractal dimension of the roughest areas or the fractal increment parameter.                                                                                         |
| Lacunarity                          | The gap between successive frequencies.                                                                                                                                 |
| Octaves                             | The number of different noise frequencies used.                                                                                                                                                                        |
| Offset                              | The height of the terrain above ‘sea level’.                                                                                                                                                                                                                       |
| Gain                                | Scaling applied to the values.                                                                                                                                                                                                                                                                   |
| Randomize the starting position     | When enabled, a random value is multiplied with the position of the building block in the grid. This allows generating different results when changing the random seed. |

| **Parameter**                       | **Description**                                                                                                                                                         |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Noise on transformations*          | This allows replacing the random value function for a transformation with a noise function.                                                                             |
| Function                            | Noise function                                                                                                                                                          |
| Basis                               | Noise basis to influence transformations of a building block.                                                                                                           |
| Scale                               | Scaling factor for the position to calculate the noise function value.                                                                                                  |
| H                                   | The fractal dimension of the roughest areas or the fractal increment parameter.                                                                                         |
| Lacunarity                          | The gap between successive frequencies.                                                                                                                                 |
| Octaves                             | The number of different noise frequencies used.                                                                                                                                                                        |
| Offset                              | The height of the terrain above ‘sea level’.                                                                                                                                                                                                                       |
| Gain                                | Scaling applied to the values.                                                                                                                                                                                                                                                                   |

| **Parameter**                       | **Description**                                                                                                                                                         |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Randomize the starting position     | When enabled, a random value is multiplied with the position of the building block in the grid. This allows generating different results when changing the random seed. |


# Positions and Regions
| **Vector Values (X,Y,Z)**         | **Used Vector Values (X,Y,Z)**                  | **Description**                                                          |
|-----------------------------------|-------------------------------------------------|--------------------------------------------------------------------------|
| ```0 <= [X\|Y\|Z] < [grid size]``` | ```new [X\|Y\|Z] = old [X\|Y\|Z]```             | The vector values remain unchanged if they are within the grid.          |
| ```[X\|Y\|Z] < 0```               | ```new [X\|Y\|Z] = [grid size]-1 + [X\|Y\|Z]``` | Negative vector values allow specifications relative to the grid size.   |
| ```[X\|Y\|Z] >= [grid size]```    | ```new [X\|Y\|Z] = [grid size]-1```             | Vector values that are too large are set to the maximum permitted value. |
| ```[X\|Y\|Z] < -[grid size]```    | ```new [X\|Y\|Z] = 0```                         | Negative vector values that are too small are set to 0.                  |

Challenge:
- When changing the grid size, regions or positions may need to be corrected.

# Adjacency Constraints Comparison
| *Tasks*                                          | *Neighbor*     | *(Multiple) Connector* | *Geometry*  |
|--------------------------------------------------|----------------|------------------------|-------------|
| Implementation                                   | easy  | concept required       | very easy   |  
| Adding, deleting, renaming building blocks       | time-consuming | no problem             | no problem  | 
| Performance with large number of building blocks | fast | very fast              | (very) slow |

Recommendation: use (multiple) connector constraints

## Algorithm Phases
### Grid Initialization Phase
All these constraints reduce entropy in grid cells:
1. Frequency constraints: frequency == 0 or percentage == 0
2. Probability constraints: weight == 0 or probability == 0
3. Region constraints
4. Grid constraints
5. Region probability constraints: weight == 0 or probability == 0
6. Region frequency constraints: frequency == 0 or percentage == 0
7. Noise constraints

### Post Initialization Phase
1. Fixed position constraints (collapse cells)
2. Distance from position constraints


### Collapse Phase
1. Empty Neighbor Constraints
2. Dimensions Constraints
3. (Region) Probability constraints: influence collapse with weight and probability

### Propagate Phase
1. Symmetry constraints (collapse cells)
2. (Object) Frequency constraints
3. Region frequency constraints
4. Distance from object constraints: are influenced by dimensions constraints
5. Dimensions constraints (collapse cells): are influenced by symmetry (flipping)
6. Neighbor constraints
7. Connector constraints
8. Geometry constraints

### Post Generation Phase
1. Empty Neighbor Constraints

### Render Phase
1. Noise constraints: replace randomness for transformations (scale, rotation, ...)
2. Transformation constraints
3. Symmetry constraints  
