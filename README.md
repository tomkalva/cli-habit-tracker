# cli-habit-tracker
This is my first personal project. A command-line habit tracker with streaks, weekly progress, and SQLite persistence.

---

## Features

- Add and remove habits
- Mark habits as completed each day
- View today's completion status
- Track streaks for each habit
- Streaks are calculated based on consecutive daily completions
- Weekly overview (7-day view)
- Data is stored locally in habits.db

---

## Requirements

- Python 3.10+
- No external dependencies

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/tomkalva/cli-habit-tracker.git
cd cli-habit-tracker
```

### 2. Run the program
```bash
python3 main.py
```
### 3. Usage Examples

#### Add a habit
```bash
python3 main.py add <habit_name>
```
#### List habits
```bash
python3 main.py list
```
#### Mark habit as done
```bash
python3 main.py done <habit_id>
```
#### View today’s status
```bash
python3 main.py today
```
#### View weekly progress
```bash
python3 main.py week
```
