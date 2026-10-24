#!/usr/bin/env python3
"""Analyze a Lichess user's games by speed, color, opening, and loss ending."""

import argparse
import csv
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import chess.pgn
import requests

BASE_URL = "https://lichess.org/api/games/user/{username}"
SPEEDS = ("bullet", "blitz", "rapid", "classical")


def opening_name(game):
    headers = game.headers
    return headers.get("Opening") or headers.get("ECO") or "Opening not tagged"


def loss_category(game):
    termination = game.headers.get("Termination", "").lower()

    if "time" in termination or "forfeit" in termination:
        return "Lost on time"
    if game.end().board().is_checkmate():
        return "Checkmated"
    if termination == "normal":
        return "Resigned / other normal decisive finish"
    return game.headers.get("Termination") or "Termination not tagged"


def fetch_games(username, speed, limit):
    params = {
        "max": limit,
        "rated": "true",
        "perfType": speed,
        "opening": "true",
        "clocks": "true",
    }
    headers = {
        "Accept": "application/x-chess-pgn",
        "User-Agent": "LichessReport/1.0 (personal chess analysis script)",
    }

    response = requests.get(
        BASE_URL.format(username=username),
        params=params,
        headers=headers,
        timeout=60,
    )

    if response.status_code == 404:
        raise RuntimeError(
            f"User '{username}' was not found. Check the spelling."
        )
    response.raise_for_status()
    return response.text


def analyze(username, speeds, limit):
    # stats[speed][color][opening] = W/D/L counter
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    endings = defaultdict(Counter)
    game_counts = Counter()

    for speed in speeds:
        pgn = io.StringIO(fetch_games(username, speed, limit))

        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            headers = game.headers
            player = username.lower()

            if headers.get("White", "").lower() == player:
                color = "White"
                outcome = {
                    "1-0": "W",
                    "0-1": "L",
                    "1/2-1/2": "D",
                }.get(headers.get("Result"))
            elif headers.get("Black", "").lower() == player:
                color = "Black"
                outcome = {
                    "0-1": "W",
                    "1-0": "L",
                    "1/2-1/2": "D",
                }.get(headers.get("Result"))
            else:
                continue

            if outcome is None:
                continue

            game_counts[speed] += 1
            stats[speed][color][opening_name(game)][outcome] += 1

            if outcome == "L":
                endings[speed][loss_category(game)] += 1

    return stats, endings, game_counts


def make_report(username, speeds, stats, endings, game_counts, min_games):
    report = {
        "username": username,
        "games_analyzed": dict(game_counts),
        "minimum_games_for_lowest_score_list": min_games,
        "openings": [],
        "loss_endings": [],
    }

    for speed in speeds:
        for color in ("White", "Black"):
            for opening, counts in stats[speed][color].items():
                wins, draws, losses = counts["W"], counts["D"], counts["L"]
                games = wins + draws + losses
                report["openings"].append({
                    "speed": speed,
                    "color": color,
                    "opening": opening,
                    "games": games,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "loss_percent": round(100 * losses / games, 1),
                    "score_percent": round(
                        100 * (wins + 0.5 * draws) / games, 1
                    ),
                })

        for category, count in endings[speed].items():
            report["loss_endings"].append({
                "speed": speed,
                "category": category,
                "losses": count,
            })

    return report


def print_markdown(report, min_games):
    print(f"# Lichess report: {report['username']}\n")

    for speed, count in report["games_analyzed"].items():
        print(f"## {speed.title()} — {count} games\n")

        for color in ("White", "Black"):
            rows = [
                row for row in report["openings"]
                if row["speed"] == speed and row["color"] == color
            ]
            rows.sort(key=lambda row: row["games"], reverse=True)

            print(f"### {color}\n")
            print("| Games | W-D-L | Score | Opening |")
            print("|---:|:---:|---:|:---|")
            for row in rows[:15]:
                print(
                    f"| {row['games']} | "
                    f"{row['wins']}-{row['draws']}-{row['losses']} | "
                    f"{row['score_percent']:.1f}% | {row['opening']} |"
                )

            low = [
                row for row in rows if row["games"] >= min_games
            ]
            low.sort(key=lambda row: row["score_percent"])
            if low:
                print(f"\nLowest scores (minimum {min_games} games):")
                for row in low[:5]:
                    print(
                        f"- {row['opening']}: {row['score_percent']:.1f}% "
                        f"from {row['games']} games "
                        f"({row['wins']}-{row['draws']}-{row['losses']})"
                    )
            print()

        speed_endings = [
            row for row in report["loss_endings"] if row["speed"] == speed
        ]
        print("Loss endings:")
        if speed_endings:
            for row in sorted(
                speed_endings, key=lambda item: item["losses"], reverse=True
            ):
                print(f"- {row['category']}: {row['losses']}")
        else:
            print("- No losses recorded.")
        print()


def write_csv(report, path):
    fields = [
        "record_type", "speed", "color", "opening", "games",
        "wins", "draws", "losses", "loss_percent", "score_percent",
        "category",
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in report["openings"]:
            writer.writerow({"record_type": "opening", **row})

        for row in report["loss_endings"]:
            writer.writerow({"record_type": "loss_ending", **row})


def main():
    parser = argparse.ArgumentParser(
        description="Analyze rated Lichess games by speed, opening, and loss ending."
    )
    parser.add_argument("username", help="Lichess username")
    parser.add_argument(
        "--perf",
        choices=(*SPEEDS, "all"),
        default="all",
        help="Speed to analyze (default: all four supported speeds)",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=500,
        help="Maximum games to fetch per speed (default: 500)",
    )
    parser.add_argument(
        "--min-games",
        type=int,
        default=10,
        help="Minimum opening sample size for lowest-score summaries",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json", "csv"),
        default="markdown",
        help="Report format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        help="Optional output filename; otherwise prints to the terminal",
    )
    args = parser.parse_args()

    if args.games < 1 or args.min_games < 1:
        parser.error("--games and --min-games must be positive")

    speeds = SPEEDS if args.perf == "all" else (args.perf,)

    try:
        stats, endings, game_counts = analyze(
            args.username, speeds, args.games
        )
    except (requests.RequestException, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    report = make_report(
        args.username, speeds, stats, endings, game_counts, args.min_games
    )

    if args.format == "json":
        output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    elif args.format == "csv":
        if not args.output:
            parser.error("CSV output requires --output, e.g. --output report.csv")
        write_csv(report, Path(args.output))
        print(f"CSV report written to {args.output}")
    else:
        if args.output:
            # Capture Markdown output so it can be saved to a file.
            from contextlib import redirect_stdout

            with Path(args.output).open("w", encoding="utf-8") as file:
                with redirect_stdout(file):
                    print_markdown(report, args.min_games)
            print(f"Markdown report written to {args.output}")
        else:
            print_markdown(report, args.min_games)


if __name__ == "__main__":
    main()
