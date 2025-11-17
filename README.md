# Settler - Catan Settlement Placement Tool

An intelligent web application that helps Settlers of Catan players make optimal settlement placement decisions during the initial draft phase.

Can access the project at www.settlerstrategy.com

Created by Colin Ingraham, Josh Schmitt, and Sam Coehlo for GateHacks 2025
## Features

- Interactive board setup with customizable resource placement
- Custom settlement scoring algorithm
- Real-time strategic recommendations
- Visual indicators for optimal placement locations
- Post-draft analysis with production metrics

## Tech Stack

- **Backend:** Django, Python
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Algorithm:** Custom scoring system based on resource probability and diversity

## Local Installation

1. Clone the repository:
```bash
git clone https://github.com/colin-ingraham/settler.git
cd settler
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install django
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

6. Open http://localhost:8000 in your browser

## Usage

1. **Setup Phase:** Click tiles to cycle through resource types or use the randomize button
2. **Number Placement:** Select a starting hex for the number spiral
3. **Draft Phase:** Place settlements based on AI recommendations
4. **Analysis:** Review your strategy and production metrics

## Algorithm

The scoring algorithm considers:
- Resource production probability (based on dice roll odds)
- Resource diversity (access to all 5 resource types)
- Number diversity (avoiding clustering on same numbers)
- Strategic fit based on player's first settlement choice

## Screenshots

<img width="1967" height="1307" alt="image" src="https://github.com/user-attachments/assets/c4266937-03e2-4f8b-9898-71f611ae82f3" />
<img width="1996" height="1100" alt="image" src="https://github.com/user-attachments/assets/5516a799-a300-4bab-b8f3-0d212650e3f5" />


## Future Enhancements

- [ ] Expansion board support
- [ ] Save/load board configurations
- [ ] Multiplayer online drafting
- [ ] Historical game data analysis

## License

MIT License - feel free to use this for your game nights!

## Contributing

Pull requests welcome! Please open an issue first to discuss proposed changes.

---

