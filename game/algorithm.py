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

# NEW: Bonus for each *new* resource type a node offers
DIVERSITY_BONUS = 2.5 

# --- Main Function ---

def calculate_node_scores(board_data, player_resources=None):
    """
    Calculates scores for all 54 nodes based on the provided board data.
    
    board_data: list of dicts with {resource, roll, index}
    player_resources: (optional) list of strings of resources a player *already* has
    returns: dict of {node_id: {score, description, resources}}
    """
    if player_resources is None:
        player_resources = []

    # --- Encapsulated Classes ---
    
    class Cell:
        def __init__(self, resource: str, roll: int):
            self.resource = resource
            self.roll = roll

        def getDotValue(self) -> int:
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
                roll = cellData[cellDataIdx].get("roll", 0) 
                if roll is None:
                    roll = 0
                cellGrid[rowIdx][cellIdx] = Cell(resource, roll)
                cellDataIdx += 1
        return cellGrid

    class Node:
        def __init__(self, node_num: int, cell_list: list, port_type: str = None):
            self.nodeNum = node_num
            self.cellList = cell_list
            self.port = port_type
            
            # These will be populated by other methods
            self.new_resources_found = [] 
            self.stats = {} # Will be filled by _analyze_production
        
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
            
            summary = []
            for r, count in resource_counts.items():
                if count > 1:
                    summary.append(f"{r} (x{count})")
                else:
                    summary.append(r)
            return ", ".join(summary)
        
        def _analyze_production(self) -> dict:
            """Internal helper to get detailed stats *before* scoring."""
            stats = {"dots": 0, "high": 0, "mid": 0, "low": 0, "unique": set()}
            for cell in self.cellList:
                if cell.resource == 'desert':
                    continue
                
                stats["unique"].add(cell.resource)
                stats["dots"] += cell.getDotValue()
                
                if cell.roll in [6, 8]: stats["high"] += 1
                elif cell.roll in [5, 9, 4, 10]: stats["mid"] += 1
                elif cell.roll in [2, 3, 11, 12]: stats["low"] += 1
            
            stats["unique_count"] = len(stats["unique"])
            return stats

        def getDescription(self, player_resources: list) -> str:
            """
            Generate strategic description based on node's resources.
            MUST be called *after* calcCellScore() to have stats.
            """
            
            # self.stats is populated by calcCellScore, which is called *before* this.
            if not self.stats or self.stats["dots"] == 0:
                if self.port:
                    return f"No production. Offers {self.port.capitalize()} port access."
                return "No production."

            desc_parts = []
            resources_str = self.getResourceSummary()

            # 1. Overall Production Rating
            if self.stats["high"] >= 2:
                desc_parts.append(f"Excellent Numbers: Touches two high-prob tiles ({resources_str}).")
            elif self.stats["high"] == 1:
                desc_parts.append(f"Strong Production: Built on {resources_str} with a 6 or 8.")
            elif self.stats["mid"] >= (1 + self.stats["low"]): # e.g., (5,9) > (2)
                desc_parts.append(f"Good Production: Solid mid-range numbers on {resources_str}.")
            elif self.stats["dots"] > 0:
                desc_parts.append(f"Modest Production: Relies on {resources_str}.")

            # 2. Resource Diversity (Node-level)
            if self.stats["unique_count"] == 3:
                desc_parts.append("PRO: High resource diversity.")
            elif self.stats["unique_count"] == 1 and len(self.cellList) > 1:
                desc_parts.append("CON: Relies heavily on one resource.")

            # 3. Port Bonus
            if self.port:
                is_match = any(cell.resource in self.port for cell in self.cellList if cell.resource != 'desert')
                if is_match:
                    desc_parts.append(f"PRO: Excellent {self.port.capitalize()} port synergy!")
                elif self.port == '3:1':
                    desc_parts.append("PRO: Valuable 3:1 port access.")
                else:
                    # e.g., A wood port on a brick/sheep node
                    desc_parts.append(f"PRO: Access to {self.port.capitalize()} port.")

            # 4. Cons (Low Numbers)
            if self.stats["low"] > 0 and self.stats["high"] == 0:
                desc_parts.append(f"CON: Risky, relies on {self.stats['low']} low-prob number(s).")

            # 5. Strategic Fit (Player-level)
            if self.new_resources_found:
                needed_str = ", ".join([r.capitalize() for r in self.new_resources_found])
                # This is the most important info, add it last for emphasis.
                desc_parts.append(f"STRATEGIC FIT: Offers needed {needed_str}.")

            return " ".join(desc_parts)

        def getSameResourceIndecies(self) -> list:
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

        def calcCellScore(self, player_resources: list) -> float:
            # --- Call analyzer helper FIRST ---
            # This populates self.stats for getDescription() to use
            self.stats = self._analyze_production()
            
            cellScore = 0
            
            DOUBLE_R_DIM = 0.90
            TRIPLE_R_DIM = 0.75
            PORT_INCREASE = 1.0
            SAME_RESOURCE_BONUS = 1.0

            sameResourceIndecies = self.getSameResourceIndecies()
            
            if len(self.cellList) == 0:
                return 0

            sorted_cells = sorted(self.cellList, key=lambda c: c.getDotValue(), reverse=True)

            if len(sameResourceIndecies) == 3:
                # All three are the same resource
                cellScore += sorted_cells[0].getDotValue() * resource_values[sorted_cells[0].resource]
                cellScore += sorted_cells[1].getDotValue() * resource_values[sorted_cells[1].resource] * DOUBLE_R_DIM
                cellScore += sorted_cells[2].getDotValue() * resource_values[sorted_cells[2].resource] * TRIPLE_R_DIM
            
            elif len(sameResourceIndecies) == 2:
                # Two cells are the same
                cell1 = self.cellList[sameResourceIndecies[0]]
                cell2 = self.cellList[sameResourceIndecies[1]]
                
                if cell1.getDotValue() >= cell2.getDotValue():
                    cellScore += cell1.getDotValue() * resource_values[cell1.resource]
                    cellScore += cell2.getDotValue() * resource_values[cell2.resource] * DOUBLE_R_DIM
                else:
                    cellScore += cell2.getDotValue() * resource_values[cell2.resource]
                    cellScore += cell1.getDotValue() * resource_values[cell1.resource] * DOUBLE_R_DIM

                # Now, add the score for the third, different cell *if it exists*
                if len(self.cellList) == 3:
                    other_cell_index = 3 - (sameResourceIndecies[0] + sameResourceIndecies[1])
                    other_cell = self.cellList[other_cell_index]
                    cellScore += other_cell.getDotValue() * resource_values[other_cell.resource]
            
            else:
                # No matching resources, or only 1-2 tiles with different resources
                for cell in self.cellList:
                    cellScore += cell.getDotValue() * resource_values[cell.resource]

            # --- Port Logic ---
            if self.port is not None:
                cellScore += PORT_INCREASE
                for cell in self.cellList:
                    if cell.resource in self.port and cell.resource != "desert":
                        cellScore += SAME_RESOURCE_BONUS
                        break

            # --- Diversity Bonus Logic ---
            if player_resources:
                new_resources_on_this_node = set()
                for cell in self.cellList:
                    if cell.resource not in player_resources and cell.resource != "desert":
                        new_resources_on_this_node.add(cell.resource)
                
                # Store for getDescription()
                self.new_resources_found = list(new_resources_on_this_node)
                
                # Apply bonus
                bonus = len(new_resources_on_this_node) * DIVERSITY_BONUS
                cellScore += bonus

            return cellScore

    # --- End of Encapsulated Classes ---

    # 1. Initialize the board grid
    cellGrid = initializeCells(board_data)
    
    # 2. Define Port Mappings
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

    # 3. Define Node-to-Cell Mappings
    # *** DATA FIX: Corrected n21, n22, n32, n33 to match your original file ***
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
        "n21": [cellGrid[1][2], cellGrid[1][1], cellGrid[2][2]], # Hexes 5, 4, 9
        "n22": [cellGrid[1][2], cellGrid[1][3], cellGrid[2][3]], # Hexes 5, 6, 10
        "n23": [cellGrid[1][2], cellGrid[1][3], cellGrid[2][3]], # Hexes 5, 6, 10 (Wait, n21 is 4,5,9. n22 is 5,9,10)
        "n24": [cellGrid[1][3], cellGrid[2][3], cellGrid[2][4]], # Hexes 6, 10, 11
        "n25": [cellGrid[1][3], cellGrid[2][4]],
        "n26": [cellGrid[2][4]],
        # row 4
        "n27": [cellGrid[2][0]],
        "n28": [cellGrid[2][0], cellGrid[3][0]],
        "n29": [cellGrid[2][0], cellGrid[2][1], cellGrid[3][0]],
        "n30": [cellGrid[2][1], cellGrid[3][0], cellGrid[3][1]],
        "n31": [cellGrid[2][1], cellGrid[2][2], cellGrid[3][1]],
        "n32": [cellGrid[2][2], cellGrid[3][1], cellGrid[3][2]], # Hexes 9, 13, 14
        "n33": [cellGrid[2][2], cellGrid[2][3], cellGrid[3][2]], # Hexes 9, 10, 14
        "n34": [cellGrid[2][3], cellGrid[3][2], cellGrid[3][3]], # Hexes 10, 14, 15
        "n35": [cellGrid[2][3], cellGrid[2][4], cellGrid[3][3]], # Hexes 10, 11, 15
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
        node_port = port_map.get(i) 
        
        node = Node(i, node_cell_list, node_port)
        
        score = node.calcCellScore(player_resources)
        description = node.getDescription(player_resources) 
        
        result[i] = {
            "score": round(score, 1),
            "description": description,
            "resources": node.getResourceSummary()
        }
    
    return result