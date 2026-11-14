from psycopg import DatabaseError

from Model import Model
from View import View
from View import Choice

class Controller:
    def __init__(self) -> None:
        self.view = View()
        self.model = Model(self.view.init_params())

    def handle_showtable(self):
        table_name = self.view.recv_table_name()
        cols = self.view.recv_columns()
        limit = self.view.recv_input("Input the limit for shown table (Leave blank to show all): ")

        if limit == 0:
            raise DatabaseError("LIMIT value has to be greater than 0.")

        result = self.model.fetch_all(table_name, cols if cols[0] else [], limit)

        if result:
            self.view.draw_table(result)
            if limit:
                self.view.print_message(f"Limited by {limit} rows.\n")
        else:
            self.view.print_message(f"Table {table_name} is currently empty\n")

    def handle_insertrow(self):
        table_name = self.view.recv_table_name()
        cols_list = self.model.get_table_cols(table_name)

        pseudo_fill = {col: "-" for col in cols_list}
        self.view.draw_table([pseudo_fill])

        recv = self.view.recv_row(cols_list)
        result = self.model.insert_row(table_name, recv)

        if result:
            self.view.draw_table(result)
            self.view.print_message("Row added.\n")
        else:
            self.view.print_message("Something went wrong during the insertion.\n")

    def handle_removerow(self):
        table_name = self.view.recv_table_name()
        pk_list = self.model.get_table_pk(table_name)
        cols_list = self.model.get_table_cols(table_name)

        pseudo_fill = {col: "*" if col in pk_list else "-" for col in cols_list}
        self.view.draw_table([pseudo_fill])

        recv = self.view.recv_row(pk_list)
        result = self.model.remove_row(table_name, recv)

        if result:
            self.view.draw_table(result)
            self.view.print_message("Row removed\n")
        else:
            self.view.print_message("No row with provided prime keys was found.\n")

    def handle_editrow(self):
        table_name = self.view.recv_table_name()
        pk_list = self.model.get_table_pk(table_name)
        cols_list = self.model.get_table_cols(table_name)

        pseudo_fill = {col: "*" if col in pk_list else "-" for col in cols_list}
        self.view.draw_table([pseudo_fill])
        self.view.print_message("Enter the prime key values, marked as (*) of the entry you want to edit.\n")
        pk_recv = self.view.recv_row(pk_list)

        self.view.print_message("Enter new values for this row: ")
        new_data = self.view.recv_row(cols_list)

        result = self.model.edit_row(table_name, pk_recv, new_data)
        if result:
            self.view.draw_table(result)
            self.view.print_message("Row updated.\n")
        else:
            self.view.print_message("A row with provided prime keys was not found.\n")

    def handle_generatedata(self):
        table_name = self.view.recv_table_name()
        amount = self.view.recv_input("Enter the int value: ", int)

        inserted = self.model.generate_data(table_name, amount)

        if inserted:
            self.view.print_message(f"Successfully inserted {inserted} rows into the {table_name} table. \n")
        else:
            self.view.print_message(f"Something went wrong during the insertion.\n")

    def handle_search(self):
        query_id = self.view.show_search_menu()

        if query_id == 1:
            self.view.print_message("Use '%' as wildcard for LIKE filters (e.g. %Хірург% or Іваненко%).")
            spec_like = self.view.recv_input("Doctor specialization pattern (LIKE): ", str)
            pat_like = self.view.recv_input("Patient name pattern (LIKE): ", str)
            date_from = self.view.recv_input("Start date (YYYY-MM-DD HH:MM:SS): ", str)
            date_to = self.view.recv_input("End date (YYYY-MM-DD HH:MM:SS): ", str)
            params = (spec_like, pat_like, date_from, date_to)

        elif query_id == 2:
            self.view.print_message("Use '%' as wildcard for LIKE filters (e.g. %бронхіт%).")
            illness_like = self.view.recv_input("Illness name pattern (LIKE): ", str)
            date_from = self.view.recv_input("Start date (YYYY-MM-DD HH:MM:SS): ", str)
            date_to = self.view.recv_input("End date (YYYY-MM-DD HH:MM:SS): ", str)
            params = (illness_like, date_from, date_to)

        elif query_id == 3:
            doc_like = self.view.recv_input("Doctor name pattern (LIKE, e.g. %): ", str)
            date_from = self.view.recv_input("Start date (YYYY-MM-DD HH:MM:SS): ", str)
            date_to = self.view.recv_input("End date (YYYY-MM-DD HH:MM:SS): ", str)
            min_visits = self.view.recv_input("Minimum appointments count (int): ", int)
            max_visits = self.view.recv_input("Maximum appointments count (int): ", int)
            params = (doc_like, date_from, date_to, min_visits, max_visits)

        else:
            self.view.print_message("Invalid search query number.\n")
            return

        rows, elapsed_ms = self.model.execute_search(query_id, params)

        if rows:
            self.view.draw_table(rows)
        else:
            self.view.print_message("No records matched the specified filters.")

        self.view.print_message(f"[Query execution time: {elapsed_ms:.3f} ms]\n")


    def run(self) -> None:
        run = True

        while run:
            chs = self.view.show_menu()

            try:
                if chs == Choice.SHOW_TABLE:
                    self.handle_showtable()
                elif chs == Choice.INSERT_ROW:
                    self.handle_insertrow()
                elif chs == Choice.REMOVE_ROW:
                    self.handle_removerow()
                elif chs == Choice.EDIT_ROW:
                    self.handle_editrow()
                elif chs == Choice.GENERATE_DATA:
                    self.handle_generatedata()
                elif chs == Choice.SEARCH:
                    self.handle_search()
                if chs == Choice.EXIT:
                    run = False
            except Exception as e:
                self.view.print_message(f"[DATABASE ERROR]: {e}")
