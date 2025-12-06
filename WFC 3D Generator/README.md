The WFC 3D Generator add-on procedurally generates a new object from a collection of objects using a simple implementation of the Wave Function Collapse algorithm with constraints.

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
* WFC 3D Backup:
  * Import/Export all WFC 3D Generator constraints to/from a JSON file.
* WFC 3D Rotation Tool:
  * Copies and rotates an object along with its adjacency constraints.

## Constraints Overview
* Adjacency Constraints: 
  * Neighbor Constraints: define a list of allowed neighbors for all possible directions (at once);
    Advantage: easy to define, Disadvantage: difficult to expand
  * Connector Constraints: define a connector name for any direction that match with the connector name of possible neighbors with the same connector name in the opposite direction;
    Advantage: building blocks are easily expandable, Disadvantage: not always easy to define
  * Geometry Constraints: Edges or faces are used to determine whether two objects can be placed next to each other.
  * Empty Neighbor Constraints: These constraints prohibit empty neighbors.
* Dimensions Constraints:
  * This enables building blocks that are larger than a cell.
* Fixed Position Constraints:
  * This allows you to set a fixed starting position within the grid in order to achieve a more predictable result.
* Grid and Region Constraints:
  * Allows you to specify where an object may be located within the grid.
* Distance Constraints:
  * Rules that restrict the placement of building blocks based on their distance from a specific point or another building block.
* Probability Constraints:
  * These constraints increase or decrease the probability of an object being selected at random.
* Region Probability Constraints:
  * These constraints increase or decrease the probability of an object being selected at random in a specific region.
* Frequency Constraints:
  * Define how often the same object or any other object may occur in the immediate vicinity or on one of the 3 axes XYZ.
* Region Frequency Constraints:
  * Define how often the same object may occur in a specific region.
* Symmetry Constraints:
  * These constraints allow mirror-symmetric and/or rotation-symmetric objects to be generated.
  * It is possible to transfer random transformations to mirror partners, flip mirror partners accordingly,
    or define other building blocks as mirror partners.
* Transformations:
  * These are not really restrictions. This allows you to randomize the position, size, rotation, and flipping of building blocks.
* Noise Constraints:
  * Noise constraints either influence the probability of an object occurring or replace random values in transformations with noise values. 


More information about the constraints can be found on [GitHub](https://github.com/DanRohde/blender-stuff/blob/main/WFC%203D%20Generator/constraints.md).

An overview of all custom properties can be found on [GitHub](https://github.com/DanRohde/blender-stuff/blob/main/WFC%203D%20Generator/properties.md).

## How the WFC 3D Generator algorithm works
1. **Initializes** each cell of the grid with a list of permitted building blocks. Grid and region constraints are taken into account.
2. Find the cell with the **lowest entropy**, in this case, the cell with the smallest list of building blocks. If there is more than one, the first or a random one is selected.
3. **Collapse** the cell: Select a random object from the list of building blocks. Dimensions, empty neighbor, and probability constraints are taken into account
4. **Propagate** the constraints of the randomly selected building block to the neighborhood and the entire grid. Symmetry constraints,  (region) frequency constraints, distance constraints, dimensions constraints, and adjacency constraints are applied.
5. **Repeat** steps 2-4 until all cells are collapsed.
6. **Render** the grid in the order in which cells are collapsed. Transformations are applied.

More information about the constraints can be found on [GitHub](https://github.com/DanRohde/blender-stuff/blob/main/WFC%203D%20Generator/constraints.md).

## Limitations and Known Issues
* For neighbor restrictions to take effect, there must be more than one object in the source collection.
* Region constraints don't work with all symmetry constraint variants
* Dimensions constraints can cause empty cells, especially in conjunction with symmetry constraints



## Upcoming Features
* 3D Viewport constraint visualizer
* some tutorials and documentation (thx, David-rD, for your feedback)
* ??? I need more feedback with ideas. You can give me feedback on Blender.org or [GitHub](https://github.com/DanRohde/blender-stuff/discussions) ???