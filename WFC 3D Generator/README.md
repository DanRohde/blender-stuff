The WFC 3D Generator add-on generates a new object from a collection of objects using a simple implementation of the Wave Function Collapse algorithm with constraints.

Each object in the source collection can use custom properties to define the permitted neighbors. The generator randomly combines these objects in a 3D grid while adhering to the neighbor constraints. The allowed position in the grid can be defined by grid constraints. 

## Quick Start Guide
1. Install and enable the WFC 3D Generator add-on
2. Create a source collection with some objects
3. Define constraints: 
    1. open 3D Viewport: Press 'N' > WFC 3D > WFC 3D Constraints Editor
    2. select a source collection
    3. add some constraints to objects 


## Neighbor Constraints
* Used custom properties: ``wfc_left``, ``wfc_right`` ,``wfc_front``, ``wfc_back``, ``wfc_top``, ``wfc_bottom``
* Allowed property values:
	* empty string - allows all neighbors
	* comma separated list of object names - permitted neighbor(s)
	* "None" - disallows all neighbors


## Grid Constraints

**Corner constraints:**
* Used custom property: ``wfc_corners``
* Allowed property values:
	* empty string - allows all corners
	* "-" - forbids all corners
	* comma separated list of allowed corners: ``fbl,fbr,ftl,ftr,bbl,bbr,btl,btr`` ("f" - front, "b" - back or bottom in second position, "t" - top, "l" - left, "r" - right) 


**Edge constraints:**
* Used custom property: ``wfc_edges``
* Allowed property values:
	* empty string - allows all edges
	* "-" - forbids all edges
	* comma separated list of permitted edges: ``fb,fl,ft,fr,bb,bl,bt,br,lb,lt,rb,rt`` ("f" - front, "b" - back or bottom in second position, "t" - top, "l" - left, "r" - right)

	
**Face constraints:**
* Used custom property: ``wfc_faces``
* Allowed property values:
	* empty string - allows all faces
	* "-" - forbids all faces
	* comma separated list of permitted faces: ``front,back,top,bottom,left,right``


**Inside constraints:**
* Use custom property:	``wfc_inside``
* Allowed property values:
	* empty string - allows the object to stay inside the grid
	* "-" - forbids to stay inside

	
## Weight Constraint
* Used custom property: ``wfc_weight``
* Allowed property values:
	* empty string - weight of 1
	* 0 - object will not be used
	* 1..n - increases the chance of being chosen by a factor of n 


## Upcoming Features
* more constraints: count constraints ...
* a constraint validator to check for unknown objects ...
* a different kind of constraints based on connector types instead of object lists
