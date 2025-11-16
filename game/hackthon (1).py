#Nilton coelho

import random
random.seed()

DEF_CELL_DATA = [{"resource":"wood", "roll":5},
            {"resource":"desert", "roll":0},
            {"resource":"ore", "roll":2},
            {"resource":"brick", "roll":8},
            {"resource":"sheep", "roll":10},
            {"resource":"wood", "roll":9},
            {"resource":"ore", "roll":6},
            {"resource":"wheat", "roll":4},
            {"resource":"wood", "roll":3},
            {"resource":"ore", "roll":11},
            {"resource":"sheep", "roll":4},
            {"resource":"wheat", "roll":3},
            {"resource":"sheep", "roll":11},
            {"resource":"brick", "roll":6},
            {"resource":"wood", "roll":5},
            {"resource":"wheat", "roll":8},
            {"resource":"sheep", "roll":12},
            {"resource":"brick", "roll":9},
            {"resource":"ore", "roll":10}]




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
    2: 1, 12: 1
}

sea = {
    "empty":0,
    "3for1":1,
    "2brickf1":1.25,
    "2woodf1":1.25,
    "2oref1":1.25,
    "2wheatf1":1.25,
    "2sheepf1":1.25
    }

resources = ["wood", "brick", "ore", "wheat", "sheep", "desert"]

# intitalizes cells in cellGrid
def initializeCells(cellData=[], randomize=False):

    cellGrid =[[None, None, None],
           [None, None, None, None],
           [None, None, None, None, None],
           [None, None, None, None],
           [None, None, None]]
    
    if(randomize):
        return randomInititialization(cellGrid)
    else:
        return normalInitialization(cellGrid, cellData)

# initializes cells in cellGrid using the cellData
def normalInitialization(cellGrid=[[]], cellData=[])->list:
    cellDataIdx = 0
    for rowIdx in range(5):
        for cellIdx in range(len(cellGrid[rowIdx])):
            resource = cellData[cellDataIdx]["resource"]
            roll = cellData[cellDataIdx]["roll"]
            cellGrid[rowIdx][cellIdx] = Cell(resource, roll)
            cellDataIdx += 1

    return cellGrid

# randomly creates cells with random values
def randomInititialization(cellGrid=[[]])->list:
    resourceNum = 6

    for rowIdx in range(5):
        for cellIdx in range(len(cellGrid[rowIdx])):
            resource = resources[random.randint(0, resourceNum-1)]
            roll : int
            if (resource == "desert"):
                resourceNum -= 1
                roll = 0
            else:
                roll = random.randint(2,12)
            cellGrid[rowIdx][cellIdx] = Cell(resource,roll)

    return cellGrid
            
cellIdx = 0

# Class: Cell
class Cell:

    resource:str
    roll:int
    cellNum:int

    def __init__(self, resource:str,roll:int):
        global cellIdx
        self.resource = resource
        self.roll = roll
        self.cellNum = cellIdx
        cellIdx += 1

    def getDotValue(self)->int:
        dotValues = {0:0,7:0,2:1,12:1,3:2,11:2,4:3,10:3,5:4,9:4,6:5,8:5}
        return dotValues[self.roll]
    
    def __str__(self)->str:
        return f"Cell {self.cellNum}: {self.resource} , {self.roll}"
        
    
# End of Cell Class


    

nodeIdx = 0


