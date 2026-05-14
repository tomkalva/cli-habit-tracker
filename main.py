import argparse
import sqlite3



parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="command")

add_parser = subparsers.add_parser("add")
add_parser.add_argument("habit")

list_parser = subparsers.add_parser("list")

args = parser.parse_args()



connection = sqlite3.connect("habits.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY,
    name TEXT
)
""")




if args.command == "add":
    print(f"Added {args.habit}")

    cursor.execute(
    "INSERT INTO habits (name) VALUES (?)",
    (args.habit,)
    )
    
if args.command == "list":
    cursor.execute("SELECT * FROM habits")
    rows = cursor.fetchall()

    print_string = ""
    for habit in rows:
        print_string += f"{habit[0]}.{habit[1]}\n"

    print(print_string)


connection.commit()
connection.close()