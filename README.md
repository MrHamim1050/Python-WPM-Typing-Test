# Python WPM Typing Test

A command-line tool written in Python that measures your typing speed and calculates your Words Per Minute (WPM). It utilizes the curses module to provide an enhanced terminal interface, live color-coded feedback, scrolling prompts, and high-score persistence.

## Features

- **Real-Time WPM & Accuracy:** Measures your typing speed and error rate live as you type.
- **Scrolling Prompts:** Automatically handles prompts of any length with smooth line-wrapping and terminal boundary safety.
- **Terminal Resize Handling:** Pauses gracefully if the window is resized below minimum usable dimensions.
- **High Score Tracking:** Saves your personal best speed and accuracy to a local file.
- **Input Safety:** Strictly filters input to accept printable characters while properly handling Backspace and ESC exits.


## Prerequisites
- Python 3.x
- *(Note: `curses` comes built-in with Python on Linux/macOS. If you are on Windows, you will need to install the Windows-compatible curses wrapper)*:
  ```bash
  pip install windows-curses


## How to Run

1. Clone the repository and navigate into the folder:
   ```bash
   git clone https://github.com/MrHamim1050/Python-WPM-Typing-Test.git 
   
   cd Python-WPM-Typing-Test

2) Run the script:
 ```bash
python main.py