# Class: Node
class Node:
    cellList : list[Cell]
    consecutiveNodes : list['Node']
    hasSettlement : bool
    port : str

    def __init__(self):
        global nodeIdx
        self.hasSettlement = False
        self.cellList = cellListDict[f"n{str(nodeIdx)}"]
        self.nodeNum = nodeIdx
        self.port = None
        if (self.nodeNum in nodesWithPorts):
            self.port = nodesWithPorts[self.nodeNum]
        nodeIdx += 1

    def calcCellScore(self)->int:
        cellScore = 0
        sameResourceIndecies = self.getSameResourceIndecies()
        DOUBLE_R_DIM = 0.90
        TRIPLE_R_DIM = 0.75
        PORT_INCREASE = 1
        SAME_RESOURCE_BONUS = 1

        # only 2 cells have the same resource
        if (len(sameResourceIndecies) == 2):
            if (self.cellList[sameResourceIndecies[0]].roll >= self.cellList[sameResourceIndecies[1]].roll):
                cellScore += self.cellList[sameResourceIndecies[0]].getDotValue() * resource_values[self.cellList[sameResourceIndecies[0]].resource]
                cellScore += self.cellList[sameResourceIndecies[1]].getDotValue() * resource_values[self.cellList[sameResourceIndecies[1]].resource] * DOUBLE_R_DIM
            else:
                cellScore += self.cellList[sameResourceIndecies[1]].getDotValue() * resource_values[self.cellList[sameResourceIndecies[1]].resource]
                cellScore += self.cellList[sameResourceIndecies[0]].getDotValue() * resource_values[self.cellList[sameResourceIndecies[0]].resource] * DOUBLE_R_DIM
            lastIdx = 3 - (sameResourceIndecies[0] + sameResourceIndecies[1])

            if (len(self.cellList) == 3):
                cellScore == self.cellList[lastIdx].getDotValue() * resource_values[self.cellList[lastIdx].resource]
        # 3 cells have the same resource
        elif (len(sameResourceIndecies) == 3):
            if (self.cellList[0].roll >= self.cellList[1].roll and self.cellList[0].roll >= self.cellList[2].roll):
                cellScore += self.cellList[0].getDotValue() * resource_values[self.cellList[0].resource]
                if (self.cellList[1].roll >= self.cellList[2].roll):
                    cellScore += self.cellList[1].getDotValue() * resource_values[self.cellList[1].resource] * DOUBLE_R_DIM
                    cellScore += self.cellList[2].getDotValue() * resource_values[self.cellList[2].resource] * TRIPLE_R_DIM
                else:
                    cellScore += self.cellList[2].getDotValue() * resource_values[self.cellList[2].resource] * DOUBLE_R_DIM
                    cellScore += self.cellList[1].getDotValue() * resource_values[self.cellList[1].resource] * TRIPLE_R_DIM
            elif (self.cellList[1].roll >= self.cellList[0].roll and self.cellList[1].roll >= self.cellList[2].roll):
                cellScore += self.cellList[1].getDotValue() * resource_values[self.cellList[1].resource]
                if (self.cellList[0].roll >= self.cellList[2].roll):
                    cellScore += self.cellList[0].getDotValue() * resource_values[self.cellList[0].resource] * DOUBLE_R_DIM
                    cellScore += self.cellList[2].getDotValue() * resource_values[self.cellList[2].resource] * TRIPLE_R_DIM
                else:
                    cellScore += self.cellList[2].getDotValue() * resource_values[self.cellList[2].resource] * DOUBLE_R_DIM
                    cellScore += self.cellList[0].getDotValue() * resource_values[self.cellList[0].resource] * TRIPLE_R_DIM
            else:
                cellScore += self.cellList[2].getDotValue() * resource_values[self.cellList[2].resource]
                if (self.cellList[0].roll >= self.cellList[1].roll):
                    cellScore += self.cellList[0].getDotValue() * resource_values[self.cellList[0].resource] * DOUBLE_R_DIM
                    cellScore += self.cellList[1].getDotValue() * resource_values[self.cellList[1].resource] * TRIPLE_R_DIM
                else:
                    cellScore += self.cellList[1].getDotValue() * resource_values[self.cellList[1].resource] * DOUBLE_R_DIM
                    cellScore += self.cellList[0].getDotValue() * resource_values[self.cellList[0].resource] * TRIPLE_R_DIM
        # no cells have the same resource
        else:
            for cell in self.cellList:
                cellScore += cell.getDotValue() * resource_values[cell.resource]

        # if the node has a port
        if (self.port is not None):
            cellScore += PORT_INCREASE
            # if the port's resource matches one of the cell's resources
            for cell in self.cellList:
                if (self.port == cell.resource):
                    cellScore += SAME_RESOURCE_BONUS

        return cellScore
    # End of calcCellScore()
    
    def __str__(self)->str:
        return f"Node: {str(self.nodeNum)}]"
    
    def printCells(self)->str:
        text = ""
        for i in range(len(self.cellList)):
            text = f"{text}({str(self.cellList[i])})"
            if (i < len(self.cellList) - 1):
                text = f"{text}; "

        return text

    # returns a list of the indecies with the same resource
    def getSameResourceIndecies(self)->list:
        indecies = []
        if (len(self.cellList) <= 1):
            return indecies
        
        if (len(self.cellList) == 3):
            if (self.cellList[0].resource == self.cellList[1].resource):
                indecies.append(0)
                indecies.append(1)
                if (self.cellList[0].resource == self.cellList[2].resource):
                    indecies.append(2)
            elif (self.cellList[0].resource == self.cellList[2].resource):
                indecies.append(1)
                indecies.append(2)
        elif (self.cellList[0].resource == self.cellList[1].resource):
            indecies.append(0)
            indecies.append(1)

        return indecies
    
