import argparse
import sqlite3



parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="command")

add_parser = subparsers.add_parser("add")
add_parser.add_argument("habit")

remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("habit")

list_parser = subparsers.add_parser("list")

args = parser.parse_args()



connection = sqlite3.connect("habits.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
)
""")




if args.command == "add":
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



if args.command == "remove":
    cursor.execute(
        "SELECT 1 FROM habits WHERE name = ?",
        (args.habit,)
    )
    exists = cursor.fetchone()

    if exists:
        cursor.execute(
            "DELETE FROM habits WHERE name = ?",
            (args.habit,)
        )
        connection.commit()
        print(f"Removed {args.habit}")
    else:
        print("Habit doesn't exist")
        
        

if args.command == "list":
    cursor.execute("SELECT * FROM habits ORDER BY id")
    rows = cursor.fetchall()
    if not rows:
        print("No habits yet.\nTry: add <your habit>")
    else:
        for id, name in rows:
            print(f"{id:>3} | {name}")





connection.close()