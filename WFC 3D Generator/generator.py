import random
import numpy as np

from .constraints import WFC3DConstraints
from .grid import WFC3DGrid
from .helper import get_default_empty_name
from .geometry import auto_detect_spacing

class WFC3DGenerator:
    def __init__(self, props):
        self.props = props
        self.collection = props.collection_obj
        self.grid_size = props.grid_size
        self.use_constraints = props.use_constraints
        self.random_start_cell = props.random_start_cell
        self.collapsed_cells = []
        self.spacing = self.get_spacing(self.props)

        self.set_seed(props.seed)

        self.objects = []
        self.constraints = None
        self.load_objects()

        self.grid = WFC3DGrid(self.grid_size)

        if self.use_constraints:
            self.constraints = WFC3DConstraints()
            self.constraints.initialize_constraints(self.grid, self.collection, self.objects, self.spacing)

    def get_spacing(self, props):
        if not props.auto_detect_spacing: return props.spacing

        spacing = auto_detect_spacing(props)
        props.spacing = spacing
        return spacing

    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(np.abs(seed))

    def load_objects(self):
        """Loads objects from the collection"""
        self.objects = [ obj for obj in self.collection.objects if not obj.name.startswith(get_default_empty_name())]
        self.objects.extend([child for child in self.collection.children if len(child.objects)>0])
        if not self.objects:
            raise ValueError("Collection is empty!")

    
    def get_entropy(self, x, y, z):
        """Calculates the entropy (number of possible states) of a cell"""
        return len(self.grid.grid[x, y, z])

    def get_lowest_entropy_cell(self):
        """Finds the cell with the lowest entropy"""
        min_entropy = float('inf')
        min_cells = {}
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if self.grid.collapsed[x, y, z]: continue
                    entropy = self.get_entropy(x, y, z)
                    if entropy > min_entropy: continue
                    min_entropy = entropy
                    min_cell = (x, y, z)
                    if min_entropy in min_cells:
                        min_cells[min_entropy].append(min_cell)
                    else:
                        min_cells[min_entropy] = [ min_cell ]

        if len(min_cells) == 0: return None
        
        if self.random_start_cell:
            return random.choice(min_cells[min_entropy])
        else:
            return min_cells[min_entropy][0]
        
    def collapse(self, cell):
        """Collapses a cell into a single state"""
        if self.use_constraints:
            collapsed = self.constraints.collapse(cell)
        else:
            x, y, z = cell
            self.grid.grid[x, y, z] = [random.choice(self.grid.grid[x,y,z])]
            collapsed = [ self.grid.mark_collapsed(x, y, z) ]
        return collapsed

    def generate_model(self, progress = None):
        """Execute WFC algorithm and generate the model"""

        self.grid.initialize_grid(self.objects, self.constraints)
        if self.use_constraints: self.collapsed_cells.extend(self.constraints.propagate(self.constraints.apply_post_init_constraints()))
        while True:
            cell = self.get_lowest_entropy_cell()
            if cell is None: break
            collapsed = self.collapse(cell)
            self.collapsed_cells.extend(self.constraints.propagate(collapsed) if self.use_constraints else collapsed)
            if progress is not None: progress.update_inc(len(collapsed))
        if self.use_constraints: self.constraints.propagate_post_gen_constraints()

    def generate_model_in_background_task(self, progress = None):
        cell = self.get_lowest_entropy_cell()
        if cell is None:
            if self.use_constraints: self.constraints.propagate_post_gen_constraints()
            return False
        collapsed = self.collapse(cell)
        self.collapsed_cells.extend(self.constraints.propagate(collapsed) if self.use_constraints else collapsed)
        if progress is not None: progress.update_inc(len(collapsed))
        return True

    def init_generate_model_in_background(self):
        self.grid.initialize_grid(self.objects, self.constraints)
        if self.use_constraints: self.collapsed_cells.extend(self.constraints.propagate(self.constraints.apply_post_init_constraints()))

    def clean(self):
        self.grid.clean()
        self.grid = None
        self.objects = None
        self.collapsed_cells = None
        if self.constraints: self.constraints.clean()
        self.constraints = None
        self.props = None
        self.collection = None
        self.grid_size = None