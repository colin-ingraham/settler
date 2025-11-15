// Catan Board Generator
class CatanBoard {
    constructor(svgId) {
        this.svg = document.getElementById(svgId);
        this.hexSize = 50; // radius of hexagon
        this.centerX = 400;
        this.centerY = 400;
        
        // Standard Catan board layout (3-4-5-4-3 pattern)
        // 0 = sea, 1 = land
        this.boardLayout = [
            // Row 0 (top): 3 sea tiles
            [0, 0, 0],
            // Row 1: 1 sea, 3 land, 1 sea
            [0, 1, 1, 1, 0],
            // Row 2: 1 sea, 4 land, 1 sea
            [0, 1, 1, 1, 1, 0],
            // Row 3 (middle): 1 sea, 4 land, 1 sea
            [0, 1, 1, 1, 1, 0],
            // Row 4: 1 sea, 3 land, 1 sea
            [0, 1, 1, 1, 0],
            // Row 5 (bottom): 3 sea tiles
            [0, 0, 0]
        ];
        
        this.init();
    }
    
    init() {
        this.generateBoard();
    }
    
    // Calculate hexagon points
    getHexagonPoints(cx, cy, size) {
        const points = [];
        for (let i = 0; i < 6; i++) {
            const angle = (Math.PI / 3) * i - Math.PI / 6;
            const x = cx + size * Math.cos(angle);
            const y = cy + size * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        return points.join(' ');
    }
    
    // Calculate hex position based on row and column
    getHexPosition(row, col) {
        const hexWidth = this.hexSize * Math.sqrt(3);
        const hexHeight = this.hexSize * 2;
        
        // Offset for centering
        const rowCount = this.boardLayout.length;
        const maxCols = Math.max(...this.boardLayout.map(r => r.length));
        
        // Calculate x position
        let x = this.centerX + (col - this.boardLayout[row].length / 2) * hexWidth;
        
        // Calculate y position
        let y = this.centerY + (row - rowCount / 2) * hexHeight * 0.75;
        
        return { x, y };
    }
    
    // Generate the entire board
    generateBoard() {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('id', 'board-group');
        
        // Generate hexagons
        this.boardLayout.forEach((row, rowIndex) => {
            row.forEach((tileType, colIndex) => {
                const pos = this.getHexPosition(rowIndex, colIndex);
                this.createHexagon(group, pos.x, pos.y, tileType, rowIndex, colIndex);
            });
        });
        
        this.svg.appendChild(group);
    }
    
    // Create a single hexagon
    createHexagon(parent, x, y, tileType, row, col) {
        const hexGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        hexGroup.setAttribute('class', 'hex-group');
        hexGroup.setAttribute('data-row', row);
        hexGroup.setAttribute('data-col', col);
        hexGroup.setAttribute('data-type', tileType === 1 ? 'land' : 'sea');
        
        // Create hexagon polygon
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', this.getHexagonPoints(x, y, this.hexSize));
        polygon.setAttribute('class', tileType === 1 ? 'hex-land' : 'hex-sea');
        
        hexGroup.appendChild(polygon);
        
        // Add visual elements for land tiles (will be used for resources later)
        if (tileType === 1) {
            // Placeholder for future resource icon
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', x);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', this.hexSize * 0.4);
            circle.setAttribute('class', 'number-token');
            circle.setAttribute('fill', '#f9f4e8');
            circle.setAttribute('opacity', '0.3');
            hexGroup.appendChild(circle);
        }
        
        // Add harbor indicators for certain sea tiles (visual markers only)
        if (tileType === 0 && this.isHarborPosition(row, col)) {
            const harborCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            harborCircle.setAttribute('cx', x);
            harborCircle.setAttribute('cy', y);
            harborCircle.setAttribute('r', 8);
            harborCircle.setAttribute('class', 'harbor-indicator');
            hexGroup.appendChild(harborCircle);
        }
        
        parent.appendChild(hexGroup);
    }
    
    // Determine if a sea position should have a harbor
    isHarborPosition(row, col) {
        // Standard harbor positions in Catan
        const harborPositions = [
            [0, 1], // Top row
            [1, 0], [1, 4], // Second row
            [2, 0], [2, 5], // Third row
            [3, 0], [3, 5], // Fourth row
            [4, 0], [4, 4], // Fifth row
            [5, 1]  // Bottom row
        ];
        
        return harborPositions.some(([r, c]) => r === row && c === col);
    }
}