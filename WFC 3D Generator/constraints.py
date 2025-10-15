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
                
            # load probability and frequency constraints
            for p in ["weight","probability","freq_acles","freq_grid","freq_neighbor"]:
                cp = "wfc_"+p
                if cp in obj and obj[cp] != "":
                    self.constraints[obj_name][p] = obj[cp]
                else:
                    self.constraints[obj_name][p] = None

            # load grid constraints
            grid_constraints = { 'wfc_corners':'corners', 'wfc_edges':'edges', 'wfc_inside':'inside','wfc_faces' :'faces' }
            for cp,c in grid_constraints.items():
                if cp in obj and obj[cp] != "":
                    self.constraints[obj_name][c] = obj[cp].split(",")
            
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

    def get_weighted_options(self, elements):
        options = []    
        for name in elements:
            if self.constraints[name]['weight']:
                weight = self.constraints[name]['weight']
                option = [name for _ in range(weight)]
                options.extend(option)
            else:
                options.extend(elements)
        return options
    
    def apply_probability_constraints(self, elements):
        options= []
        rand = random.random()
        random.shuffle(elements)
        for name in elements:
            p = self.constraints[name]['probability']
            if p is not None and p < 1:
                if rand < p:
                    options = [name]
                    break
            else:
                options.append(name)
        return self.get_weighted_options(options)

    def apply_frequency_constraints(self, elements):
        # XXXX count elements if frequency options are set
        
        return elements
    
    def collapse(self, grid, x, y, z):
        """ Collapse a grid cell with constraints """    
        options = self.apply_probability_constraints(grid.grid[x,y,z])
        if len(options)>0:
            grid.grid[x, y, z] = [ random.choice(options) ]
        else:
            grid.grid[x, y, z] = []
        grid.mark_collapsed(x, y, z)


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
        """Propagate constraints"""
        
        if len(grid.grid[x,y,z])>0:
            current_obj = grid.grid[x,y,z][0]
        else:
            current_obj = None
        
        # propagate frequency constraints:
        if current_obj and self.constraints[current_obj]["freq_grid"] is not None and self.constraints[current_obj]["freq_grid"]>-1:
            count = grid.count_obj(current_obj, None, None)
            if self.constraints[current_obj]["freq_grid"] == 0: 
                grid.grid[x,y,z] = []
           
            if count >= self.constraints[current_obj]["freq_grid"]:
                grid.remove_obj(current_obj, None, None)
                
                
        # propagate neighbor constraints:
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
        
