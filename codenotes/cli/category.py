from re import M
from codenotes.exceptions import MissingArgsException
from codenotes.util.sql import add_conditions_sql
from typing import Union, final
from argparse import Namespace

from rich import box
from rich.console import Console
from rich.table import Table

import codenotes.db.utilities.tasks_categories as task_categories
import codenotes.db.utilities.notes_categories as notes_categories
from codenotes.cli import PrintFormatted
from codenotes.util.text import format_list_text
from codenotes.db.connection import SQLiteConnection
from codenotes.util.args import format_argument_text


def create_args_empty(args: Namespace) -> bool:
    """ Check if arguments required to select an annotation type

    Parameters
    ----------
    args: Namespace
        Arguments capture

    Returns
    -------
    empty : bool
        Return boolean value if any args are empty
    """
    args_needed = [
        args.note,
        args.task
    ]
    if any(args_needed):
        return False
    return True


def search_args_empty(args: Namespace) -> bool:

    args_needed = [
        args.note,
        args.task,
        args.all    
    ]
    if any(args_needed):
        return False
    return True


@final
class CreateCategory:

    category: Union[list[str], str]
    category_table_name: str
    category_id_column: str
    category_name_column: str
    console: Console
    db: SQLiteConnection

    def __init__(self, args: Namespace) -> None:
        self.console = Console()
        self.db = SQLiteConnection()

        try:
            if create_args_empty(args):
                raise MissingArgsException

            self.category = format_list_text(args.text)
            self.__get_category_table(args)

            if args.preview:
                self._show_preview()

            else:
                self.save_category()

        except KeyboardInterrupt:
            self.console.print('[bold yellow]\nCorrectly Cancelled[/bold yellow]')
        
        except MissingArgsException:
            print("ERROR")

    @classmethod
    def set_args(cls, args: Namespace) -> None:
        cls(args)

    def category_exists(self, category_name: str) -> bool:
        """ Checks if the typed category exists

        Returns
        -------
        exists: bool
            Boolean value flag if the category already exists
        """
        sql = f"SELECT {self.category_id_column} FROM {self.category_table_name} WHERE {self.category_name_column} = '{category_name}'"
        query = self.db.exec_sql(sql)
        categories_list: list[tuple] = query.fetchall()

        if categories_list: # categories_list == []
            return True
        return False

    def save_category(self) -> None:
        sql = f'INSERT INTO {self.category_table_name} ({self.category_name_column}) VALUES(?)'
        
        with self.console.status('[bold yellow]Saving Tasks...') as status:
            if isinstance(self.category, list):
                # TODO: Validate if len of the category is 30
                for category in self.category:
                    if not self.category_exists(category):
                        values = (category,)
                        self.db.exec_sql(sql, values)

                        PrintFormatted.print_category_creation(category)
                    else:
                        PrintFormatted.custom_print(f'❌ [bold red]"{category}"[/bold] already exists')

            elif isinstance(self.category, str):
                if not self.category_exists(self.category):
                    values = (self.category,)
                    self.db.exec_sql(sql, values)

                    PrintFormatted.print_category_creation(self.category)
                else:
                    PrintFormatted.custom_print(f'❌ [bold red]"{self.category}"[/bold] already exists')
            
            if self.category:
                self.console.print('[bold green]✔️ Category Saved')

            else:
                self.console.print('[bold red] 💥 No Category Saved')
            
            status.stop()

        self.db.commit()
        self.db.close()

    def __get_category_table(self, args: Namespace) -> None:
        if args.note:
            self.category_table_name = notes_categories.TABLE_NAME
            self.category_id_column = notes_categories.COLUMN_ID
            self.category_name_column = notes_categories.COLUMN_NAME

        elif args.task:
            self.category_table_name = task_categories.TABLE_NAME
            self.category_id_column = task_categories.COLUMN_ID
            self.category_name_column = task_categories.COLUMN_NAME

    def _show_preview(self) -> None:
        table = Table(box=box.ROUNDED)
        table.add_column('Categories')

        if isinstance(self.category, list):
            for category in self.category:
                table.add_row(category)

        elif isinstance(self.category, str):
            table.add_row(self.category)

        self.console.print(table, justify='center')

        if PrintFormatted.ask_confirmation(
                '[yellow]Do you want to save them?(y/n):[/yellow]'
            ):
            self.save_category()


class SearchCategory:
    
    console: Console
    db: SQLiteConnection
    search_category: str

    def __init__(self, args: Namespace) -> None:
        self.console = Console()
        self.db = SQLiteConnection()
        self.search_category = format_argument_text(args.text)

        try:
            if search_args_empty(args):
                raise MissingArgsException
            
            self.search()

        except MissingArgsException:
            pass

    @classmethod
    def set_args(cls, args: Namespace) -> None:
        """ Class method that initializes the class and automatically will do the search

        Parameters
        ----------
        args: Namespace
            Arguments of argparse
        """
        cls(args)

    def search(self) -> None:
        pass

    def sql_query(self) -> None:
        sql = ""

        if self.search_category:
            pass
            # sql = add_conditions_sql(sql, f'WHERE {}' = '{}', 'AND')



class DeleteCategory:
    pass
