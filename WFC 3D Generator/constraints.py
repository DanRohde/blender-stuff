import bpy
import numpy as np
from itertools import product
from mathutils import Vector, Matrix
import random
from collections import deque

from .constants import *

class WFC3DConstraints:
    def __init__(self):
        self.constraints = {}
        self.symrotation = {}
        self.grid = None
    
    def initialize_constraints(self, grid, collection, objects):
        """Loads constraints from custom properties"""
        allobjects = [o.name for o in objects]
        default_obj = None
        if DEFAULT_EMPTY_NAME in collection.objects:
            default_obj = collection.objects[DEFAULT_EMPTY_NAME]

        self.grid = grid

        for obj in objects:
            obj_name = obj.name
            self.constraints[obj_name] = {}
            
            if obj.name in bpy.data.collections:
                if len(bpy.data.collections[obj_name].objects) >0:
                    obj = bpy.data.collections[obj.name].objects[0]
                else:
                    continue

            # load probability, frequency, transformation, symmetry constraints
            for p in PROBABILITY_CONSTRAINTS + FREQUENCY_CONSTRAINTS + TRANSFORMATION_CONSTRAINTS + SYMMETRY_CONSTRAINTS + REGION_CONSTRAINTS + ADD_NEIGHBOR_CONSTRAINTS:
                cp = "wfc_"+p
                if cp in obj and obj[cp] != "":
                    self.constraints[obj_name][p] = obj[cp]
                elif default_obj and cp in default_obj and default_obj[cp] != "":
                    self.constraints[obj_name][p] = default_obj[cp]
                else:
                    self.constraints[obj_name][p] = PROP_DEFAULTS[p]

            # load grid constraints
            for c in GRID_CONSTRAINTS:
                cp = "wfc_"+c
                if cp in obj and obj[cp] != "":
                    self.constraints[obj_name][c] = obj[cp].split(",")
                elif default_obj and cp in default_obj and default_obj[cp] != "":
                    self.constraints[obj_name][c] = default_obj[cp].split(",")

            # load neighbor constraints
            for direction in DIRECTIONS:
                prop_name = f"wfc_{direction.lower()}"
                eo = obj
                if prop_name not in obj and default_obj: eo = default_obj
                if prop_name in eo:
                    if eo[prop_name] == "":
                        self.constraints[obj_name][direction] = allobjects
                    else:
                        self.constraints[obj_name][direction] = eo[prop_name].split(',')
                else:
                    self.constraints[obj_name][direction] = allobjects 
    def are_grid_constraints_satisfied(self, name, pos):
        if 'corners' in self.constraints[name] and self.grid.is_corner(pos):
            for c in self.constraints[name]['corners']:
                if c == '' and len(self.constraints[name]['corners']) == 1: return True
                if c == '-' or c == 'None' or c == 'False': return False
                if c in self.grid.corners and pos == self.grid.corners[c]: return True
            return False
        if 'edges' in self.constraints[name] and self.grid.is_edge(pos):
            for c in self.constraints[name]['edges']:
                if c == '' and len(self.constraints[name]['edges']) == 1: return True
                if c == '-' or c == 'None': return False
                if c in self.grid.edges and self.grid.is_on_given_edge(pos, self.grid.edges[c]): return True
            return False
        if 'inside' in self.constraints[name] and self.grid.is_inside(pos):
            inside = self.constraints[name]['inside']
            if inside == '' or inside == 'True': return True
            if inside == '-' or inside == 'None' or inside == 'False': return False
            return False
        if 'faces' in self.constraints[name] and self.grid.is_face(pos):
            for f in self.constraints[name]['faces']:
                if f == '' and len(self.constraints[name]['faces']) == 1: return True
                if f == '-' or f == 'None' or f == 'False': return False
                if self.grid.is_on_specific_face(pos, f): return True
            return False
        ret = True
        if 'region_min' in self.constraints[name] or 'region_max' in self.constraints[name]:
            ret = ret and self.grid.is_inside_region(pos, self.constraints[name].get('region_min', None),
                                                self.constraints[name].get('region_max', None))
        if 'region_quadrant' in self.constraints[name]:
            ret = ret and self.grid.is_inside_region_quadrant(pos, self.constraints[name]['region_quadrant'])

        return ret
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

    @staticmethod
    def mirror_and_rotate_3d(coords, shape, mirror_axes=(False, False, False), rotate_axis=None, n_rotations=1):
        p = Vector(coords)
        center = Vector([(s-1)/2 for s in shape])
        generated_points = set()
    
        flip_options = [[False, True] if mirror_axes[i] else [False] for i in range(3)]
        mirrored_points = []
    
        for flip_x, flip_y, flip_z in product(*flip_options):
            q = p.copy()
            if flip_x: q.x = 2 * center.x - q.x
            if flip_y: q.y = 2 * center.y - q.y
            if flip_z: q.z = 2 * center.z - q.z
            mirrored_points.append(q)
    
        if rotate_axis is not None:
            rot_axis = Vector(rotate_axis).normalized()
        else:
            rot_axis = None
    
        for mp in mirrored_points:
            if rot_axis is None or n_rotations <= 1:
                # No rotation, just use the mirrored point
                qi = tuple(int(round(v)) for v in mp)
                if all(0 <= qi[i] < shape[i] for i in range(3)): generated_points.add(qi)
            else:
                for i in range(n_rotations):
                    theta = (2 * np.pi / n_rotations) * i
                    rot_matrix = Matrix.Rotation(theta, 4, rot_axis)
                    q_rot = rot_matrix @ (mp - center) + center
                    qi = tuple(int(round(v)) for v in q_rot)
                    if all(0 <= qi[j] < shape[j] for j in range(3)):
                        generated_points.add(qi)
    
        return generated_points

    def apply_symmetry_constraints(self, grid, x, y, z):
        """Apply symmetry to collapsed cells"""
        if len(grid.grid[x,y,z])==0: 
            return
        mirror_axes = self.constraints[grid.grid[x,y,z][0]]["sym_mirror_axes"]
        rotate_axis = self.constraints[grid.grid[x,y,z][0]]["sym_rotate_axis"]
        rotate_n = self.constraints[grid.grid[x,y,z][0]]["sym_rotate_n"]

        if rotate_axis and (not rotate_n or rotate_n <=0):
            rotate_axis = None        
            
        if mirror_axes or rotate_axis:
            points = self.mirror_and_rotate_3d((x,y,z), grid.grid_size, mirror_axes, rotate_axis, rotate_n)
            for point in points:
                nx,ny,nz = point
                if not (nx==x and ny==y and nz==z):
                    grid.grid[nx,ny,nz] = grid.grid[x,y,z]
                    #if 'sym_mirror_axes_rotate' in bpy.context.scene.wfc_props and bpy.context.scene.wfc_props['sym_mirror_axes_rotate']:
                        #if (nx,ny,nz) in self.symrotation:
                            #self.symrotation[(nx,ny,nz)] = tuple(a+b for a,b in zip(self.symrotation[(nx,ny,nz)], angles))
                        #self.symrotation[(nx, ny, nz)] = angles
                    grid.mark_collapsed(nx,ny,nz)

    def apply_symmetry_rotation(self, position, obj):
        angles = self.symrotation[position]
        axis = ['X', 'Y', 'Z']
        for a in range(3):
            obj.rotation_euler.rotate_axis(axis[a], angles[a])


    def collapse(self, grid, x, y, z):
        """Collapse a grid cell with constraints"""
        options = self.apply_probability_constraints(grid.grid[x,y,z])
        if len(options)>0:
            grid.grid[x, y, z] = [ random.choice(options) ]
        else:
            grid.grid[x, y, z] = []
        self.apply_symmetry_constraints(grid, x, y, z)
        grid.mark_collapsed(x, y, z)



    def apply_transformation_constraints(self, position, src_obj, target_obj):
        def _get_mapped_random_values(vmin, vmax, steps):
            if steps < 0 and vmin > vmax:
                steps =- steps
                sw = vmax
                vmax = vmin 
                vmin = sw
                
            if steps > 0 and vmax-vmin >= 0:
                v = []
                j = vmin
                while j<=vmax:
                    v.append(j)
                    j += steps
                if j-steps < vmax: v.append(vmax)
                return v[random.randrange(0,len(v))]
            else:
                return vmin + (vmax - vmin) * random.random()

        src_name = src_obj.name
            
        if src_name not in self.constraints:
            return 
        constraints = self.constraints[src_name]
        if constraints["translation_min"] is not None or constraints["translation_max"] is not None or constraints["translation_steps"] is not None:
            tmin = constraints.get("translation_min",PROP_DEFAULTS["translation_min"])
            tmax = constraints.get("translation_max",PROP_DEFAULTS["translation_max"])
            ts = constraints.get("translation_steps",PROP_DEFAULTS["translation_steps"])
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
        
        if constraints["rotation_min"] is not None or constraints["rotation_max"] is not None or constraints["rotation_steps"] is not None:
            rmin = constraints.get("rotation_min",PROP_DEFAULTS["rotation_min"])
            rmax = constraints.get("rotation_max",PROP_DEFAULTS["rotation_max"])
            rs = constraints.get("rotation_steps",PROP_DEFAULTS["rotation_steps"])
            
            axis=['X','Y','Z']
            for i in range(3):
                a = _get_mapped_random_values(rmin[i], rmax[i], rs[i])
                if a!=0: target_obj.rotation_euler.rotate_axis(axis[i], a)
        if position in self.symrotation:
            self.apply_symmetry_rotation(position, target_obj)

    def propagate_frequency_constraints(self, grid, x, y, z):
        if len(grid.grid[x,y,z])==0:
            return []
        reduced_cells = []
        current_obj = grid.grid[x,y,z][0]
        # grid frequency
        if self.constraints[current_obj]["freq_grid"] is not None and self.constraints[current_obj]["freq_grid"]>-1:
            count = 0
            if current_obj and self.constraints[current_obj]["freq_grid"] is not None and self.constraints[current_obj]["freq_grid"]>-1:
                count = grid.count_obj(current_obj)
            if self.constraints[current_obj]["freq_grid"] == 0: grid.grid[x,y,z] = []
           
            if count >= self.constraints[current_obj]["freq_grid"]: reduced_cells.extend(grid.remove_obj(current_obj, None, None))
        
        # neighbor frequency
        nf = [ { "freq_neighbor_face" : FACE_DIRECTIONS}, {"freq_neighbor_corner" : CORNER_DIRECTIONS}, {"freq_neighbor_edge" : EDGE_DIRECTIONS}, {"freq_neighbor" : DIRECTIONS}]
        for a in nf:
            for p,direction in a.items():
                if self.constraints[current_obj][p] is not None and self.constraints[current_obj][p]>-1:
                    if grid.count_neighbors(x, y, z, current_obj, direction) > self.constraints[current_obj][p]:
                        reduced_cells.extend(grid.remove_neighbors(x, y, z, current_obj, direction))
        
        # axes
        axis={ 0: [1,0,0], 1: [0,1,0], 2 : [0,0,1]}
        if self.constraints[current_obj]["freq_axes"] is not None:
            max_count = self.constraints[current_obj]["freq_axes"]
            for i in range(3):
                if max_count[i] < 0: continue
                if grid.count_axis_neighbors(x,y,z,current_obj,axis[i])[i] >= max_count[i]:
                    reduced_cells.extend(grid.remove_axis_neighbors(x,y,z,current_obj,axis[i]))
        
        nf = [ { "freq_any_neighbor_face" : FACE_DIRECTIONS}, {"freq_any_neighbor_corner" : CORNER_DIRECTIONS}, {"freq_any_neighbor_edge" : EDGE_DIRECTIONS}, {"freq_any_neighbor" : DIRECTIONS}]
        # any neighbor frequency
        for a in nf:
            for p, direction in a.items():
                if self.constraints[current_obj][p] is not None and self.constraints[current_obj][p]>-1:
                    diff = self.constraints[current_obj][p] - grid.count_neighbors(x, y, z, None, direction)
                    if diff < 0: grid.remove_max_neighbors(x, y, z, abs(diff), direction)
        
        if self.constraints[current_obj]["freq_any_axes"] is not None:
            max_count = self.constraints[current_obj]["freq_any_axes"]
            for i in range(3):
                if max_count[i]<0:
                    continue
                diff = max_count[i] - grid.count_axis_neighbors(x, y, z, None, axis[i])[i]
                if diff < 0: grid.remove_max_axis_neighbors(x, y, z, abs(diff), axis[i])
        return reduced_cells
     
    def propagate(self, grid, x, y, z):
        """Propagate constraints"""
                
        # propagate neighbor constraints:
        queue = deque([(x, y, z)])
        queue.extend(self.propagate_frequency_constraints(grid, x, y, z))
        
        while queue:
            cx, cy, cz = queue.popleft()
            if len(grid.grid[cx,cy,cz])>0:
                current_obj =  grid.grid[cx, cy, cz][0]
            else:
                continue

            for direction, (dx, dy, dz) in DIRECTIONS.items():
                nx, ny, nz = cx + dx, cy + dy, cz + dz             
                if not grid.within_boundaries(nx, ny, nz) or grid.collapsed[nx,ny,nz]: continue

                neighbor_options = grid.grid[nx, ny, nz]

                # Filter disallowed options
                new_options = [obj for obj in neighbor_options if obj in self.constraints[current_obj].get(direction, []) and current_obj in self.constraints[obj].get(OPPOSITE_DIRECTIONS[direction],[])]

                if len(new_options) >= len(neighbor_options): continue
                if len(new_options) == 0 and self.constraints[current_obj]['allow_neighbor_constraint_violations']:
                    new_options= [obj for obj in neighbor_options if self.constraints[obj]['allow_neighbor_constraint_violations']]
                    if len(new_options) == 0: new_options = [random.choice(neighbor_options)]
                    if len(new_options) >= len(neighbor_options): continue

                grid.grid[nx, ny, nz] = new_options
                queue.append((nx, ny, nz))
