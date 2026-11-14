from enum import Enum
from typing import Any

class Choice(Enum):
    SHOW_TABLE = 1
    INSERT_ROW = 2
    REMOVE_ROW = 3
    EDIT_ROW = 4
    GENERATE_DATA = 5
    SEARCH = 6
    EXIT = 7
    NONE = 8

class View:
    @staticmethod
    def separator(func):
        def printer(*args):
            print("\n----------------------------------------\n")
            res = func(*args)
            return res
        return printer

    @staticmethod
    def init_params() -> list[str]:
        param_list = []

        print("To skip login type SKIP: ", end="")
        if str(input()) != "SKIP":
            print("Enter database name: ", end="")
            param_list.append(str(input()))
            print("Enter username: ", end="")
            param_list.append(str(input()))
            print("Enter password: ", end="")
            param_list.append(str(input()))
            print("Enter host IP: ", end="")
            param_list.append(str(input()))
            print("Enter host port: ", end="")
            param_list.append(str(input()))
        else:
            with open(".env", "r") as file:
                param_list = [s.strip().split(":")[1].strip() for s in file.readlines() if ":" in s]

        return param_list

    @staticmethod
    @separator
    def show_menu() -> Choice | None:
        print("Choose the option:",
              "Show table: 1",
              "Insert a row into the table: 2",
              "Remove a row from the table: 3",
              "Edit a row in the table: 4",
              "Generate a set amount of data: 5",
              "Search: 6",
              "Exit: 7", sep="\n")

        try:
            choice = Choice(int(input()))
            return choice

        except:
            print("[ERROR] Please choose a valid option")
            return Choice.NONE

    @staticmethod
    @separator
    def show_search_menu() -> int:
        print("Choose a search query:",
            "1. Appointments by Doctor specialization (LIKE), Patient name (LIKE), and Date range (BETWEEN)",
            "2. Diagnoses by Illness name (LIKE) and Date range (BETWEEN) with competence Doctors",
            "3. Doctor workload statistics (GROUP BY / HAVING) by Name (LIKE), Date range, and Visits count range",
            sep="\n")
        return int(input("Enter query number (1-3): ").strip())

    @staticmethod
    def print_message(msg: str) -> None:
        print(msg, end="")

    @staticmethod
    def recv_input(msg: str) -> str:
        print(msg, end="")

        return input()

    @staticmethod
    @separator
    def recv_table_name() -> str:
        print("Enter the table name: ", end="")

        table = str(input())
        return table

    @staticmethod
    @separator
    def recv_columns() -> list[str]:
        print("Enter table columns to show, separated by comma (e.g. col1,col2,col3) or skip to display all columns: ", end = "")

        col_choices = str(input()).split(",")
        return col_choices

    @staticmethod
    @separator
    def recv_row(cols: list[str]) -> dict[str, str]:
        print("Fill in all the provided attributes:")

        recv = {}
        for col in cols:
            print(f"{col}: ", end="")
            recv[col] = str(input())

        return recv

    @staticmethod
    @separator
    def draw_table(data: list[dict] | None) -> None:
        if not data:
            print("Nothing to display")
            return

        length_map = {}

        for _dict in data:
            for key in _dict.keys():
                if key not in length_map.keys() or len(str(_dict[key])) > length_map[key]:
                    length_map[key] = len(str(_dict[key])) if len(str(_dict[key])) > len(key) else len(key)

        total_table_length = 0

        for val in length_map.values():
            total_table_length += 2 + val + 1

        total_table_length += 1

        print("-" * total_table_length, sep="")
        for key in data[0]:
            print(f"| {key}", " " * (length_map[key] - len(key) + 1), sep="", end="")
        print("|")
        print("-" * total_table_length, sep="")

        for _dict in data:
            for key in _dict:
                print(f"| {_dict[key]}", " " * (length_map[key] - len(str(_dict[key])) + 1), sep="", end="")
            print("|")

        print("-" * total_table_length, sep="")
