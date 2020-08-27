import py_cui
import curses
from yaspin import yaspin
from typing import List, Tuple
from datetime import date, datetime, timedelta

from codenotes.db.utilities import Category
import codenotes.db.utilities.tasks as tasks
from codenotes.console import PrintFormatted
from codenotes.db.connection import SQLiteConnection
import codenotes.db.utilities.tasks_categories as categories


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


class AddTaskTUI:

    tasks_list_menu: py_cui.widgets.ScrollMenu
    task_text_block: py_cui.widgets.TextBox

    categories_list: List[Category] = []
    selected_category: Category = None

    def __init__(self, root: ImpPyCUI):
        """ Constructor of AddTaskTUI class"""
        self.root = root
        self.db = SQLiteConnection()
        self.cursor = self.db.get_cursor()

        # -| Text Blocks |-
        self.task_text_block = self.root.add_text_box('New Task', 0, 0, column_span=4)
        # -| Scroll Menus |-
        self.task_categories_menu = self.root.add_scroll_menu('Categories', 1, 0, row_span=4)
        self.tasks_list_menu = self.root.add_scroll_menu('Tasks to add', 1, 1, column_span=3, row_span=3)
        # -| Buttons |-
        self.save_button = self.root.add_button('Save Tasks', 4, 1, column_span=3, command=self.save_tasks)

        self.__config()

    @classmethod
    def set_root(cls, root: ImpPyCUI):
        return cls(root)

    def get_categories(self) -> List[Tuple[str]]:
        """ Gets all categories stored in database """
        sql = f'SELECT {categories.COLUMN_CATEGORY_ID},{categories.COLUMN_CATEGORY_NAME} FROM {categories.TABLE_NAME};'

        query = self.cursor.execute(sql)

        return query.fetchall()

    def _show_category_name(self):
        """ Shows message popup to display complete the whole category name """
        category = self.task_categories_menu.get()

        self.root.show_message_popup('Category Name:', category.category_name)

    def _show_missing_category(self):
        """ Shows warning popup to advice the user that he hasn't choose a category where to save the tasks """
        self.root.show_warning_popup("You Haven't Choose a Category", 'Please Select Category Where to Save the Tasks')

    def _load_menu_categories(self):
        """ Functions that creates a list of tasks and added it to the categories menu """
        self.categories_list = [Category(category[0], category[1]) for category in self.get_categories()]

        self.task_categories_menu.add_item_list(self.categories_list)

    def _select_category(self):
        """ Function that is executed when a category is selected """
        self.selected_category = self.task_categories_menu.get()

        self.task_categories_menu.set_title(f'{self.selected_category}')

    def _ask_new_category(self):
        """ Shows text box popup """
        self.root.show_text_box_popup('Enter new category name (Max. 30):', command=self._add_category)

    def _add_category(self, category: str):
        """ Adds new category to categories menu and saves it in database """
        if category and len(category) <= 30:
            sql = f'INSERT INTO {categories.TABLE_NAME} ({categories.COLUMN_CATEGORY_NAME}) VALUES (?)'

            self.cursor.execute(sql, (category,))

            category_id = self.cursor.lastrowid
            self.task_categories_menu.add_item(Category(category_id, category))

            self.db.conn.commit()
        else:
            self._ask_new_category()

    def _add_task(self):
        """  Adds task to tasks_list_menu widget """
        text = self.task_text_block.get()

        self.tasks_list_menu.add_item(text)
        self.task_text_block.clear()

    def _remove_task(self):
        """ Removes task from list """
        self.tasks_list_menu.remove_selected_item()

    def save_tasks(self):
        """ Function that stores the tasks added in tasks_list_menu widget """
        tasks_list = self.tasks_list_menu.get_item_list()
        creation_date = datetime.now().date()

        sql = f'INSERT INTO {tasks.TABLE_NAME} ({tasks.COLUMN_TASK_CONTENT},{tasks.COLUMN_TASK_CREATION}, '\
              f'{tasks.COLUMN_TASK_CATEGORY}) VALUES (?,?,?); '

        with yaspin(text='Saving Tasks') as spinner:
            if tasks_list:
                if self.selected_category is not None:
                    # Selected a category
                    self.root.stop()
                    for task in tasks_list:
                        values = (task, creation_date, self.selected_category.category_id)

                        self.cursor.execute(sql, values)
                        spinner.hide()
                        PrintFormatted.print_tasks_storage(task, self.selected_category.category_name)
                        spinner.show()
                    spinner.ok("✔")

                    self.db.conn.commit()
                    self.db.close()
                else:
                    self._show_missing_category()
            else:
                # Empty list of tasks
                self.root.stop()
                spinner.text = 'No Task Saved'
                spinner.fail("💥")
                self.db.close()

    def __config(self):
        """ Function that configures the widgets of the root """
        self._load_menu_categories()

        self.task_text_block.add_key_command(py_cui.keys.KEY_ENTER, self._add_task)
        self.task_text_block.set_focus_text('|Enter - Add New Task| Esc - Exit|')

        self.tasks_list_menu.add_key_command(py_cui.keys.KEY_BACKSPACE, self._remove_task)
        self.tasks_list_menu.set_focus_text('|Backspace - Remove Task|Esc - Exit |')

        self.task_categories_menu.add_key_command(py_cui.keys.KEY_ENTER, self._select_category)
        self.task_categories_menu.add_key_command(py_cui.keys.KEY_N_LOWER, self._ask_new_category)
        self.task_categories_menu.add_key_command(py_cui.keys.KEY_SPACE, self._show_category_name)
        self.task_categories_menu.set_focus_text(
            '|n - New Category|Enter - Select Category|Space - Show category|Up/Down - Move|Esc - Exit|'
        )

        self.root.set_title('Codenotes - Add Tasks')
        self.root.status_bar.set_text('|q-Quit Without Saving Tasks| Arrows keys - Move| Enter - Enter Focus Mode|')


class SearchTaskTUI:

    DATE_OPTIONS: List[str] = ['None', 'Today', 'Yesterday']

    date_search_button: py_cui.widgets.Button
    task_search_text_box: py_cui.widgets.TextBox

    search_date: date = None

    def __init__(self, root: ImpPyCUI):
        """ Constructor of SearchTaskTUI class 

        Parameters
        ----------
        root : ImpPyCUI
            Root for TUI
        """
        self.root = root
        self.db = SQLiteConnection()
        self.cursor = self.db.get_cursor()
        # -| Buttons |-
        self.date_search_button = self.root.add_button('Select Date', 0, 3, command=self._show_menu_date_popup)
        # -| Text Boxes |-
        self.task_search_text_box = self.root.add_text_box('Search task:', 0, 0)

        self.__config()

    @classmethod
    def set_root(cls, root: ImpPyCUI):
        """ Sets root and initialize class
        
        Parameters
        ----------
        root : ImpPyCUI
            Root for TUI
        """
        return cls(root)

    def _show_menu_date_popup(self):
        self.root.show_menu_popup('Date Options', menu_items=self.DATE_OPTIONS, command=self._set_date_option)

    def _set_date_option(self, date_option):
        title = ''
        if date_option == 'None':
            title = 'Select Date'
            self.search_date = None
        elif date_option == 'Today':
            title = 'Today'
            self.search_date = datetime.now().date()
        elif date_option == 'Yesterday':
            title = 'Yesterday'
            self.search_date = datetime.now().date() - timedelta(days=1)

        self.date_search_button.set_title(title)

    def __config(self):
        """ Function that configures the widgets of the root """

        self.root.set_title('Codenotes - Search Tasks')
