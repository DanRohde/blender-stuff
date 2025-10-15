import bpy
import numpy as np
import random
from collections import deque

from .constants import DIRECTIONS, TRANSFORMATION_CONSTRAINTS


class WFC3DConstraints:
    
    def __init__(self):
        self.constraints = {}
    
    def initialize_constraints(self, objects):
        """Loads constraints from custom properties"""
        allobjects = [o.name for o in objects]
        for obj in objects:
            obj_name = obj.name
            self.constraints[obj_name] = {}
            
            if obj.name in bpy.data.collections:
                    obj = bpy.data.collections[obj.name].objects[0]
                
            # load weight constraints
            if "wfc_weight" in obj and obj["wfc_weight"] != "":
                self.constraints[obj_name]["weight"] = int(obj["wfc_weight"])
            else:
                self.constraints[obj_name]["weight"] = 1

            # load grid constraints
            grid_constraints = { 'wfc_corners':'corners', 'wfc_edges':'edges', 'wfc_inside':'inside','wfc_faces' :'faces' }
            for gc in grid_constraints:
                if gc in obj and obj[gc] != "":
                    self.constraints[obj_name][grid_constraints[gc]] = obj[gc].split(",")
            
            # load transformation constraints
            for r in TRANSFORMATION_CONSTRAINTS:
                if "wfc_"+r in obj:
                    self.constraints[obj_name][r] = obj["wfc_"+r]
                else:
                    self.constraints[obj_name][r] = None
                    
            
            # load neighbor constraints
            for direction in DIRECTIONS:
                prop_name = f"wfc_{direction.lower()}"
                # take first element from collection to get constraints
                if prop_name in obj:
                    if obj[prop_name] == "":
                        self.constraints[obj_name][direction] = allobjects
                    else:
                        self.constraints[obj_name][direction] = obj[prop_name].split(',')
                else:
                    self.constraints[obj.name][direction] = allobjects 

    def get_weighted_options(self, obj_names):
        """ Increase object count in object list depending on it's weight """
        options = []
        for name in obj_names:
            weight = self.constraints[name]['weight']
            option = [name for _ in range(weight)]
            options.extend(option)
        return options

    def apply_transformation_constraints(self, src_obj, target_obj):
        def _get_mapped_random_values(vmin, vmax, steps):
            if (steps < 0 and vmin > vmax):
                steps =- steps
                s = vmax
                vmax = vmin 
                vmin = s
                
            if (steps > 0 and vmax-vmin >= 0):
                v = []
                i = vmin
                while i<=vmax:
                    v.append(i)
                    i += steps
                if (i-steps < vmax):
                    v.append(vmax)   
                return v[random.randrange(0,len(v))]
            else:
                return vmin + (vmax - vmin) * random.random()
        constraints = self.constraints[src_obj.name]    
        if constraints["translation_min"] is not None and constraints["translation_max"] is not None and constraints["translation_steps"] is not None:
            tmin = constraints["translation_min"]
            tmax = constraints["translation_max"]
            ts = constraints["translation_steps"]
            loc = target_obj.location
            for i in range(3):
                loc[i]+=_get_mapped_random_values(tmin[i], tmax[i], ts[i])
            target_obj.location = loc
        
        if constraints["scale_type"] is not None and constraints["scale_type"] > 0:
            
            if constraints["scale_type"] == 1 and constraints["scale_uni"] is not None:
                s = _get_mapped_random_values(constraints["scale_uni"][0], constraints["scale_uni"][1], constraints["scale_uni"][2])
                target_obj.scale.x = s 
                target_obj.scale.y = s
                target_obj.scale.z = s
            if constraints["scale_type"] == 2 and constraints["scale_min"] is not None and constraints["scale_max"] is not None and constraints["scale_steps"] is not None:
                smin = constraints["scale_min"]
                smax = constraints["scale_max"]
                ss = constraints["scale_steps"]
                
                target_obj.scale.x = _get_mapped_random_values(smin[0], smax[0], ss[0])
                target_obj.scale.y = _get_mapped_random_values(smin[1], smax[1], ss[1])
                target_obj.scale.z = _get_mapped_random_values(smin[2], smax[2], ss[2])
        
        if constraints["rotation_min"] is not None and constraints["rotation_max"] is not None and constraints["rotation_steps"] is not None:
            rmin = constraints["rotation_min"]
            rmax = constraints["rotation_max"]
            rs = constraints["rotation_steps"]
            
            axis=['X','Y','Z']
            for i in range(3):
                a = _get_mapped_random_values(rmin[i], rmax[i], rs[i])
                if a!=0:
                    target_obj.rotation_euler.rotate_axis(axis[i], a)
        
    def propagate(self, grid, x, y, z):
        """Propagate constraints to neighbors"""
        queue = deque([(x, y, z)])
        
        while queue:
            cx, cy, cz = queue.popleft()
            if len(grid.grid[cx,cy,cz])>0:
                current_obj =  grid.grid[cx, cy, cz][0]
            else:
                continue
            
            for direction, (dx, dy, dz) in DIRECTIONS.items():
                nx, ny, nz = cx + dx, cy + dy, cz + dz             
                if 0 <= nx < grid.grid_size[0] and \
                   0 <= ny < grid.grid_size[1] and \
                   0 <= nz < grid.grid_size[2]:
                    neighbor_options = grid.grid[nx, ny, nz]
                    if len(neighbor_options) > 1:
                        # Find permitted neighbors for this direction
                        allowed = self.constraints[current_obj].get(direction, [])
                        # Filter disallowed options
                        new_options = [obj for obj in neighbor_options if obj in allowed]
                        if len(new_options) < len(neighbor_options):
                            grid.grid[nx, ny, nz] = new_options
                            queue.append((nx, ny, nz))
        
