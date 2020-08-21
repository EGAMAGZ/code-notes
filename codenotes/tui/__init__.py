import py_cui
import curses
from yaspin import yaspin
from datetime import datetime

import codenotes.db.utilities.todo as todo
from codenotes.console import PrintFormatted
from codenotes.db.connection import SQLiteConnection


WHITE_ON_MAGENTA = 11


class ImpPyCUI(py_cui.PyCUI):

    def __init__(self, num_rows, num_cols, auto_focus_buttons=True, exit_key=py_cui.keys.KEY_Q_LOWER,
                 simulated_terminal=None):
        """ Initializer of ImpPyCUI class"""
        super().__init__(num_rows, num_cols, auto_focus_buttons, exit_key, simulated_terminal)
        self.toggle_unicode_borders()

    def _initialize_colors(self):
        """ Override of base class function"""
        super()._initialize_colors()
        curses.init_pair(WHITE_ON_MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)


class AddTodoTUI:

    tasks_list_menu: py_cui.widgets.ScrollMenu
    todo_text_block: py_cui.widgets.TextBox

    def __init__(self, root: ImpPyCUI):
        """ Constructor of AddTodoTUI class"""
        self.root = root
        self.db = SQLiteConnection()
        self.cursor = self.db.get_cursor()

        self.todo_text_block = self.root.add_text_box('New Todo Task', 0, 0, column_span=4)
        self.tasks_list_menu = self.root.add_scroll_menu('Todo tasks to add', 1, 0, column_span=4, row_span=4)

        self.__config()

    @classmethod
    def set_root(cls, root: ImpPyCUI):
        return cls(root)

    def _add_todo_task(self):
        """  Adds task to tasks_list_menu widget """
        text = self.todo_text_block.get()
        self.tasks_list_menu.add_item(text)
        self.todo_text_block.clear()

    def _remove_todo_task(self):
        """ Removes task from list """
        self.tasks_list_menu.remove_selected_item()

    def _save_todo_tasks(self):
        """ Function that stores the tasks added in tasks_list_menu widget """
        creation_date = datetime.now().date()
        todo_tasks_list = self.tasks_list_menu.get_item_list()
        sql = f'INSERT INTO {todo.TABLE_NAME} ({todo.COLUMN_TODO_CONTENT},{todo.COLUMN_TODO_CREATION}) VALUES ' \
              f'(?,?); '
        with yaspin(text='saving todo tasks') as spinner:
            for task in todo_tasks_list:
                values = (task, creation_date)
                self.cursor.execute(sql, values)
                self.db.conn.commit()
                spinner.hide()
                PrintFormatted.print_tasks_storage(task)
                spinner.show()
            spinner.ok("✔")
        self.cursor.close()
        self.db.conn.close()

    def __config(self):
        """ Function that configures the widgets of the root """
        self.todo_text_block.add_key_command(py_cui.keys.KEY_ENTER, self._add_todo_task)
        self.todo_text_block.set_focus_text('|Enter - Add New Todo Task|')

        self.tasks_list_menu.add_key_command(py_cui.keys.KEY_BACKSPACE, self._remove_todo_task)
        self.tasks_list_menu.set_focus_text('|Backspace - Remove Todo Task|')

        self.root.set_title('Codenotes - Add TODO Tasks')
        self.root.status_bar.set_text('|q-Quit & Save Todo Tasks| Arrows keys - Move| Enter - Enter Focus Mode|')
        self.root.run_on_exit(self._save_todo_tasks)


class SearchTodoTUI:

    def __init__(self, root: ImpPyCUI):
        self.root = root

        self.__config()

    @classmethod
    def set_root(cls, root: ImpPyCUI):
        return cls(root)

    def __config(self):
        self.root.set_title('Codenotes - Search TODO Tasks')