# End of Node class

nodeList = []
NODE_NUM = 54

# Initializes all Nodes
def initializeNodes()->None:
    global nodeList
    for i in range(NODE_NUM):
        nodeList.append(Node())

# Finds two Nodes with the best scores
def findTwoBest()->list:
    twoBest = []

    # sorts the first two nodes into twoBest
    if (nodeList[0].calcCellScore() >= nodeList[1].calcCellScore()):
        twoBest.append(nodeList[0])
        twoBest.append(nodeList[1])
    else:
        twoBest.append(nodeList[1])
        twoBest.append(nodeList[0])

    # finds the two best scores in the rest of nodeList
    for i in range(2, NODE_NUM):
        betterThanIdx0 = nodeList[i].calcCellScore() > twoBest[0].calcCellScore()
        betterThanIdx1 = nodeList[i].calcCellScore() > twoBest[1].calcCellScore()

        # if the node is better than both best nodes
        if (not(nodeList[i].hasSettlement) and betterThanIdx0 and betterThanIdx1):
            if (twoBest[0].calcCellScore() >= twoBest[1].calcCellScore()):
                twoBest[0] = nodeList[i]
            else:
                twoBest[1] = nodeList[i]
        # if the node is better than the first best
        elif (betterThanIdx0):
            twoBest[0] = nodeList[i]
        # if the node is better than the second best
        elif (betterThanIdx1):
            twoBest[1] = nodeList[i]

    return twoBest

def rankNodes()->dict:
    rankedDict = {}

    for node in nodeList:
        rankedDict[str(node)] = node.calcCellScore()

    return rankedDict

cellGrid = initializeCells(DEF_CELL_DATA)
# in clockwise order
nodesWithPorts = {2:"3:1", 3:"3:1",
                  5:"3:1", 6:"3:1",
                  15:"wheat", 25:"wheat",
                  36:"wood", 46:"wood",
                  52:"3:1", 53:"3:1",
                  50:"sheep", 49:"sheep",
                  48:"3:1", 47:"3:1",
                  38:"brick", 28:"brick",
                  17:"ore", 7:"ore"}

