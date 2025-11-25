# WFC 3D Generator - Custom Properties Overview
## Statistics: Constraint Properties per Object
* Neighbor constraints: 31
* Grid constraints: 4
* Region constraints: 3
* Probability constraints: 3
* Region probability constraints: 5
* Transformations: 12
* Frequency constraints: 11
* Region frequency constraints: 4
* Symmetry constraints: 19
* Connector constraints: 30
* Fixed position constraints: 1
* Dimensions constraints: 1
* Geometry constraints: 9
* Noise constraints: 4
* Distance constraints: 5

* **Sum: 142**

## Neighbor Constraints
* Allows neighbors to be restrict in all directions: face neighbors, edge neighbors (`wfc_en_...`), corner neighbors (`wfc_cn_...`)
* Used custom properties: face neighbors: `wfc_[left|right|front|back|top|bottom]`, edge neighbors: `wfc_en_[fl|fr|ft|fb|bl|br|bt|bb|lt|lb|rt|rb]`,
  corner neighbors: `wfc_cn_[fbl|fbr|ftl|ftr|bbl|bbr|btl|btr]`, `wfc_allow_neighbor_constraint_violations`, `wfc_any[_face|_edge|_corner]`
* Allowed property values:
    * empty string - allows all neighbors
    * comma separated list of object names - permitted neighbor(s)
    * "None" - disallows all neighbors

## Fixed Position Constraints
* This allows you to set a fixed starting position within the grid in order to achieve a more predictable result.
* Used custom property: `wfc_fixed_position_[0..n]`
* Allowed property value: an integer vector

## Dimensions Constraints
* This enables building blocks that are larger than a cell.
* Used custom property: `wfc_dim_xyz`
* Allowed property value: an integer vector

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

## Distance Constraints
* Used custom properties: `wfc_distance[_from|_object|_position|_subcollection]`
* Allowed property values:
  * wfc_distance: integer vector
  * wfc_distance_from: integer: 0: object,  1: position, 2: sub-collection
  * wfc_distance_object: a pointer to an object
  * wfc_distance_position: integer vector
  * wfc_distance_subcollection: a pointer to a collection

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

## Region Probability Constraints:
* Used custom properties: `wfc_regprob_[name|min|max|weight|probability]_[0..n]`
* Allowed property values:
  * wfc_regprob_name_[0..n]: a string with a region name
  * wfc_regprob_[min|max]: a float vector
  * wfc_regprob_weight: an integer
  * wfc_regprob_probability: a float value between 0 and 1

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

## Region Frequency Constraints:
* Used custom properties: `wfc_regfreq_name_[0..n],wfc_regfreq_min_[0..n],wfc_regfreq_max_[0..n],wfc_regfreq_freq_[0..n]`
* Allowed property values:
  * `wfc_regfreq_name_[0..n]`: a string with a region name 
  * `wfc_regfreq_min_[0..n], wfc_regfreq_max_[0..n]`: an integer vector (x,y,z)
  * `wfc_regfreq_freq`: an integer

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
* Used custom properties: `wfc_conn_[any[_face|_edge|_corner]|front|back|left|right|top|bottom|cn_(fbl|fbr|ftl|ftr|bbl|bbr|btl|btr)|en_(fl|fr|ft|fb|bl|br|bt|bb|lt|lb|rt|rb)]`
* Allowed property value: string with a connector name

## Geometry Constraints
* Used custom properties: `wfc_geo_[top|bottom|left|right|front|back],wfc_geo_match_[edges|faces], wfc_geo_tolerance`
* Allowed property values:
* wfc_geo_[top|bottom|left|right|front|back]: a boolean
* wfc_geo_match_[edges|faces]: a boolean
* wfc_geo_tolerance: a float value

## Noise Constraints
* Used custom properties: `wfc_noise_[prob|transf]_basis, wfc_noise_prob_threshold, wfc_noise_transf_scale`
* Allowed property values:
  * wfc_noise_[prob|transf]_basis: integer value between 2 - 11
  * wfc_noise_prob_threshold: float value between 0 and 1
  * wfc_noise_transf_scale: float value 0..inf