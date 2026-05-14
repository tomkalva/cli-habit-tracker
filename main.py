import argparse
import sqlite3
import datetime


parser = argparse.ArgumentParser(
    prog="habit",
    description="A simple CLI habit tracker",
    formatter_class=argparse.RawTextHelpFormatter
)

subparsers = parser.add_subparsers(dest="command")

add_parser = subparsers.add_parser("add",
    help="Add a new habit",
    description="Creates a new habit in your tracker"
)
add_parser.add_argument("habit")


remove_parser = subparsers.add_parser("remove",
    help="Remove a habit",
    description="Removes a habit from your tracker"
)
remove_parser.add_argument("id", type=int)


done_parser = subparsers.add_parser("done",
    help="Mark habit as done",
    description="Marks a habit as done for today"
)
done_parser.add_argument("id", type=int)


list_parser = subparsers.add_parser("list",
    help="List all habits",
    description="Lists all your habits and their ID's"
)

today_parser = subparsers.add_parser("today",
    help="Show today's completion status",
    description="Displays all habits grouped into done and not done for today"
)

done_parser = subparsers.add_parser("streak",
    help="Mark habit as done",
    description="Marks a habit as done for today"
)
done_parser.add_argument("id", type=int)


parser.epilog = """
Examples:
  main.py add exercise
  main.py remove 3
  main.py done 2
  main.py list
  main.py today
"""

args = parser.parse_args()





connection = sqlite3.connect("habits.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS completions (
    habit_id INTEGER,
    date TEXT,
    UNIQUE(habit_id, date)
)
""")


def calculate_streak(done_dates):
    streak = 0
    current_day = datetime.date.today()

    while True:
        day_str = current_day.isoformat()

        if day_str in done_dates:
            streak += 1
            current_day -= datetime.timedelta(days=1)
        else:
            break
    
    return streak


if args.command is None:
    parser.print_help()
    exit()


elif args.command == "add":
    cursor.execute(
        "SELECT 1 FROM habits WHERE name = ?",
        (args.habit,)
    )
    exists = cursor.fetchone()

    if exists:
        print("Habit already exists")
    else:
        cursor.execute(
            "INSERT INTO habits (name) VALUES (?)",
            (args.habit,)
        )
        connection.commit()
        print(f"Added {args.habit}")



elif args.command == "remove":
    cursor.execute(
        "SELECT 1 FROM habits WHERE id = ?",
        (args.id,)
    )

    exists = cursor.fetchone()

    if exists:
        cursor.execute(
            "DELETE FROM habits WHERE id = ?",
            (args.id,)
        )
        connection.commit()
        print(f"Removed habit {args.id}")
    else:
        print("Habit not found")
        
        

elif args.command == "list":
    cursor.execute("SELECT * FROM habits ORDER BY id")
    rows = cursor.fetchall()
    if not rows:
        print("No habits yet.\nTry: add <your habit>")
    else:
        print("ID  | HABIT")
        print("------------")

        for id, name in rows:
            print(f"{id:>2}  | {name}")


elif args.command == "today":
    cursor.execute("SELECT * FROM habits ORDER BY id")
    all_habits = cursor.fetchall()

    if not all_habits:
        print("No habits yet.\nTry: add <your habit>")
    else:
        today_date = datetime.date.today().isoformat()

        cursor.execute(
            "SELECT habit_id FROM completions WHERE date = ?",
            (today_date,)
        )
        completed_habits = cursor.fetchall()

        completed_ids = {row[0] for row in completed_habits}

        done_today = []
        not_done_today = []

        for habit_id, name in all_habits:
            if habit_id in completed_ids:
                done_today.append((habit_id, name))
            else:
                not_done_today.append((habit_id, name))

        print("Done today:")
        for id, name in done_today:
            print(f"{id:>2}  | {name}")

        print("\nNot done today:")
        for id, name in not_done_today:
            print(f"{id:>2}  | {name}")



elif args.command == "done":
    cursor.execute(
        "SELECT 1 FROM habits WHERE id = ?",
        (args.id,)
    )
    exists = cursor.fetchone()

    if exists:
        try:
            today_date = datetime.date.today().isoformat()
            cursor.execute(
                "INSERT INTO completions (habit_id, date) VALUES (?, ?)",
                (args.id, today_date)
            )
            connection.commit()
            print(f"Marked habit {args.id} as done")
        except sqlite3.IntegrityError:
            print("Already marked done today")
    else:
        print("Habit not found")



elif args.command == "streak":
    cursor.execute(
    "SELECT date FROM completions WHERE habit_id = ?",
    (args.id,)
    )
    done_dates = {row[0] for row in cursor.fetchall()}

    streak = calculate_streak(done_dates)

    print(f"Current streak: {streak}")



connection.close()