# Hardcoded values for every Node objects cellList
cellListDict = {# row 1
    "n0":[cellGrid[0][0]],
    "n1":[cellGrid[0][0]],
    "n2":[cellGrid[0][0], cellGrid[0][1]],
    "n3":[cellGrid[0][1]],
    "n4":[cellGrid[0][1], cellGrid[0][2]],
    "n5":[cellGrid[0][2]],
    "n6":[cellGrid[0][2]],
    # row 2
    "n7":[cellGrid[1][0]],
    "n8":[cellGrid[0][0], cellGrid[1][0]],
    "n9":[cellGrid[0][0], cellGrid[1][0], cellGrid[1][1]],
    "n10":[cellGrid[0][0], cellGrid[0][1], cellGrid[1][1]],
    "n11":[cellGrid[0][1], cellGrid[1][1], cellGrid[1][2]],
    "n12":[cellGrid[0][1], cellGrid[0][2], cellGrid[1][2]],
    "n13":[cellGrid[0][2], cellGrid[1][2], cellGrid[1][3]],
    "n14":[cellGrid[0][2], cellGrid[1][3]],
    "n15":[cellGrid[1][3]],
    # row 3
    "n16":[cellGrid[2][0]],
    "n17":[cellGrid[1][0], cellGrid[2][0]],
    "n18":[cellGrid[1][0], cellGrid[2][0], cellGrid[2][1]],
    "n19":[cellGrid[1][0], cellGrid[1][1], cellGrid[2][1]],
    "n20":[cellGrid[1][1], cellGrid[2][1], cellGrid[2][2]],
    "n21":[cellGrid[1][1], cellGrid[1][2], cellGrid[2][3]],
    "n22":[cellGrid[1][2], cellGrid[2][2], cellGrid[2][3]],
    "n23":[cellGrid[1][2], cellGrid[1][3], cellGrid[2][3]],
    "n24":[cellGrid[1][3], cellGrid[2][3], cellGrid[2][4]],
    "n25":[cellGrid[1][3], cellGrid[2][4]],
    "n26":[cellGrid[2][4]],
    # row 4
    "n27":[cellGrid[2][0]],
    "n28":[cellGrid[2][0], cellGrid[3][0]],
    "n29":[cellGrid[2][0], cellGrid[2][1], cellGrid[3][0]],
    "n30":[cellGrid[2][1], cellGrid[3][0], cellGrid[3][1]],
    "n31":[cellGrid[2][1], cellGrid[2][2], cellGrid[3][1]],
    "n32":[cellGrid[2][3], cellGrid[3][1], cellGrid[3][2]],
    "n33":[cellGrid[2][2], cellGrid[2][3], cellGrid[3][2]],
    "n34":[cellGrid[2][3], cellGrid[3][2], cellGrid[3][3]],
    "n35":[cellGrid[2][3], cellGrid[2][4], cellGrid[3][3]],
    "n36":[cellGrid[2][4], cellGrid[3][3]],
    "n37":[cellGrid[2][4]],
    # row 5
    "n38":[cellGrid[3][0]],
    "n39":[cellGrid[3][0], cellGrid[4][0]],
    "n40":[cellGrid[3][0], cellGrid[3][1], cellGrid[4][0]],
    "n41":[cellGrid[3][1], cellGrid[4][0], cellGrid[4][1]],
    "n42":[cellGrid[3][1], cellGrid[3][2], cellGrid[4][1]],
    "n43":[cellGrid[3][2], cellGrid[4][1], cellGrid[4][2]],
    "n44":[cellGrid[3][2], cellGrid[3][3], cellGrid[4][2]],
    "n45":[cellGrid[4][2], cellGrid[3][3]],
    "n46":[cellGrid[3][3]],
    # row 6
    "n47":[cellGrid[4][0]],
    "n48":[cellGrid[4][0]],
    "n49":[cellGrid[4][0], cellGrid[4][1]],
    "n50":[cellGrid[4][1]],
    "n51":[cellGrid[4][1], cellGrid[4][2]],
    "n52":[cellGrid[4][2]],
    "n53":[cellGrid[4][2]],
}

def printCellGrid()->None:
    for row in cellGrid:
        for cell in row:
            print(str(cell))


printCellGrid()
initializeNodes()
print(rankNodes())
result = findTwoBest()
print(str(result[0]))
print(str(result[1]))








