import time
from dataclasses import field
from hashlib import file_digest
from typing import  Any

import psycopg
from psycopg.rows import dict_row
from psycopg import sql, DatabaseError, ProgrammingError


class Model:
    SCHEMA = {
        "Лікар": {
            "pk": ["Ліцензія"],
            "columns": ["Ліцензія", "ПІБ", "Спеціалізація"],
            "gen_sql": "large_queries/generate_doctor.sql"
        },
        "Пацієнт": {
            "pk": ["Номер мед. картки"],
            "columns": ["Номер мед. картки", "ПІБ"],
            "gen_sql": "large_queries/generate_patient.sql"
        },
        "Хвороба": {
            "pk": ["Код"],
            "columns": ["Код", "Назва"],
            "gen_sql": "large_queries/generate_illness.sql"
        },
        "Лікування": {
            "pk": ["Ліцензія_лікаря", "Код_хвороби"],
            "columns": ["Ліцензія_лікаря", "Код_хвороби"],
            "gen_sql": "large_queries/generate_doctor-illness.sql"
        },
        "Запис": {
            "pk": ["Ліцензія_лікаря", "Номер_пацієнта", "Дата_запису"],
            "columns": ["Ліцензія_лікаря", "Номер_пацієнта", "Дата_запису"],
            "gen_sql": "large_queries/generate_doctor-patient.sql"
        },
        "Діагноз": {
            "pk": ["Номер_пацієнта", "Код_хвороби", "Дата_Захворювання"],
            "columns": ["Номер_пацієнта", "Код_хвороби", "Дата_Захворювання"],
            "gen_sql": "large_queries/generate_patient-illness.sql"
        }
    }

    SEARCH_QUERIES = {
        1: "large_queries/search_1.sql",
        2: "large_queries/search_2.sql",
        3: "large_queries/search_3.sql"
    }

    def __init__(self, arg_list : list[str]):
        self.dsn = f"dbname={arg_list[0]} user={arg_list[1]} password={arg_list[2]} host={arg_list[3]} port={arg_list[4]}"

    def get_table_cols(self, table_name: str) -> list[Any]:
        if not table_name:
            raise DatabaseError("No table provided")

        if table_name in self.SCHEMA.keys():
            return self.SCHEMA[table_name]["columns"]
        else:
            raise DatabaseError(f"No table named {table_name} in this database")

    def get_table_pk(self, table_name: str) -> list[Any]:
        if not table_name:
            raise DatabaseError("No table provided")

        if table_name in self.SCHEMA.keys():
            return self.SCHEMA[table_name]["pk"]
        else:
            raise DatabaseError(f"No table named {table_name} in this database")

    def fetch_all(self, table_name: str, columns: list[str], limit: int) -> list[dict]:
        if not table_name:
            raise DatabaseError("No table provided")

        try:
            with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    if columns:
                        cols_sql = sql.SQL(", ").join(sql.Identifier(col) for col in columns)
                    else:
                        cols_sql = sql.SQL("*")

                    if limit:
                        query = sql.SQL("""
                            SELECT {fields}
                            FROM {table}
                            LIMIT %s
                        """).format(fields=cols_sql, table=sql.Identifier(table_name))

                        cur.execute(query, (limit,))
                    else:
                        query = sql.SQL("""
                            SELECT {fields}
                            FROM {table}
                        """).format(fields=cols_sql, table=sql.Identifier(table_name))

                        cur.execute(query)

                    return cur.fetchall()

        except psycopg.errors.ForeignKeyViolation as e:
            raise DatabaseError(f"Foreign key violation: the table {table_name} is connected with other tables "
                                f"via foreign key or key doesn't exist.")
        except psycopg.errors.UniqueViolation:
            raise DatabaseError(f"Unique violation: entry with provided prime key already exists.")
        except psycopg.errors.InvalidDatetimeFormat:
            raise DatabaseError(f"Invalid datetime format: use format YYYY-MM-DD HH:MM:SS.")
        except psycopg.errors.UndefinedTable:
            raise DatabaseError(f"No table named {table_name} in this database")
        except psycopg.Error as e:
            raise DatabaseError(f"An error occurred while fetching the data from the database: {e}.")

    def insert_row(self, table_name: str, data: dict | None) -> list[Any]:
        if not data:
            raise DatabaseError("No data provided")

        keys = data.keys()
        values = data.values()

        try:
            with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *").format(
                        table=sql.Identifier(table_name),
                        fields=sql.SQL(", ").join(sql.Identifier(col) for col in keys),
                        values=sql.SQL(", ").join(sql.Placeholder() * len(values))
                    )

                    cur.execute(query, [value for value in values])

                    return cur.fetchall()

        except psycopg.errors.ForeignKeyViolation as e:
            raise DatabaseError(f"Foreign key violation: the table {table_name} is connected with other tables "
                                f"via foreign key or key doesn't exist.")
        except psycopg.errors.UniqueViolation:
            raise DatabaseError(f"Unique violation: entry with provided prime key already exists.")
        except psycopg.errors.InvalidDatetimeFormat:
            raise DatabaseError(f"Invalid datetime format: use format YYYY-MM-DD HH:MM:SS.")
        except psycopg.errors.UndefinedTable:
            raise DatabaseError(f"No table named {table_name} in this database")
        except psycopg.Error as e:
            raise DatabaseError(f"An error occurred while modifying the database: {e.sqlstate}.")

    def remove_row(self, table_name: str, pk_values: dict) ->  list:
        if not pk_values:
            raise DatabaseError("No prime keys provided")

        conditions = [
            sql.SQL("{col}=%s").format(col=sql.Identifier(col)) for col in pk_values.keys()
        ]
        params = tuple(pk_values.values())

        try:
            with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    query = sql.SQL("DELETE FROM {table} WHERE {conditions} RETURNING *").format(
                        table=sql.Identifier(table_name),
                        conditions=sql.SQL(" AND ").join(conditions)
                    )

                    cur.execute(query, params)
                    return cur.fetchall()

        except psycopg.errors.ForeignKeyViolation as e:
            raise DatabaseError(f"Foreign key violation: the table {table_name} is connected with other tables "
                                f"via foreign key or key doesn't exist.")
        except psycopg.errors.UniqueViolation:
            raise DatabaseError(f"Unique violation: entry with provided prime key already exists.")
        except psycopg.errors.InvalidDatetimeFormat:
            raise DatabaseError(f"Invalid datetime format: use format YYYY-MM-DD HH:MM:SS.")
        except psycopg.errors.UndefinedTable:
            raise DatabaseError(f"No table named {table_name} in this database")
        except psycopg.Error as e:
            raise DatabaseError(f"An error occurred while modifying the database: {e.sqlstate}.")

    def edit_row(self, table_name: str, pk_values: dict, new_data: dict) -> list:
        if not pk_values or not new_data:
            raise DatabaseError("No prime keys or new data provided")

        filtrated_data = {
            key: val for key, val in new_data.items() if val is not None and val != ""
        }

        if not filtrated_data:
            raise DatabaseError("No new valid dat provided for update.")

        set_clauses = [
            sql.SQL("{col} = %s").format(col=sql.Identifier(col)) for col in filtrated_data.keys()
        ]

        where_clauses = [
            sql.SQL("{pk} = %s").format(pk=sql.Identifier(pk)) for pk in pk_values.keys()
        ]

        params = tuple(filtrated_data.values()) + tuple(pk_values.values())

        try:
            with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    query = sql.SQL("UPDATE {table} SET {set} WHERE {where} RETURNING *").format(
                        table=sql.Identifier(table_name),
                        set=sql.SQL(", ").join(set_clauses),
                        where=sql.SQL(" AND ").join(where_clauses)
                    )

                    cur.execute(query, params)
                    return cur.fetchall()

        except psycopg.errors.ForeignKeyViolation as e:
            raise DatabaseError(f"Foreign key violation: the table {table_name} is connected with other tables "
                                f"via foreign key or key doesn't exist.")
        except psycopg.errors.UniqueViolation:
            raise DatabaseError(f"Unique violation: entry with provided prime key already exists.")
        except psycopg.errors.InvalidDatetimeFormat:
            raise DatabaseError(f"Invalid datetime format: use format YYYY-MM-DD HH:MM:SS.")
        except psycopg.errors.UndefinedTable:
            raise DatabaseError(f"No table named {table_name} in this database")
        except psycopg.Error as e:
            raise DatabaseError(f"An error occurred while modifying the database: {e.sqlstate}.")

    def generate_data(self, table_name: str, count: int) -> int:
        if table_name not in self.SCHEMA:
            raise DatabaseError(f"No table named '{table_name}' in this database.")

        if count <= 0:
            raise DatabaseError("The amount of rows provided has to be greater than 0.")

        sql_path = str(self.SCHEMA[table_name]["gen_sql"])

        try:
            with open(sql_path, "rb") as file:
                query = file.read()

            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (count,))
                    return cur.rowcount

        except psycopg.errors.ForeignKeyViolation as e:
            raise DatabaseError(f"Foreign key violation: the table {table_name} is connected with other tables "
                                f"via foreign key or key doesn't exist.")
        except psycopg.errors.UniqueViolation:
            raise DatabaseError(f"Unique violation: entry with provided prime key already exists.")
        except psycopg.errors.InvalidDatetimeFormat:
            raise DatabaseError(f"Invalid datetime format: use format YYYY-MM-DD HH:MM:SS.")
        except psycopg.errors.UndefinedTable:
            raise DatabaseError(f"No table named {table_name} in this database")
        except psycopg.Error as e:
            raise DatabaseError(f"An error occurred while modifying the database: {e.sqlstate}.")

    def execute_search(self, query_id: int, *args) -> tuple[list[dict], float]:
        if query_id not in self.SEARCH_QUERIES:
            raise DatabaseError(f"Search query #{query_id} does not exist.")

        sql_path = self.SEARCH_QUERIES[query_id]

        try:
            with open(sql_path, "rb") as file:
                query = file.read()

            with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    start_time = time.perf_counter()
                    cur.execute(query, *args)
                    rows = cur.fetchall()
                    total_time = (time.perf_counter() - start_time) * 1000

                    return rows, total_time

        except psycopg.errors.UniqueViolation:
            raise DatabaseError(f"Unique violation: entry with provided prime key already exists.")
        except psycopg.errors.InvalidDatetimeFormat:
            raise DatabaseError(f"Invalid datetime format: use format YYYY-MM-DD HH:MM:SS.")
        except psycopg.errors.UndefinedTable:
            raise DatabaseError(f"No such table in this database")
        except psycopg.Error as e:
            raise DatabaseError(f"An error occurred while modifying the database: {e.sqlstate}.")