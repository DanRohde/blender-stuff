# Constraints
## Description

### Neighbor Constraints
Allows you to define a list of allowed neighbors for all possible directions (at once).

| **Parameter**                        | **Description**                                                                                                                 |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Direction                            | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                      |
| Neighbor | Neigbors restrict neighbors to a given list of building blocks. If no neighbor is selected, all are permitted.                  |
| No Neighbor allowed                  | prohibits all neighbors                                                                                                         |
| Allow neighbor constraint violations | If no suitable neighbors can be found, all building blocks that also have this paremeter set can be used as possible neighbors. |

### Connector Constraints
You can define a connector name for any direction that match with the connector name of possible neighbors with the same connector name in the opposite direction.

| **Parameter**                  | **Description**                                                                                                                  |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Direction | 26 possible directions and 4 direction groups (faces, corners, edges, any) can be selected                                       |
| Name | The connector name to restrict the possible neighbors. Only neighbors with the same name in the opposite direction can be used. Empty names or unspecified directions allow any neighbor. |

### Geometry Constraints
Edges or faces are used to determine whether two objects can be placed next to each other.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Faces         | Only edges or faces of selected faces will be compared.                    |
| Match Edges   | Use edges for comparison.                                                  |
| Match Faces   | Use faces for comparison.                                                  |
| Tolerance     | Maximum distance between vertices during edge/face vector comparison.      |
| Threshold     | Maximum distance between grid cell face and building block faces or edges. |


### Dimensions Constraints
This enables building blocks that are larger than a cell.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Dimensions | Extension of the building block across multiple cells. |

## Fixed Position Constraints
This allows you to set a fixed starting position within the grid in order to achieve a more predictable result.

| **Parameter** | **Description**                                                            |
|---------------|----------------------------------------------------------------------------|
| Fixed Position | A fixed position within the grid allows for more predictable results.  |

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
