The WFC 3D Generator add-on generates a new object from a collection of objects using a simple implementation of the Wave Function Collapse algorithm with constraints.

Each object in the source collection can use custom properties to define the permitted neighbors. The generator randomly combines these objects in a 3D grid while adhering to the neighbor constraints. The allowed position in the grid can be defined by grid constraints. 

## Quick Start Guide
1. Install and enable the WFC 3D Generator add-on
2. Create a source collection with some objects
3. Define constraints: 
    1. open 3D Viewport: Press 'N' > WFC 3D Edit > WFC 3D Constraints Editor
    2. select a source collection
    3. add some constraints to objects 
4. Create a new object:
    1. open 3D Viewport: WFC 3D Gen > WFC 3D Generator
    2. Press "Generate WFC 3D Model"

Some examples can be found on [GitHub](https://github.com/DanRohde/blender-stuff/tree/main/Examples).

## Features
The WFC 3D Generator Extension implements a very simple variant of the [Wave Function Collapse algorithm](https://en.wikipedia.org/wiki/Model_synthesis). 
With cleverly chosen building blocks and constraints, any object can be created on a random basis, 
but taking the constraints into account, e.g., works of art, buildings, cities, game maps, and even galaxies.

* Simple generator interface WFC 3D Gen:
  * It allows you to watch the WFC algorithm at work thanks to a render delay. Rendering can be paused or canceled at any time.
  * The cherry-picking function automatically starts generation after an adjustable delay to generate the desired result more quickly.
  * In addition to the grid size, you can set the cell size and an offset between even and odd rows, columns, and files.
* Convenient constraint editor WFC 3D Edit:
  * All currently supported constraints can be easily assigned to objects there.
  * Offers the option of defining constraints for one or more objects simultaneously (object constraints) or for the entire source collection (collection defaults).
  * Allows you to select objects in the 3D viewport or outliner with manual or automatic transfer of the selected objects
  * Auto-Save: every constraint change is automatically saved as a custom property when enabled
* WFC 3D Validator:
  * Checks the source collection with building blocks to see whether transformations (scale, rotate) 
    have been applied and whether neighbors exist in neighbor constraints.

## Constraints Overview
* Adjacency Constraints: 
  * Neighbor Constraints: define a list of allowed neighbors for all possible directions (at once);
    Advantage: easy to define, Disadvantage: difficult to expand
  * Connector Constraints: define a connector name for any direction that match with the connector name of possible neighbors with the same connector name in the opposite direction;
    Advantage: building blocks are easily expandable, Disadvantage: not always easy to define
* Grid and Region Constraints:
  * Allows you to specify where an object may be located within the grid.
* Probability Constraints:
  * These constraints increase or decrease the probability of an object being selected at random.
* Frequency Constraints:
  * Define how often the same object or any other object may occur in the immediate vicinity or on one of the 3 axes XYZ.
* Symmetry Constraints:
  * These constraints allow mirror-symmetric and/or rotation-symmetric objects to be generated.
  * It is possible to transfer random transformations to mirror partners, flip mirror partners accordingly,
    or define other building blocks as mirror partners.
* Transformations:
  * These are not really restrictions. This allows you to randomize the position, size, rotation, and flipping of building blocks.

## How the WFC 3D Generator algorithm works
1. **Initializes** each cell of the grid with a list of permitted building blocks. Grid and region constraints are taken into account.
2. Find the cell with the **lowest entropy**, in this case, the cell with the smallest list of building blocks. If there is more than one, the first or a random one is selected.
3. **Collapse** the cell: Select a random object from the list of building blocks. Probability constraints and symmetry constraints are propagated and matching cells are collapsed.
4. **Propagate** the constraints of the randomly selected building block to the neighborhood and the entire grid. Frequency constraints and adjacency constraints are applied.
5. **Repeat** steps 2-4 until all cells are collapsed.
6. **Render** the grid in the order in which cells are collapsed. Transformations are applied.


## Limitations and Known Issues
* For neighbor restrictions to take effect, there must be more than one object in the source collection.
* Region constraints don't work with all symmetry constraint variants

## Statistics: Constraint Properties per Object
* Neighbor constraints: 28
* Grid constraints: 4
* Region constraints: 3
* Probability constraints: 3
* Transformations: 12
* Frequency constraints: 11
* Symmetry constraints: 19
* Connector constraints: 27


* **Sum: 107**

## Neighbor Constraints
* Allows neighbors to be restrict in all directions: face neighbors, edge neighbors (`wfc_en_...`), corner neighbors (`wfc_cn_...`)
* Used custom properties: face neighbors: `wfc_[left|right|front|back|top|bottom]`, edge neighbors: `wfc_en_[fl|fr|ft|fb|bl|br|bt|bb|lt|lb|rt|rb]`,
  corner neighbors: `wfc_cn_[fbl|fbr|ftl|ftr|bbl|bbr|btl|btr]`, `wfc_allow_neighbor_constraint_violations`, `wfc_any`
* Allowed property values:
    * empty string - allows all neighbors
    * comma separated list of object names - permitted neighbor(s)
    * "None" - disallows all neighbors


## Grid Constraints

**Corner constraints:**
* Used custom property: `wfc_corners`
* Allowed property values:
    * empty string - allows all corners
    * "-" - forbids all corners
    * comma separated list of allowed corners: `fbl,fbr,ftl,ftr,bbl,bbr,btl,btr` ("f" - front, "b" - back or bottom in second position, "t" - top, "l" - left, "r" - right) 


**Edge constraints:**
* Used custom property: `wfc_edges`
* Allowed property values:
    * empty string - allows all edges
    * "-" - forbids all edges
    * comma separated list of permitted edges: `fb,fl,ft,fr,bb,bl,bt,br,lb,lt,rb,rt` ("f" - front, "b" - back or bottom in second position, "t" - top, "l" - left, "r" - right)

	
**Face constraints:**
* Used custom property: `wfc_faces`
* Allowed property values:
    * empty string - allows all faces
    * "-" - forbids all faces
    * comma separated list of permitted faces: ``front,back,top,bottom,left,right``


**Inside constraints:**
* Use custom property:	`wfc_inside`
* Allowed property values:
    * empty string - allows the object to stay inside the grid
    * "-" - forbids to stay inside

## Region Constraints
* Used custom properties: `wfc_region_min,wfc_region_max,wfc_region_quadrant`
* Allowed property values:
    * wfc_region_[min|max]: integer vector 
    * wfc_region_quadrant: boolean vector of size 8 (fbl,fbr,ftl,ftr,bbl,bbr,btl,btr)
	
## Probability Constraints
* Used custom properties: `wfc_weight,wfc_probability,wfc_auto_weight`
* Allowed property values:
    * wfc_probability: float value between 0 and 1
    * wfc_weight: empty string - weight of 1, 0 - object will not be used, 1..n - increases the chance of being chosen by a factor of n
    * wfc_auto_weight: boolean enables/disables automatic weight determination


## Transformations
* Used custom properties: `wfc_translation_min,wfc_translation_max,wfc_translation_steps,wfc_rotation_min,wfc_rotation_max,wfc_rotation_steps,wfc_scale_min,wfc_scale_max,wfc_scale_steps,wfc_scale_uni,wfc_scale_type,wfc_flipping`
* Allowed property values:
    * wfc_translation_min,wfc_translation_max,wfc_translation_steps: a float vector (x,y,z)
    * wfc_rotation_min,wfc_rotation_max,wfc_rotation_steps: a float vector  (x,y,z)
    * wfc_scale_type: integer value: 0 - no scaling, 1 - uniform scaling, 2 - non-uniform scaling
    * wfc_scale_uni: a float vector (min,max,steps) for uniform scaling
    * wfc_scale_min,wfc_scale_max,wfc_scale_steps: a float vector (x,y,z) for non-uniform scaling
    * wfc_flipping: a float vector with probabilities for flipping on a specific axis
    
   
## Frequency Constraints
* Used custom properties: `wfc_freq_[any_]neighbor[_face|_edge|_corner],wfc_freq_grid,wfc_freq_[any_]axes`
* Allowed property values:
   * wfc_grid, wfc_freq_[any_]neighbor[_face|_edge|_corner]: an integer
   * wfc_[_any]_axes: an integer vector


## Symmetry Constraints
* Used custom properties: `wfc_sym_mirror,wfc_sym_rotate_axis,wfc_sym_rotate_n,wfc_sym_mirror_axes_[x|y|z|xy|xz|yz|xyz],wfc_sym_mirror_flip_[x|y|z|xy|xz|yz|xyz],wfc_sym_mirror_flip_transl, wfc_sym_mirror_trans`
* Allowed property values: 
    * wfc_sym_mirror: a vector of booleans or integers
    * wfc_sym_mirror_axes_[x|y|z|xy|xz|yz|xyz]: a pointer to an mirror partner object
    * wfc_sym_mirror_flip_[x|y|z|xy|xz|yz|xyz]: a boolean value that allows the mirror partners to be flipped
    * wfc_sym_mirror_flip_transl: a boolean value that allows the mirror partners to flip the translation transformation
    * wfc_sym_mirror_trans: a boolean that allows a transfer of random transformations to mirror partners
    * wfc_sym_rotate_axis: a float vector
    * wfc_sym_rotate_n: an integer (number of rotations: n=4 => 90° rotation)
    

## Connector Constraints
* Used custom properties: `wfc_conn_[any|front|back|left|right|top|bottom|cn_(fbl|fbr|ftl|ftr|bbl|bbr|btl|btr)|en_(fl|fr|ft|fb|bl|br|bt|bb|lt|lb|rt|rb)]`
* Allowed property value: string with a connector name

## Upcoming Features
* dimension constraints: allows a building block to cover more than one grid cell (XYZ span and alignment)
* improved translations: adding flipping
* add noise to the grid (Perlin, Voronoi, ... ):  removes objects from the grid or adds objects to the grid to change the probability of an object appearing.
* viewport constraint visualizer
* geometry constraints: matching edges/faces
* maybe various grid shapes: cubic, spherical, and cylindrical