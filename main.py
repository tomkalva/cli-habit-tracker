import argparse
import sqlite3
import datetime
from collections import defaultdict



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
list_parser.add_argument("--sort", choices=["streak", "id", "name"])


today_parser = subparsers.add_parser("today",
    help="Show today's completion status",
    description="Displays all habits grouped into done and not done for today"
)

week_parser = subparsers.add_parser("week",
    help="Show habit completion summary for the last 7 days",
    description="Displays how many times each habit was completed during the last 7 days"
)

streak_parser = subparsers.add_parser("streak",
    help="Shows streak for habit",
    description="Shows number of consecutive days this habit has been complete"
)
streak_parser.add_argument("id", type=int)


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


cursor.execute("SELECT habit_id, date FROM completions")
all_completions = cursor.fetchall()
done_map = defaultdict(set)

for habit_id, date in all_completions:
    done_map[habit_id].add(date)



def calculate_streak(done_dates):
    streak = 0
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    today_str = today.isoformat()
    yesterday_str = yesterday.isoformat()

    if today_str in done_dates:
        current_day = today
    elif yesterday_str in done_dates:
        current_day = yesterday
    else:
        return 0
    

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
        cursor.execute("SELECT name FROM habits WHERE id = ?", (args.id,))
        name = cursor.fetchone()[0]
        confirm = input(f'Are you sure you want to delete "{name}"? (y/N): ')

        if confirm.lower() not in ("y", "yes"):
            print("Cancelled")
            exit()
        
        else:
            cursor.execute("DELETE FROM completions WHERE habit_id = ?", (args.id,))
            cursor.execute("DELETE FROM habits WHERE id = ?", (args.id,))
            connection.commit()
            print(f"Removed habit {args.id}")
    else:
        print("Habit not found")
        exit()
        
        

elif args.command == "list":
    cursor.execute("SELECT * FROM habits ORDER BY id")
    rows = cursor.fetchall()
    if not rows:
        print("No habits yet.\nTry: add <your habit>")
    else:
        def list_header():
            print(f"{'ID':<3} | {'HABIT':<12} | STREAK")
            print("-" * 35)

        def list_print(rows, sort_index):
            data = []

            for id, name in rows:
                streak = calculate_streak(done_map[id])
                data.append((id, name, streak))
            reverse = args.sort == "streak"
            data.sort(key=lambda x: x[sort_index], reverse=reverse)

            for id, name, streak in data:
                streak_text = f"{streak} day" if streak == 1 else f"{streak} days"
                name = (name[:11] + "…") if len(name) > 12 else name

                print(f"{id:<3} | {name:<12} | {streak_text}")


        if args.sort == "streak":
            list_header()
            list_print(rows, 2)

        elif args.sort == "id":
            list_header()
            list_print(rows, 0)

        elif args.sort == "name":
            list_header()
            list_print(rows, 1)

        else:
            list_header()
            list_print(rows, 0)




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




elif args.command == "week":
    cursor.execute("SELECT * FROM habits ORDER BY id")
    all_habits = cursor.fetchall()

    if not all_habits:
        print("No habits yet.\nTry: add <your habit>")
    else:
        today = datetime.date.today()
        weekdays = []
        weekdays_full = []
        NAME_WIDTH = 12
        DAY_WIDTH = 3

        for i in range(6, -1, -1):
            day = today -datetime.timedelta(days=i)
            weekdays.append(day.strftime("%a"))
            weekdays_full.append(day)

        print(f"{'HABIT':<12} | " + " | ".join(f"{d:<{DAY_WIDTH}}" for d in weekdays))
        print("-" * 55)

        for habit_id, name in all_habits:
            marks = []
            
            for day in weekdays_full:
                if day.isoformat() in done_map[habit_id]:
                        marks.append("✔")
                else:
                    marks.append("✘")


            name = name[:NAME_WIDTH - 1] + "…" if len(name) > NAME_WIDTH else name

            print(f"{name:<{NAME_WIDTH}} | " + " | ".join(f"{m:<{DAY_WIDTH}}" for m in marks))




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
    streak = calculate_streak(done_map[args.id])

    print(f"Current streak: {streak}")



connection.close()