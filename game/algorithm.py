import random

# --- Constants ---

# Resource multipliers
resource_values = {
    "brick": 1.2,
    "wood": 1.2,
    "ore": 1.1,
    "wheat": 1.1,
    "sheep": 1,
    "desert": 0
}

# Roll → dot count (probability weight)
roll_dots = {
    6: 5, 8: 5,
    5: 4, 9: 4,
    4: 3, 10: 3,
    3: 2, 11: 2,
    2: 1, 12: 1,
    0: 0,
    None: 0
}

# --- Helper Functions ---

# --- Main Function ---

def calculate_node_scores(board_data):
    """
    Calculates scores for all 54 nodes based on the provided board data.
    
    board_data: list of dicts with {resource, roll, index}
    returns: dict of {node_id: {score, description, resources}}
    """

    # --- Encapsulated Classes ---
    # We define the classes *inside* the function to avoid global state
    
    class Cell:
        def __init__(self, resource: str, roll: int):
            self.resource = resource
            self.roll = roll

        def getDotValue(self) -> int:
            # Use the global roll_dots dictionary
            return roll_dots.get(self.roll, 0)
        
        def __str__(self) -> str:
            return f"{self.resource}, {self.roll}"
    
    def initializeCells(cellData: list) -> list:
        """Initialize the cell grid from board data"""
        cellGrid = [
            [None, None, None],
            [None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None],
            [None, None, None]
        ]
        
        cellDataIdx = 0
        for rowIdx in range(5):
            for cellIdx in range(len(cellGrid[rowIdx])):
                resource = cellData[cellDataIdx]["resource"]
                # Use .get() for safety, defaulting to 0
                roll = cellData[cellDataIdx].get("roll", 0) 
                if roll is None: # Handle explicit None
                    roll = 0
                cellGrid[rowIdx][cellIdx] = Cell(resource, roll)
                cellDataIdx += 1

        return cellGrid

    class Node:
        def __init__(self, node_num: int, cell_list: list, port_type: str = None):
            self.nodeNum = node_num
            self.cellList = cell_list
            self.port = port_type
            self.hasSettlement = False # Not used in this function, but good for state
        
        def getResourceSummary(self) -> str:
            """Generate a human-readable summary of resources at this node"""
            resource_counts = {}
            for cell in self.cellList:
                if cell.resource != 'desert':
                    r = cell.resource.capitalize()
                    if r not in resource_counts:
                        resource_counts[r] = 0
                    resource_counts[r] += 1
            
            if not resource_counts:
                return "Desert location"
            
            # Create description like "Wood, Brick (2), Ore"
            summary = []
            for r, count in resource_counts.items():
                if count > 1:
                    summary.append(f"{r} (x{count})")
                else:
                    summary.append(r)
            return ", ".join(summary)

        def getDescription(self) -> str:
            """Generate strategic description based on node's resources"""
            score = self.calcCellScore()
            resources = self.getResourceSummary()
            
            # Count high-value numbers (6, 8)
            high_nums = sum(1 for cell in self.cellList if cell.roll in [6, 8])
            
            if score >= 13:
                return f"Excellent spot with {resources}. High productivity!"
            elif score >= 10:
                if high_nums >= 2:
                    return f"Strong position with {resources} and great numbers."
                else:
                    return f"Good balance of {resources}."
            elif score >= 7:
                return f"Decent {resources} access with moderate numbers."
            elif score > 0:
                return f"Limited {resources} production."
            else:
                return "No production here."

        def getSameResourceIndecies(self) -> list:
            """
            Correctly finds the resource with the most tiles on this node.
            Returns a list of indecies for that resource, or [] if no duplicates.
            """
            resource_map = {}
            for i, cell in enumerate(self.cellList):
                if cell.resource == 'desert':
                    continue
                if cell.resource not in resource_map:
                    resource_map[cell.resource] = []
                resource_map[cell.resource].append(i)
            
            best_indecies = []
            for indecies in resource_map.values():
                if len(indecies) > len(best_indecies):
                    best_indecies = indecies
                    
            return best_indecies if len(best_indecies) > 1 else []

        def calcCellScore(self) -> float:
            cellScore = 0
            
            # --- New Logic Constants ---
            DOUBLE_R_DIM = 0.90
            TRIPLE_R_DIM = 0.75
            PORT_INCREASE = 1.0
            SAME_RESOURCE_BONUS = 1.0

            sameResourceIndecies = self.getSameResourceIndecies()
            
            if len(self.cellList) == 0:
                return 0

            # Sort cells by dot value, highest first
            # This makes diminishing returns apply to the *worst* numbers first
            sorted_cells = sorted(self.cellList, key=lambda c: c.getDotValue(), reverse=True)

            if len(sameResourceIndecies) == 3:
                # All three are the same resource
                cellScore += sorted_cells[0].getDotValue() * resource_values[sorted_cells[0].resource]
                cellScore += sorted_cells[1].getDotValue() * resource_values[sorted_cells[1].resource] * DOUBLE_R_DIM
                cellScore += sorted_cells[2].getDotValue() * resource_values[sorted_cells[2].resource] * TRIPLE_R_DIM
            
            elif len(sameResourceIndecies) == 2:
                # Two cells are the same
                
                # Find the odd-one-out
                other_cell_index = 3 - (sameResourceIndecies[0] + sameResourceIndecies[1])
                other_cell = self.cellList[other_cell_index]
                
                # Add its score normally
                cellScore += other_cell.getDotValue() * resource_values[other_cell.resource]
                
                # Apply diminishing returns to the two same-resource cells
                cell1 = self.cellList[sameResourceIndecies[0]]
                cell2 = self.cellList[sameResourceIndecies[1]]
                
                if cell1.getDotValue() >= cell2.getDotValue():
                    cellScore += cell1.getDotValue() * resource_values[cell1.resource]
                    cellScore += cell2.getDotValue() * resource_values[cell2.resource] * DOUBLE_R_DIM
                else:
                    cellScore += cell2.getDotValue() * resource_values[cell2.resource]
                    cellScore += cell1.getDotValue() * resource_values[cell1.resource] * DOUBLE_R_DIM
            
            else:
                # No matching resources, or only 1-2 tiles
                for cell in self.cellList:
                    cellScore += cell.getDotValue() * resource_values[cell.resource]

            # --- Port Logic ---
            if self.port is not None:
                cellScore += PORT_INCREASE
                # Check if any adjacent resource matches the port
                # This fixes the bug: "brick" in "2brickf1" == True
                for cell in self.cellList:
                    if cell.resource in self.port and cell.resource != "desert":
                        cellScore += SAME_RESOURCE_BONUS
                        break # Only apply bonus once

            return cellScore

    # --- End of Encapsulated Classes ---

    # 1. Initialize the board grid
    cellGrid = initializeCells(board_data)
    
    # 2. Define Port Mappings (based on your new algorithm)
    # NOTE: Your original file had overlapping ports (e.g., 2 and 3). 
    # I am using the visual port locations from the frontend HTML.
    # Frontend node 1 (index 0) corresponds to "n0"
    nodesWithPorts = {
        1: "3:1",  # n1
        3: "3:1",  # n3
        6: "mountain", # n6
        15: "3:1", # n15
        26: "3:1", # n26
        37: "hill", # n37
        46: "3:1", # n46
        52: "pasture", # n52
        47: "forest", # n47
        38: "3:1", # n38
        27: "field", # n27
        16: "3:1", # n16
        7: "3:1"  # n7
        # This map assumes your 9 ports map to these 13 node locations
        # You may need to adjust which node gets which port
    }
    
    # Map node numbers to their 2-letter port types from your 'sea' dict
    # This is an EXAMPLE of how you'd map your new port logic.
    # You need to define which node gets which port.
    
    # For now, I will use the *resource names* from your 'nodesWithPorts'
    # dict to match your new 'calcCellScore' logic
    
    port_map = {
        2:"3:1", 3:"3:1",
        5:"3:1", 6:"3:1",
        15:"wheat", 25:"wheat",
        36:"wood", 46:"wood",
        52:"3:1", 53:"3:1",
        50:"sheep", 49:"sheep",
        48:"3:1", 47:"3:1",
        38:"brick", 28:"brick",
        17:"ore", 7:"ore"
    }


    # 3. Define Node-to-Cell Mappings (Using the CORRECT map from your old file)
    cellListDict = {
        # row 1
        "n0": [cellGrid[0][0]],
        "n1": [cellGrid[0][0]],
        "n2": [cellGrid[0][0], cellGrid[0][1]],
        "n3": [cellGrid[0][1]],
        "n4": [cellGrid[0][1], cellGrid[0][2]],
        "n5": [cellGrid[0][2]],
        "n6": [cellGrid[0][2]],
        # row 2
        "n7": [cellGrid[1][0]],
        "n8": [cellGrid[0][0], cellGrid[1][0]],
        "n9": [cellGrid[0][0], cellGrid[1][0], cellGrid[1][1]],
        "n10": [cellGrid[0][0], cellGrid[0][1], cellGrid[1][1]],
        "n11": [cellGrid[0][1], cellGrid[1][1], cellGrid[1][2]],
        "n12": [cellGrid[0][1], cellGrid[0][2], cellGrid[1][2]],
        "n13": [cellGrid[0][2], cellGrid[1][2], cellGrid[1][3]],
        "n14": [cellGrid[0][2], cellGrid[1][3]],
        "n15": [cellGrid[1][3]],
        # row 3
        "n16": [cellGrid[2][0]],
        "n17": [cellGrid[1][0], cellGrid[2][0]],
        "n18": [cellGrid[1][0], cellGrid[2][0], cellGrid[2][1]],
        "n19": [cellGrid[1][0], cellGrid[1][1], cellGrid[2][1]],
        "n20": [cellGrid[1][1], cellGrid[2][1], cellGrid[2][2]],
        "n21": [cellGrid[1][1], cellGrid[1][2], cellGrid[2][2]], # Corrected from your new file
        "n22": [cellGrid[1][2], cellGrid[2][2], cellGrid[2][3]], # Corrected from your new file
        "n23": [cellGrid[1][2], cellGrid[1][3], cellGrid[2][3]],
        "n24": [cellGrid[1][3], cellGrid[2][3], cellGrid[2][4]],
        "n25": [cellGrid[1][3], cellGrid[2][4]],
        "n26": [cellGrid[2][4]],
        # row 4
        "n27": [cellGrid[2][0]],
        "n28": [cellGrid[2][0], cellGrid[3][0]],
        "n29": [cellGrid[2][0], cellGrid[2][1], cellGrid[3][0]],
        "n30": [cellGrid[2][1], cellGrid[3][0], cellGrid[3][1]],
        "n31": [cellGrid[2][1], cellGrid[2][2], cellGrid[3][1]],
        "n32": [cellGrid[2][2], cellGrid[3][1], cellGrid[3][2]], # Corrected from your new file
        "n33": [cellGrid[2][2], cellGrid[2][3], cellGrid[3][2]], # Corrected from your new file
        "n34": [cellGrid[2][3], cellGrid[3][2], cellGrid[3][3]],
        "n35": [cellGrid[2][3], cellGrid[2][4], cellGrid[3][3]],
        "n36": [cellGrid[2][4], cellGrid[3][3]],
        "n37": [cellGrid[2][4]],
        # row 5
        "n38": [cellGrid[3][0]],
        "n39": [cellGrid[3][0], cellGrid[4][0]],
        "n40": [cellGrid[3][0], cellGrid[3][1], cellGrid[4][0]],
        "n41": [cellGrid[3][1], cellGrid[4][0], cellGrid[4][1]],
        "n42": [cellGrid[3][1], cellGrid[3][2], cellGrid[4][1]],
        "n43": [cellGrid[3][2], cellGrid[4][1], cellGrid[4][2]],
        "n44": [cellGrid[3][2], cellGrid[3][3], cellGrid[4][2]],
        "n45": [cellGrid[4][2], cellGrid[3][3]],
        "n46": [cellGrid[3][3]],
        # row 6
        "n47": [cellGrid[4][0]],
        "n48": [cellGrid[4][0]],
        "n49": [cellGrid[4][0], cellGrid[4][1]],
        "n50": [cellGrid[4][1]],
        "n51": [cellGrid[4][1], cellGrid[4][2]],
        "n52": [cellGrid[4][2]],
        "n53": [cellGrid[4][2]],
    }
    
    # 4. Create nodes, calculate scores, and format results
    result = {}
    for i in range(54):
        node_cell_list = cellListDict[f"n{i}"]
        node_port = port_map.get(i) # Get the port type, if one exists for this node
        
        node = Node(i, node_cell_list, node_port)
        score = node.calcCellScore()
        
        result[i] = {
            "score": round(score, 1),
            "description": node.getDescription(),
            "resources": node.getResourceSummary()
        }
    
    return result