import bpy
import numpy as np
from itertools import product
from mathutils import Vector, Matrix
import random
from collections import deque

from .constants import *
from .helper import get_default_empty_object, get_default_empty_name, get_noise, remap
from .geometry import compare_edges, compare_faces

class WFC3DConstraints:
    def __init__(self):
        self.constraints = {}
        self.objects = {}
        self.auto_weights = {}
        self.sympartner = []
        self.sympartner_obj = []
        self.symtransform = []
        self.symflip = []
        self.grid = None
        self.cache_geometry_compare = {}
        self.collection = None
        self.spacing = None
    
    def initialize_constraints(self, grid, collection, objects, spacing):
        """Loads constraints from custom properties"""
        self.objects = objects
        default_obj = get_default_empty_object(collection)
        self.collection = collection
        self.grid = grid
        self.sympartner = np.empty(grid.grid_size, dtype=object)
        self.sympartner_obj = np.empty(grid.grid_size, dtype=object)
        self.symtransform = np.empty(grid.grid_size, dtype=object)
        self.symflip = np.empty(grid.grid_size, dtype=object)
        self.spacing = spacing
        for obj in objects:
            obj_name = obj.name
            self.constraints[obj_name] = {}
            self.cache_geometry_compare[obj_name] = {}
            if obj_name in bpy.data.collections:
                obj = get_default_empty_object(bpy.data.collections[obj_name])
                if obj is None: obj = bpy.data.collections[obj_name].objects[0]

            # load probability, frequency, transformation, symmetry, region, neighbor
            for p in GEN_CONSTRAINTS + ADD_NEIGHBOR_CONSTRAINTS:
                cp = "wfc_"+p
                if p in LIST_CONSTRAINTS:
                    self.constraints[obj_name][p] = []
                    if cp in obj: self.constraints[obj_name][p].append(obj[cp]) # backward compatibility
                    if default_obj is not None:
                        idx = 0
                        while f"{cp}_{idx}" in default_obj:
                            self.constraints[obj_name][p].append(default_obj[f"{cp}_{idx}"])
                            idx += 1
                    idx = 0
                    while f"{cp}_{idx}" in obj:
                        self.constraints[obj_name][p].append(obj[f"{cp}_{idx}"])
                        idx += 1
                    if cp in obj and len(self.constraints[obj_name][p])==0: self.constraints[obj_name][p].append(obj[cp]) # backward compatibility
                elif cp in obj and obj[cp] != "":
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

            for direction in DIRECTIONS:
                if direction.startswith("ANY"): continue
                dirlower = direction.lower()
                # load connector constraints:
                self.constraints[obj_name]["conn_"+dirlower] = self.get_adjacency_property_value(direction, 'conn_', obj, default_obj)
                # load neighbor constraints:
                val  = self.get_adjacency_property_value(direction,'', obj, default_obj)
                self.constraints[obj_name][dirlower] = None if val == '' else val.split(',')

    def get_adjacency_property_value(self, direction, prefix, obj, default_obj):
        cname = prefix + direction.lower()
        prop_name = f"wfc_{cname}"
        any_prop_name = f"wfc_{prefix}any"
        any_face_prop_name = f"wfc_{prefix}any_face"
        any_edge_prop_name = f"wfc_{prefix}any_edge"
        any_corner_prop_name = f"wfc_{prefix}any_corner"

        val = PROP_DEFAULTS[cname]
        if prop_name in obj and obj[prop_name] != "":
            val = obj[prop_name]
        elif any_face_prop_name in obj and obj[any_face_prop_name] != "" and direction in FACE_DIRECTIONS:
            val = obj[any_face_prop_name]
        elif any_edge_prop_name in obj and obj[any_edge_prop_name] != "" and direction in EDGE_DIRECTIONS:
            val = obj[any_edge_prop_name]
        elif any_corner_prop_name in obj and obj[any_corner_prop_name] != "" and direction in CORNER_DIRECTIONS:
            val = obj[any_corner_prop_name]
        elif any_prop_name in obj and obj[any_prop_name] != "":
            val = obj[any_prop_name]
        elif default_obj:
            if prop_name in default_obj and default_obj[prop_name] != "":
                val = default_obj[prop_name]
            elif any_face_prop_name in default_obj and default_obj[any_face_prop_name] != "" and direction in FACE_DIRECTIONS:
                val = default_obj[any_face_prop_name]
            elif any_edge_prop_name in default_obj and default_obj[any_edge_prop_name] != "" and direction in EDGE_DIRECTIONS:
                val = default_obj[any_edge_prop_name]
            elif any_corner_prop_name in default_obj and default_obj[any_corner_prop_name] != "" and direction in CORNER_DIRECTIONS:
                val = default_obj[any_corner_prop_name]
            elif any_prop_name in default_obj and default_obj[any_prop_name] != "":
                val = default_obj[any_prop_name]
        return val
    def are_grid_constraints_satisfied(self, name, pos):
        if 'noise_prob_basis' in self.constraints[name] and self.constraints[name]['noise_prob_basis'] > 1:
                n = get_noise(pos, self.constraints[name]['noise_prob_basis'], self.constraints[name]['noise_prob_scale'], 0, 1)
                return n >= self.constraints[name]['noise_prob_threshold']
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
        if 'regprob_probability' in self.constraints[name]:
            for i in range(len(self.constraints[name]['regprob_probability'])):
                if self.constraints[name]['regprob_probability'][i] != 0 and self.constraints[name]['regprob_weight'][i] != 0: continue
                if self.grid.is_inside_region(pos, self.constraints[name]['regprob_min'][i], self.constraints[name]['regprob_max'][i]): return False
        if 'regfreq_freq' in self.constraints[name]:
            for i in range(len(self.constraints[name]['regfreq_freq'])):
                if self.constraints[name]['regfreq_freq'][i] != 0: continue
                if self.grid.is_inside_region(pos, self.constraints[name]['regfreq_min'][i], self.constraints[name]['regfreq_max'][i]): return False
        ret = True
        if 'region_min' in self.constraints[name] or 'region_max' in self.constraints[name]:
            ret = ret and self.grid.is_inside_region(pos, self.constraints[name].get('region_min', None),
                                                self.constraints[name].get('region_max', None))
        if 'region_quadrant' in self.constraints[name]:
            ret = ret and self.grid.is_inside_region_quadrant(pos, self.constraints[name]['region_quadrant'])

        return ret

    def get_auto_weight(self, name):
        if not self.constraints[name].get('auto_weight', False): return 0
        if self.auto_weights.get(name, -1) != -1: return self.auto_weights.get(name)

        weight = 0
        for d in DIRECTIONS:
            if d not in self.constraints[name] or self.constraints[name][d] == "":
                weight += len(self.objects)
            else:
                weight += len(self.constraints[name][d])
        for c in CONNECTOR_CONSTRAINTS:
            if c not in self.constraints[name] or self.constraints[name][c] == "":
                weight += len(self.objects)
            else:
                weight += 1
        for c in GRID_CONSTRAINTS:
            if c not in self.constraints[name] or self.constraints[name][c] == "":
                weight += len(self.objects)
            else:
                weight += len(self.constraints[name][c])
        for c in REGION_CONSTRAINTS:
            if c not in self.constraints[name] or self.constraints[name][c] == "":
                weight += len(self.objects)
        if sum(self.constraints[name]['dim_xyz'])==3: weight += 1
        maxlen = (len(CONNECTOR_CONSTRAINTS+GRID_CONSTRAINTS+REGION_CONSTRAINTS)+len(DIRECTIONS)+1)*len(self.objects)
        weight = int(round(len(self.objects) * weight/ maxlen))

        self.auto_weights[name] = weight
        return weight

    def get_region_weight(self, position, element):
        if 'regprob_weight' not in self.constraints[element]: return -1
        for r in range(len(self.constraints[element]['regprob_weight'])):
            if self.grid.is_inside_region(position, self.constraints[element]['regprob_min'][r], self.constraints[element]['regprob_max'][r]): return self.constraints[element]['regprob_weight'][r]
        return -1

    def get_weighted_options(self, position, elements):
        options = []
        for name in elements:
            weight = self.get_auto_weight(name)
            region_weight = self.get_region_weight(position, name)
            if region_weight != -1: weight = region_weight
            if self.constraints[name].get('weight',-1) > -1 or weight > 0:
                weight += self.constraints[name].get('weight',1)
                option = [name for _ in range(weight)]
                options.extend(option)
            else:
                options.extend(elements)
        return options

    def get_region_probability(self, position, element):
        if 'regprob_probability' not in self.constraints[element]: return -1
        for r in range(len(self.constraints[element]['regprob_probability'])):
            if self.grid.is_inside_region(position, self.constraints[element]['regprob_min'][r], self.constraints[element]['regprob_max'][r]): return self.constraints[element]['regprob_probability'][r]
        return -1

    def apply_probability_constraints(self, position, elements):
        options= []
        rand = random.random()
        random.shuffle(elements)
        for name in elements:
            p = self.constraints[name]['probability']
            rp = self.get_region_probability(position, name)
            if rp != -1: p = rp
            if p is not None and p < 1:
                if rand < p:
                    options = [name]
                    break
            else:
                options.append(name)
        return self.get_weighted_options(position, options)

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

    def get_mirror_partner_and_flipping(self, element, location, point):
        x, y, z = location
        nx, ny, nz = point
        mp = element
        flipping = (1,1,1)
        if nx == x and ny == y and nz == z: return mp, flipping
        if nx != x and ny == y and nz == z:
            if self.constraints[element]["sym_mirror_axes_x"] is not None: mp = self.constraints[element]["sym_mirror_axes_x"].name
            if self.constraints[element]["sym_mirror_flip_x"]: flipping = (-1, 1, 1)
        elif nx == x and ny != y and nz == z:
            if self.constraints[element]["sym_mirror_axes_y"] is not None: mp = self.constraints[element]["sym_mirror_axes_y"].name
            if self.constraints[element]["sym_mirror_flip_y"]: flipping = (1, -1, 1)
        elif nx == x and ny == y and nz != z:
            if self.constraints[element]["sym_mirror_axes_z"] is not None: mp = self.constraints[element]["sym_mirror_axes_z"].name
            if self.constraints[element]["sym_mirror_flip_z"]: flipping = (1, 1, -1)
        elif nx != x and ny != y and nz == z:
            if self.constraints[element]["sym_mirror_axes_xy"] is not None: mp = self.constraints[element]["sym_mirror_axes_xy"].name
            if self.constraints[element]["sym_mirror_flip_xy"]: flipping = (-1, -1, 1)
        elif nx != x and ny == y and nz != z:
            if self.constraints[element]["sym_mirror_axes_xz"] is not None: mp = self.constraints[element]["sym_mirror_axes_xz"].name
            if self.constraints[element]["sym_mirror_flip_xz"]: flipping = (-1, 1, -1)
        elif nx == x and ny != y and nz != z:
            if self.constraints[element]["sym_mirror_axes_yz"] is not None: mp = self.constraints[element]["sym_mirror_axes_yz"].name
            if self.constraints[element]["sym_mirror_flip_yz"]: flipping = (1, -1, -1)
        elif nx != x and ny != y and nz != z:
            if self.constraints[element]["sym_mirror_axes_xyz"] is not None: mp = self.constraints[element]["sym_mirror_axes_xyz"].name
            if self.constraints[element]["sym_mirror_flip_xyz"]: flipping = (-1, -1, -1)
        return mp, flipping
    def apply_symmetry_constraints(self, x, y, z):
        """Apply symmetry to collapsed cells"""
        grid = self.grid
        if len(grid.grid[x,y,z])==0: 
            return []
        mirror_axes = self.constraints[grid.grid[x,y,z][0]]["sym_mirror_axes"]
        rotate_n = self.constraints[grid.grid[x,y,z][0]]["sym_rotate_n"]
        rotate_axis = self.constraints[grid.grid[x, y, z][0]]["sym_rotate_axis"] if rotate_n and rotate_n > 0 else None
        collapsed = []

        if mirror_axes or rotate_axis:
            points = self.mirror_and_rotate_3d((x,y,z), grid.grid_size, mirror_axes, rotate_axis, rotate_n)
            for point in points:
                nx, ny, nz = point
                if x==nx and y==ny and z==nz: continue
                mp, flipping = self.get_mirror_partner_and_flipping(grid.grid[x,y,z][0], (x,y,z), point)
                grid.grid[nx, ny, nz] = [ mp ]
                collapsed.append(grid.mark_collapsed(nx,ny,nz))
                self.sympartner[nx, ny, nz] = [[x,y,z]]
                self.symflip[nx, ny, nz] = flipping
        self.sympartner[x,y,z] = collapsed
        return collapsed

    def _check_dimensions(self, position, dimensions, flipping):
        if sum(dimensions) == 3: return True
        x, y, z = position
        for nx in range(dimensions[0]):
            for ny in range(dimensions[1]):
                for nz in range(dimensions[2]):
                    gx, gy, gz = x + nx * flipping[0], y + ny * flipping[1], z + nz * flipping[2]
                    if not self.grid.within_boundaries(gx, gy, gz) or self.grid.collapsed[gx, gy, gz]: return False
        return True

    def check_space(self, elements, position):
        x, y, z = position
        options = []
        for element in elements:
            if self._check_dimensions(position, self.constraints[element]["dim_xyz"], (1,1,1) if not self.symflip[x,y,z] else self.symflip[x,y,z]): options.append(element)
        return options

    def apply_dimensions_constraints(self, x, y, z):
        collapsed = []
        if not self.grid.within_boundaries(x,y,z): return collapsed
        if len(self.grid.grid[x,y,z]) == 0: return collapsed
        obj_name = self.grid.grid[x,y,z][0]
        if sum(self.constraints[obj_name]["dim_xyz"]) == 3: return collapsed
        d = self.constraints[obj_name]["dim_xyz"]
        coll = []
        fac = (1,1,1) if self.symflip[x,y,z] is None else self.symflip[x,y,z]
        for nx in range(d[0]):
            for ny in range(d[1]):
                for nz in range(d[2]):
                    gx,gy,gz = x+nx*fac[0],y+ny*fac[1],z+nz*fac[2]
                    if not self.grid.within_boundaries(gx,gy,gz) or (((nx!=0)or(ny!=0)or(nz!=0)) and self.grid.collapsed[gx,gy,gz]): continue
                    coll.append([gx,gy,gz])
        if len(coll) == d[0]*d[1]*d[2]:
            for c in coll:
                self.grid.grid[c[0], c[1], c[2]] = self.grid.grid[x, y, z]
                collapsed.append(self.grid.mark_collapsed(c[0], c[1], c[2]))
        else:
            self.grid.grid[x, y, z] = []
            print(f"Ooops, cell {x},{y},{z} did not collapse as expected. {obj_name} does not fit.")
        return collapsed

    def collapse(self, grid, x, y, z):
        """Collapse a grid cell with constraints"""
        collapsed = []
        options = self.apply_probability_constraints((x,y,z), self.check_space(grid.grid[x,y,z], (x,y,z)))
        if len(options)>0:
            grid.grid[x, y, z] = [ random.choice(options) ]
        else:
            grid.grid[x, y, z] = []
        collapsed.append(grid.mark_collapsed(x, y, z))
        collapsed.extend(self.apply_symmetry_constraints(x, y, z))
        self.propagate_region_frequency_constraints(x, y, z)
        self.propagate_frequency_constraints(grid, x, y, z)

        collapsedadd = []
        for c in collapsed:
            collapsedadd.extend(self.apply_dimensions_constraints(c[0], c[1], c[2]))
        collapsed.extend(collapsedadd)
        return collapsed

    def apply_transformation_constraints(self, position, obj_name, target_obj):
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
        x,y,z = position
        if obj_name not in self.constraints: return
        constraints = self.constraints[obj_name]

        if self.symtransform[x, y, z] is not None:
            mat = self.symtransform[x, y, z]
            tmat, smat, rmat, fmat = mat[:3], mat[3:6], mat[6:9], mat[9:]
            if self.symflip[x, y, z] is not None:
                smat = [ a*b for a,b in zip(smat, self.symflip[x, y, z]) ]
                if constraints['sym_mirror_flip_transl']: tmat = [ a*b for a,b in zip(tmat, self.symflip[x, y, z]) ]
            for i in range(3):
                target_obj.location[i] += tmat[i]
            target_obj.scale.x, target_obj.scale.y, target_obj.scale.z = smat
            axis = ['X','Y','Z']
            for i in range(len(axis)):
                if rmat[i] != 0: target_obj.rotation_euler.rotate_axis(axis[i], rmat[i])

            target_obj.scale.x *= fmat[0]
            target_obj.scale.y *= fmat[1]
            target_obj.scale.z *= fmat[2]
            return
        symtransmat = []
        noisefactor = 1 if constraints["noise_transf_basis"] < 2 else get_noise(position, constraints["noise_transf_basis"], constraints["noise_transf_scale"])

        if constraints["translation_min"] is not None or constraints["translation_max"] is not None or constraints["translation_steps"] is not None:
            tmin = constraints.get("translation_min",PROP_DEFAULTS["translation_min"])
            tmax = constraints.get("translation_max",PROP_DEFAULTS["translation_max"])
            ts = constraints.get("translation_steps",PROP_DEFAULTS["translation_steps"])
            loc = target_obj.location
            newloc = [0.0, 0.0, 0.0]
            for i in range(3):
                newloc[i] = _get_mapped_random_values(tmin[i], tmax[i], ts[i])
                if tmin[i]!=tmax[i] and noisefactor!=1: newloc[i] = remap(noisefactor, -1, 1, tmin[i], tmax[i])
                loc[i] += newloc[i] if self.symflip[x, y, z] is None or not constraints['sym_mirror_flip_transl'] else newloc[i] * self.symflip[x, y, z][i]
            target_obj.location = loc
            symtransmat.extend(newloc)
        else:
            symtransmat.extend([0.0, 0.0, 0.0])
        if constraints["scale_type"] is not None and constraints["scale_type"] > 0:
            sm = [0.0, 0.0, 0.0]
            if constraints["scale_type"] == 1 and constraints["scale_uni"] is not None:
                if noisefactor == 1:
                    s = _get_mapped_random_values(constraints["scale_uni"][0], constraints["scale_uni"][1], constraints["scale_uni"][2])
                else:
                    s = remap(noisefactor, -1, 1, constraints["scale_uni"][0], constraints["scale_uni"][1])
                sm = [s,s,s]
            if constraints["scale_type"] == 2 and constraints["scale_min"] is not None and constraints["scale_max"] is not None and constraints["scale_steps"] is not None:
                smin = constraints["scale_min"]
                smax = constraints["scale_max"]
                ss = constraints["scale_steps"]
                sm = [_get_mapped_random_values(smin[0], smax[0], ss[0]), _get_mapped_random_values(smin[1], smax[1], ss[1]), _get_mapped_random_values(smin[2], smax[2], ss[2])]
                if noisefactor !=1:
                    if smin[0] != smax[0]: sm[0] = remap(noisefactor, -1, 1, smin[0], smax[0])
                    if smin[1] != smax[1]: sm[1] = remap(noisefactor, -1, 1, smin[1], smax[1])
                    if smin[2] != smax[2]: sm[2] = remap(noisefactor, -1, 1, smin[2], smax[2])
            target_obj.scale.x = sm[0]
            target_obj.scale.y = sm[1]
            target_obj.scale.z = sm[2]
            symtransmat.extend(sm)
        else:
            symtransmat.extend([1.0, 1.0, 1.0])

        if self.symflip[x, y, z] is not None:
            target_obj.scale.x *= self.symflip[x, y, z][0]
            target_obj.scale.y *= self.symflip[x, y, z][1]
            target_obj.scale.z *= self.symflip[x, y, z][2]

        if constraints["rotation_min"] is not None or constraints["rotation_max"] is not None or constraints["rotation_steps"] is not None:
            rmin = constraints.get("rotation_min",PROP_DEFAULTS["rotation_min"])
            rmax = constraints.get("rotation_max",PROP_DEFAULTS["rotation_max"])
            rs = constraints.get("rotation_steps",PROP_DEFAULTS["rotation_steps"])
            axis=['X','Y','Z']
            rotmat = [0.0, 0.0, 0.0]
            for i in range(3):
                if noisefactor == 1:
                    a = _get_mapped_random_values(rmin[i], rmax[i], rs[i])
                else:
                    a = remap(noisefactor, -1, 1, rmin[i], rmax[i])
                rotmat[i] = a
                if a!=0: target_obj.rotation_euler.rotate_axis(axis[i], a)
            symtransmat.extend(rotmat)
        else:
            symtransmat.extend([0.0, 0.0, 0.0])

        if constraints["flipping"] is not None and sum(constraints["flipping"]) > 0:
            rv = np.random.rand(3)
            fv = [1, 1, 1]
            pv = constraints["flipping"]
            for i in range(3):
                if (1 - pv[i]) < rv[i]: fv[i] = -1
            target_obj.scale.x *= fv[0]
            target_obj.scale.y *= fv[1]
            target_obj.scale.z *= fv[2]
            symtransmat.extend(fv)
        else:
            symtransmat.extend([1.0, 1.0, 1.0])
        # transfer transformations to symmetry partners:
        if self.constraints[obj_name]['sym_mirror_trans'] and self.sympartner[x, y, z] is not None:
            for p in self.sympartner[x, y, z]: self.symtransform[p[0], p[1], p[2]] = symtransmat

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
    def propagate_region_frequency_constraints(self, x, y, z):
        if len(self.grid.grid[x,y,z])==0: return
        obj_name = self.grid.grid[x,y,z][0]

        for i in range(len(self.constraints[obj_name]["regfreq_freq"])):
            rmin = self.constraints[obj_name]["regfreq_min"][i]
            rmax = self.constraints[obj_name]["regfreq_max"][i]
            freq = self.constraints[obj_name]["regfreq_freq"][i]
            if freq >=0 and self.grid.is_inside_region((x,y,z), rmin, rmax):
                self.grid.remove_max_region_neighbors(x,y,z,freq,rmin,rmax)

    def set_cache_geometry_compare(self, current_obj, obj, direction, result):
        if not direction in self.cache_geometry_compare[current_obj]:
            self.cache_geometry_compare[current_obj][direction] = { obj : result }
        else:
            self.cache_geometry_compare[current_obj][direction][obj] = result
        if not OPPOSITE_DIRECTIONS[direction] in self.cache_geometry_compare[obj]:
            self.cache_geometry_compare[obj][OPPOSITE_DIRECTIONS[direction]] = { current_obj : result }
        else:
            self.cache_geometry_compare[obj][OPPOSITE_DIRECTIONS[direction]][current_obj] = result
        return result

    def exists_cache_geometry_compare(self, current_obj, obj, direction):
        if direction in self.cache_geometry_compare[current_obj] and obj in self.cache_geometry_compare[current_obj][direction]:
            return True
        if OPPOSITE_DIRECTIONS[direction] in self.cache_geometry_compare[obj] and current_obj in self.cache_geometry_compare[obj][OPPOSITE_DIRECTIONS[direction]]:
            return True
        return False

    def get_cache_geometry_compare(self, current_obj, obj, direction):
        if direction in self.cache_geometry_compare[current_obj] and obj in self.cache_geometry_compare[current_obj][direction]:
            return self.cache_geometry_compare[current_obj][direction][obj]
        if OPPOSITE_DIRECTIONS[direction] in self.cache_geometry_compare[obj] and current_obj in self.cache_geometry_compare[obj][OPPOSITE_DIRECTIONS[direction]]:
            return self.cache_geometry_compare[obj][OPPOSITE_DIRECTIONS[direction]][current_obj]
        return True

    def compare_geometry(self, current_obj, obj, direction):
        if current_obj not in self.collection.objects or obj not in self.collection.objects: return True
        if self.exists_cache_geometry_compare(current_obj, obj, direction): return self.get_cache_geometry_compare(current_obj, obj, direction)
        if self.collection.objects[current_obj].type != 'MESH' or self.collection.objects[obj].type != 'MESH':
            return self.set_cache_geometry_compare(current_obj, obj, direction, True)

        result = True
        if self.constraints[current_obj]["geo_match_edges"]:
            cmpresult = compare_edges(self.collection.objects[current_obj], direction, self.collection.objects[obj],
                                      OPPOSITE_DIRECTIONS[direction],
                                      self.constraints[current_obj]["geo_tolerance"], self.spacing)
            result = result and cmpresult["obj_a_edges_count"] == cmpresult["obj_b_edges_count"] and cmpresult["matching_edges_count"] == cmpresult["obj_a_edges_count"]
        if self.constraints[current_obj]["geo_match_faces"]:
            cmpresult = compare_faces(self.collection.objects[current_obj], direction, self.collection.objects[obj],
                                      OPPOSITE_DIRECTIONS[direction],
                                      self.constraints[current_obj]["geo_tolerance"], self.spacing)

            result = result and cmpresult["obj_a_faces_count"] == cmpresult["obj_b_faces_count"] and cmpresult["matching_faces_count"] == cmpresult["obj_a_faces_count"]

        self.set_cache_geometry_compare(current_obj, obj, direction, result)
        return result

    def propagate(self, grid, x, y, z):
        """Propagate constraints"""

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
                if not grid.within_boundaries(nx, ny, nz) or grid.collapsed[nx,ny,nz] or direction.startswith('ANY'): continue
                neighbor_options = grid.grid[nx, ny, nz]

                dirlower = direction.lower()
                oppdirlower = OPPOSITE_DIRECTIONS[direction].lower()

                # Filter disallowed neighbor options
                new_options = [obj
                               for obj in neighbor_options
                                if (self.constraints[current_obj][dirlower] is None or obj in self.constraints[current_obj][dirlower])
                                    and (self.constraints[obj][oppdirlower] is None or current_obj in self.constraints[obj][oppdirlower])
                               ]
                if len(new_options) == 0 and self.constraints[current_obj]['allow_neighbor_constraint_violations']:
                    new_options= [obj for obj in neighbor_options if self.constraints[obj]['allow_neighbor_constraint_violations']]

                # Filter disallowed connector options:
                if self.constraints[current_obj].get('conn_'+dirlower,"") != "":
                    prop_name = 'conn_' + dirlower
                    opp_prop_name = 'conn_' + oppdirlower
                    new_options = [obj for obj in new_options if
                                   self.constraints[current_obj][prop_name] == self.constraints[obj][opp_prop_name] or
                                   self.constraints[obj][opp_prop_name] == ""]

                # Filter disallowed geometry:
                if self.constraints[current_obj]['geo_match_edges'] or self.constraints[current_obj]['geo_match_faces']:
                    if direction in FACE_DIRECTIONS and self.constraints[current_obj][f"geo_{dirlower}"]:
                        new_options = [ obj for obj in new_options if self.compare_geometry(current_obj, obj, direction)]

                if len(new_options) >= len(neighbor_options): continue
                grid.grid[nx, ny, nz] = new_options
                if len(new_options) == 1: queue.append((nx, ny, nz))

    def get_random_object_from_collection(self, pos, collection):
        x, y, z = pos
        if self.sympartner[x, y, z] is not None:
            if self.sympartner_obj[x, y, z] is None:
                ol = [o for o in collection.objects if not o.name.startswith(get_default_empty_name())]
                self.sympartner_obj[x, y, z] = random.choice(ol) if len(ol)>0 else []
                for p in self.sympartner[x, y, z]:
                    self.sympartner_obj[p[0],p[1],p[2]] = self.sympartner_obj[x, y, z]
            return self.sympartner_obj[x, y, z]
        return random.choice([o for o in collection.objects if not o.name.startswith(get_default_empty_name())])

    def apply_fixed_position_constraints(self, obj):
        collapsed = []
        if self.constraints[obj.name]["fixed_position_xyz"] is not None:
            for p in self.constraints[obj.name]["fixed_position_xyz"]:
                if not self.grid.within_boundaries(p[0], p[1], p[2]): continue
                self.grid.grid[p[0], p[1], p[2]] = [ obj.name ]
                collapsed.extend(self.collapse(self.grid, p[0], p[1], p[2]))
        return collapsed

    def apply_distance_from_position_constraints(self, obj):
        collapsed = []
        for i, distance in enumerate(self.constraints[obj.name]["distance"]):
            if self.constraints[obj.name]["distance_from"][i] == 1:
                position = self.constraints[obj.name]["distance_position"][i]
                gs = self.grid.grid_size
                minx, miny, minz = max(0, position[0] - distance[0]), max(0, position[1] - distance[1]), max(0, position[2] - distance[2])
                maxx, maxy, maxz = min(gs[0]-1, position[0] + distance[0]), min(gs[1]-1, position[1] + distance[1]), min(gs[2]-1, position[2] + distance[2])
                self.grid.remove_obj_in_region(obj.name, (minx, miny, minz),(maxx, maxy, maxz))
        return collapsed

    def apply_pre_constraints(self):
        collapsed = []
        for obj in self.objects:
            collapsed.extend(self.apply_fixed_position_constraints(obj))
            collapsed.extend(self.apply_distance_from_position_constraints(obj))
        return collapsed

    def apply_dimensions_draw_constraints(self, position, spacing, obj_name, new_obj):
        x, y, z = position
        if sum(self.constraints[obj_name]["dim_xyz"])==3: return
        d = self.constraints[obj_name]["dim_xyz"]
        # align element:
        loc = new_obj.location
        fac = (1, 1, 1) if self.symflip[x, y, z] is None else self.symflip[x, y, z]
        newloc = [ loc[0] + (d[0]-1)/2 * spacing[0] * fac[0], loc[1] + (d[1]-1)/2 * spacing[1] * fac[1], loc[2] + (d[2]-1)/2 * spacing[2] * fac[2] ]
        new_obj.location = newloc

        # prevent drawing:
        for nx in range(d[0]):
            for ny in range(d[1]):
                for nz in range(d[2]):
                    self.grid.grid[x+nx*fac[0], y+ny*fac[1], z+nz*fac[2]] = []

    def apply_draw_constraints(self, position, spacing, obj_name, target_obj):
        self.apply_transformation_constraints(position, obj_name, target_obj)
        self.apply_dimensions_draw_constraints(position, spacing, obj_name, target_obj)

    def clean(self):
        self.grid = None
        self.constraints = None
        self.objects = None
        self.auto_weights = None
        self.sympartner_obj = None
        self.sympartner = None
        self.symflip = None
        self.symtransform = None
        self.cache_geometry_compare = None
        self.collection = None
        self.spacing = None