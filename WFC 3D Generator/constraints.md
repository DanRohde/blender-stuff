# Constraints
## Neighbor Constraints
Allows you to define a list of allowed neighbors for all possible directions (at once).

| **Parameter**                        | **Description**                                                                                                                 |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Direction                            | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                      |
| Neighbor | Neigbors restrict neighbors to a given list of building blocks. If no neighbor is selected, all are permitted.                  |
| No Neighbor allowed                  | prohibits all neighbors                                                                                                         |
| Allow neighbor constraint violations | If no suitable neighbors can be found, all building blocks that also have this paremeter set can be used as possible neighbors. |

## Connector Constraints
You can define a connector name for any direction that match with the connector name of possible neighbors with the same connector name in the opposite direction.

| **Parameter**                  | **Description**                                                                                                                  |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Direction | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                       |
| Name | The connector name to restrict the possible neighbors. Only neighbors with the same name in the opposite direction can be used. Empty names or unspecified directions allow any neighbor. |

## Geometry Constraints
Edges or faces are used to determine whether two objects can be placed next to each other.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Faces         | Only edges or faces of selected faces will be compared.                    |
| Match Edges   | Use edges for comparison.                                                  |
| Match Faces   | Use faces for comparison.                                                  |
| Tolerance     | Maximum distance between vertices during edge/face vector comparison.      |
| Threshold     | Maximum distance between grid cell face and building block faces or edges. |

## Dimensions Constraints
This enables building blocks that are larger than a cell.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Dimensions | Extension of the building block across multiple cells. |

## Fixed Position Constraints
This allows you to set a fixed starting position within the grid in order to achieve a more predictable result.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Fixed Position | A fixed position within the grid allows for more predictable results.  |

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

| **Parameter** | **Description**                                                                                                                                   |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| min | Smallest position in the grid for the permitted region.                                                                                           |
| max | Largest position in the grid for the permitted region.                                                                                            |
| Quadrant | The grid is divided into eight quadrants and only selected quadrants can be occupied by the building block: fbl, fbr, ftl, ftr, bbl, bbr, btl, btr |
| Level | Only selected levels (floors) can be occupied by the building block.                                                                              |

## Distance Constraints
Rules that restrict the placement of building blocks based on their distance from a specific point or another building block.

| **Parameter** | **Description**                                                                                                                                                                                       |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Distance | The distance to a position or object in the grid.                                                                                                                                                     |
| From | Defines whether the distance from a position or from a specific building block must be maintained.                                                                                                    |
| Object | A link to the building block                                                                                                                                                                          |
| Position | This defines the position within the grid. Negative values are added to the maximum grid size values. Values greater than the corresponding grid size values are set to the maximum permitted values. |
| Type | This sets the distance type. |                                                                                                                                                                         |

## Frequency Constraints
Define how often the same object or any other object may occur in the immediate vicinity or on one of the 3 axes XYZ.

| **Parameter** | **Description**                                                                                                                                    |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| *Same Object* ||
| Grid          || 
| Grid %        ||
| Neighbor      ||
| Face          ||          
| Grid          ||          
| Edge          ||
| Axes          ||
| *Any Object*  ||
| Any Neighbor  ||
| Any Face      ||
| Any Corner    ||
| Any Edge      ||
| Any Axes      ||


## Region Frequency Constraints
Define how often the same object may occur in a specific region.

| **Parameter** | **Description**                                                                                                                                    |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Name          ||
| min           ||
| max           ||
| Frequency     ||
| Frequency %   ||


## Symmetry Constraints
These constraints allow mirror-symmetric and/or rotation-symmetric objects to be generated.

| **Parameter**                  | **Description**                                                                                                                                    |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| *Mirror Symmetry*              |
| Axes                           ||
| Partner                        ||
| Flip Mirror Partner            ||
| Transfer Random Transformation ||
| *Rotational Symmetry*          ||
| Axis                           ||
| Number                         ||

## Probability Constraints
These constraints increase or decrease the probability of an object being selected at random.

| **Parameter**                  | **Description**                                                                                                                                    |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Probability                    ||
| Weight                         ||
| Automatic weight determination ||

## Region Probability Constraints 
These constraints increase or decrease the probability of an object being selected at random in a specific region.

| **Parameter** | **Description**                                                                                                                                    |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Name ||
| min ||
| max ||
| Probability ||
| Weight ||


## Transformations
These are not really restrictions. This allows you to randomize the position, size, rotation, and flipping of building blocks.

| **Parameter**      | **Description**                                                                                                                                    |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Translation Offset ||
| *Rotation*         ||
| *Scale*            ||
| *Flipping*         ||


## Noise Constraints 
Noise constraints either influence the probability of an object occurring or replace random values in transformations with noise values.

| **Parameter**                       | **Description**                                                                                                                                    |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| *Noise on probability of occurance* ||
| Noise Basis                         ||
| Threshold                           ||
| Scale                               ||
| Noise on transformations            ||
| Noise Basis                         ||
| Scale                               ||
| Randomize the starting position     ||



## Algorithm Phases
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
