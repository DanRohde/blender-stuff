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

## Limitations and Known Issues
* For neighbor restrictions to take effect, there must be more than one object in the source collection.

## Statistics: Constraints per Object
* Neighbor constraints: 26
* Grid constraints: 30
* Probability constraints: 2
* Transformation constraints: 10
* Frequency constraints: 15


* **Sum: 83**

## Neighbor Constraints
* Allows neighbors to be restrict in all directions: face neighbors, edge neighbors (`wfc_en_...`), corner neighbors (`wfc_cn_...`)
* Used custom properties: face neighbors: `wfc_[left|right|front|back|top|bottom]`, edge neighbors: `wfc_en_[fl|fr|ft|fb|bl|br|bt|bb|lt|lb|rt|rb]`,
  corner neighbors: `wfc_cn[fbl|fbr|ftl|ftr|bbl|bbr|btl|btr]`
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

	
## Probability Constraints
* Used custom property: `wfc_weight`
* Allowed property values:
    * empty string - weight of 1
    * 0 - object will not be used
    * 1..n - increases the chance of being chosen by a factor of n


## Transformation Constraints
* Used custom properties: `wfc_translation_min,wfc_translation_max,wfc_translation_steps,wfc_rotation_min,wfc_rotation_max,wfc_rotation_steps,wfc_scale_min,wfc_scale_max,wfc_scale_steps`
* Allowed property values:
    * wfc_translation_min,wfc_translation_max,wfc_translation_steps: a float vector (x,y,z)
    * wfc_rotation_min,wfc_rotation_max,wfc_rotation_steps: a float vector  (x,y,z)
    * wfc_scale_type: integer value: 0 - no scaling, 1 - uniform scaling, 2 - non-uniform scaling
    * wfc_scale_uni: a float vector (min,max,steps) for uniform scaling
    * wfc_scale_min,wfc_scale_max,wfc_scale_steps: a float vector (x,y,z) for non-uniform scaling
    
   
## Frequency Constraints
* Used custom properties: `wfc_freq_[any_]neighbor[_face|_edge|_corner],wfc_freq_grid,wfc_freq_[any_]axles`
* Allowed property values:
   * wfc_grid, wfc_freq_[any_]neighbor[_face|_edge|_corner]: an integer
   * wfc_[_any]_axles: an integer vector


## Upcoming Features
* more constraints: symmetry, pattern, local/region, ...
* a constraint validator ...
* a different kind of constraints based on connector types instead of object lists
