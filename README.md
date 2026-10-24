
# ♟️ Lichess Game Report

A Python tool for analyzing a Lichess user's rated games by time control, color, opening, results, and loss-ending category.

Generate Markdown, JSON, or CSV reports to better understand your chess statistics and identify openings that may need more attention.

## ✨ Features

- **Multiple time controls:** Bullet, Blitz, Rapid, and Classical.
- **Opening statistics:** Games played, wins, draws, losses, and score percentage.
- **Color analysis:** Compare opening performance as White and Black.
- **Loss-ending analysis:** Categorizes losses by time, checkmate, and other recorded endings.
- **Lowest-scoring openings:** Highlights openings with low scores and sufficient game samples.
- **Multiple export formats:** Markdown, JSON, and CSV.
- **Configurable analysis:** Choose the time control, game limit, and minimum opening sample size.
- **Lichess API integration:** Fetches rated games without requiring a password or API token.

## 🛠️ Requirements

- Python 3.10 or newer recommended
- An internet connection
- A public Lichess username

## 📦 Installation

### 1. Clone the repository

Replace the URL below with your actual repository URL if necessary.

```bash
git clone https://github.com/AprameyKulkarni13/lichess-game-report.git
cd lichess-game-report
```

### 2. Create a virtual environment (recommended)

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 🚀 Usage

Analyze all supported time controls:

```bash
python lichess_report.py Aprameylovestoplay
```

Analyze Bullet games only:

```bash
python lichess_report.py Aprameylovestoplay --perf bullet --games 500
```

By default, the script analyzes up to 500 games per supported time control and prints a Markdown report in the terminal.

## ⚙️ Command-Line Options

| Option | Description | Default |
|---|---|---|
| `username` | Lichess username to analyze | Required |
| `--perf` | `bullet`, `blitz`, `rapid`, `classical`, or `all` | `all` |
| `--games` | Maximum games fetched per time control | `500` |
| `--min-games` | Minimum games required for lowest-score summaries | `10` |
| `--format` | `markdown`, `json`, or `csv` | `markdown` |
| `--output` | File in which to save the report | Terminal output |

## 📊 Examples

### Analyze all supported time controls

```bash
python lichess_report.py Aprameylovestoplay --perf all --games 500
```

### Analyze Bullet games

```bash
python lichess_report.py Aprameylovestoplay --perf bullet --games 500
```

### Analyze Blitz games

```bash
python lichess_report.py Aprameylovestoplay --perf blitz --games 300
```

### Export Bullet statistics to JSON

```bash
python lichess_report.py Aprameylovestoplay --perf bullet --format json --output bullet.json
```

### Export all supported time controls to CSV

```bash
python lichess_report.py Aprameylovestoplay --perf all --format csv --output report.csv
```

### Save a Markdown report

```bash
python lichess_report.py Aprameylovestoplay --perf all --output report.md
```

### Increase the minimum opening sample size

```bash
python lichess_report.py Aprameylovestoplay --perf rapid --min-games 20
```

### Analyze up to 1,000 games per time control

```bash
python lichess_report.py Aprameylovestoplay --perf all --games 1000
```

**Note:** `--games` is the maximum for each selected time control, not the combined total.

## 📈 Understanding the Results

### Opening statistics

Each opening entry includes:

- **Games:** Number of games played with that opening and color.
- **W-D-L:** Wins, draws, and losses from your perspective.
- **Score percentage:** Percentage of available points earned.
- **Loss percentage:** Percentage of games lost.

The score is calculated using:

```text
Score % = (Wins + 0.5 × Draws) / Games × 100
```

For example, 6 wins, 2 draws, and 2 losses produce a score of 70%.

### Lowest-scoring openings

The report identifies openings with the lowest scores among those meeting the configured minimum game count.

A low score does not necessarily mean an opening is objectively bad. Opponent strength, playing style, and sample size can all affect the results.

### Loss endings

Losses are grouped into categories such as:

- Lost on time
- Checkmated
- Resigned / other normal decisive finish
- Other recorded termination categories

Classification depends on the PGN termination metadata and final board position.

## 📁 Project Structure

```text
lichess-game-report/
├── lichess_report.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## 📚 Dependencies

- [python-chess](https://python-chess.readthedocs.io/) — reads and processes chess games in PGN format.
- [requests](https://requests.readthedocs.io/) — retrieves games through the Lichess API.

## ⚠️ Limitations

- Only rated games are requested.
- The number of games analyzed is limited by `--games` for each time control.
- Opening statistics describe historical results and do not prove that an opening caused a particular outcome.
- Small samples can produce misleading percentages.
- Loss-ending classification depends on the information recorded in PGN files.
- A normal decisive finish does not necessarily mean the player resigned.
- The script does not use a chess engine to identify blunders or evaluate positions.
- Ultrabullet is not included in the supported time controls.

## 🔒 Privacy

The script uses a Lichess username to retrieve public rated-game data. It does not require a Lichess password or API token.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test your changes.
5. Open a pull request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Apramey Kulkarni**

GitHub: [@AprameyKulkarni13](https://github.com/AprameyKulkarni13)

---

Made for chess players who want to understand their statistics and improve their preparation. ♟️
