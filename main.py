import curses
import math
import random
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
HIGH_SCORE_FILE = BASE_DIR / "highscore.txt"
TEXTS_FILE = BASE_DIR / "texts.txt"
FALLBACK_TEXT = (
    "Python programming is an amazing way to build tools, automate tasks, "
    "and create fun applications like this command line typing test."
)
MIN_HEIGHT = 8
MIN_WIDTH = 30


def load_high_score():
    try:
        parts = HIGH_SCORE_FILE.read_text(encoding="utf-8").strip().split(",")
        best_wpm, best_accuracy = map(float, parts)
    except FileNotFoundError:
        return 0.0, 0.0
    except (ValueError, OSError):
        return 0.0, 0.0

    if not math.isfinite(best_wpm) or not math.isfinite(best_accuracy):
        return 0.0, 0.0
    return max(best_wpm, 0.0), max(best_accuracy, 0.0)


def save_high_score(wpm, accuracy):
    best_wpm, best_accuracy = load_high_score()
    if wpm > best_wpm or (wpm == best_wpm and accuracy > best_accuracy):
        HIGH_SCORE_FILE.write_text(f"{wpm},{accuracy}", encoding="utf-8")
        return True
    return False


def load_text_from_file():
    try:
        lines = TEXTS_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return FALLBACK_TEXT

    usable_lines = [
        " ".join(line.split())
        for line in lines
        if line.strip() and all(char.isascii() and char.isprintable() for char in line)
    ]
    return random.choice(usable_lines) if usable_lines else FALLBACK_TEXT


def draw_text(stdscr, row, col, text, attr=0):
    max_y, max_x = stdscr.getmaxyx()
    if row < 0 or row >= max_y or col < 0 or col >= max_x - 1:
        return

    available = max_x - col - 1
    if available:
        stdscr.addnstr(row, col, str(text), available, attr)


def color_pair(pair_number):
    return curses.color_pair(pair_number) if curses.has_colors() else 0


def start_screen(stdscr):
    stdscr.timeout(-1)
    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        if max_y < 5 or max_x < 20:
            draw_text(stdscr, 0, 0, "Resize terminal to at least 20x5.")
        else:
            draw_text(stdscr, 0, 0, "Welcome to the Python WPM Typing Test!", curses.A_BOLD)
            draw_text(stdscr, 1, 0, "Type the prompt as quickly and accurately as possible.")
            draw_text(stdscr, 3, 0, "Press any key to begin.")
        stdscr.refresh()

        key = stdscr.get_wch()
        if key == curses.KEY_RESIZE:
            continue
        if max_y >= 5 and max_x >= 20:
            return


def display_text(stdscr, target, current, wpm, accuracy):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    if max_y < MIN_HEIGHT or max_x < MIN_WIDTH:
        draw_text(
            stdscr,
            0,
            0,
            f"Terminal too small ({max_y}x{max_x}); resize to at least "
            f"{MIN_HEIGHT}x{MIN_WIDTH}.",
        )
        stdscr.refresh()
        return False

    draw_text(stdscr, 0, 0, f"WPM: {wpm:.1f} | Accuracy: {accuracy:.1f}%", curses.A_BOLD)
    draw_text(stdscr, 2, 0, "Target text:", curses.A_DIM)

    body_top = 4
    body_rows = max_y - body_top - 1
    columns = max_x - 1
    current_position = min(len(current), max(len(target) - 1, 0))
    cursor_row = current_position // columns
    first_row = max(0, cursor_row - body_rows + 1)
    last_row = first_row + body_rows

    for line_number in range(first_row, last_row):
        start = line_number * columns
        if start >= len(target):
            break
        screen_row = body_top + line_number - first_row
        for column, char in enumerate(target[start : start + columns]):
            index = start + column
            if index >= len(current):
                color = color_pair(3)
            elif current[index] == char:
                color = color_pair(1)
            else:
                color = color_pair(2)
            stdscr.addch(screen_row, column, char, color)

    draw_text(stdscr, max_y - 1, 0, "Type the text above. Backspace corrects; ESC quits.")
    stdscr.refresh()
    return True


def display_result(stdscr, wpm, accuracy, best_wpm, is_new_high, save_error=None):
    stdscr.timeout(-1)
    while True:
        stdscr.erase()
        max_y, _ = stdscr.getmaxyx()
        draw_text(stdscr, 0, 0, "Test complete!", curses.A_BOLD)
        draw_text(stdscr, 2, 0, f"Final speed: {wpm:.1f} WPM")
        draw_text(stdscr, 3, 0, f"Accuracy: {accuracy:.1f}%")
        if is_new_high:
            draw_text(stdscr, 5, 0, "New personal best!", curses.A_BOLD)
        else:
            draw_text(stdscr, 5, 0, f"Personal best: {best_wpm:.1f} WPM")
        if save_error:
            draw_text(stdscr, 6, 0, f"Could not save high score: {save_error}")
        draw_text(stdscr, max_y - 1, 0, "Any key replays; ESC quits.")
        stdscr.refresh()

        key = stdscr.get_wch()
        if key == curses.KEY_RESIZE:
            continue
        return key not in ("\x1b", 27)


def wpm_test(stdscr):
    stdscr.timeout(50)
    while True:
        target_text = load_text_from_file()
        current_text = []
        start_time = None

        while True:
            elapsed = time.monotonic() - start_time if start_time is not None else 0.0
            wpm = (len(current_text) / 5) / (elapsed / 60) if elapsed > 0 else 0.0
            correct_chars = sum(
                typed == expected
                for typed, expected in zip(current_text, target_text)
            )
            accuracy = correct_chars / len(current_text) * 100 if current_text else 100.0

            terminal_ready = display_text(stdscr, target_text, current_text, wpm, accuracy)
            try:
                key = stdscr.get_wch()
            except curses.error:
                continue

            if key == curses.KEY_RESIZE:
                continue
            if key in ("\x1b", 27):
                return
            if not terminal_ready:
                continue

            if key in (curses.KEY_BACKSPACE, "\b", "\x7f", "\x08"):
                if current_text:
                    current_text.pop()
                continue

            if isinstance(key, str) and len(key) == 1 and key.isascii() and key.isprintable():
                if start_time is None:
                    start_time = time.monotonic()
                if len(current_text) < len(target_text):
                    current_text.append(key)

            if len(current_text) == len(target_text):
                elapsed = max(time.monotonic() - start_time, 0.001)
                wpm = (len(current_text) / 5) / (elapsed / 60)
                correct_chars = sum(
                    typed == expected
                    for typed, expected in zip(current_text, target_text)
                )
                accuracy = correct_chars / len(current_text) * 100
                best_wpm, _ = load_high_score()
                save_error = None
                try:
                    is_new_high = save_high_score(wpm, accuracy)
                except OSError as error:
                    is_new_high = False
                    save_error = str(error)
                if not display_result(
                    stdscr,
                    wpm,
                    accuracy,
                    wpm if is_new_high else best_wpm,
                    is_new_high,
                    save_error,
                ):
                    return
                stdscr.timeout(50)
                break


def main(stdscr):
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    start_screen(stdscr)
    wpm_test(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
