import argparse
import sqlite3
import datetime

#parser commands
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

list_parser = subparsers.add_parser("list",
    help="List all habits",
    description="Lists all your habits and their ID's"
)

done_parser = subparsers.add_parser("done",
    help="Mark habit as done",
    description="Marks a habit as done for today"
)
done_parser.add_argument("id", type=int)

parser.epilog = """
Examples:
  habit add exercise
  habit list
  habit remove 3
  habit done 2
"""

args = parser.parse_args()


#creates db files
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




#command logic
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



elif args.command == "done":
    cursor.execute(
        "SELECT 1 FROM habits WHERE id = ?",
        (args.id,)
    )
    exists = cursor.fetchone()

    if exists:
        try:
            today = datetime.date.today().isoformat()
            cursor.execute(
                "INSERT INTO completions (habit_id, date) VALUES (?, ?)",
                (args.id, today)
            )
            connection.commit()
            print(f"Marked habit {args.id} as done")
        except sqlite3.IntegrityError:
            print("Already marked done today")
    else:
        print("Habit not found")




connection.close()