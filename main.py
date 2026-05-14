import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="command")
add_parser = subparsers.add_parser("add")
add_parser.add_argument("habit")

list_parser = subparsers.add_parser("list")

args = parser.parse_args()


if args.command == "add":
    print(f"Adding {args.habit}")

if args.command == "list":
    print("list")    