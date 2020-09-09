import calendar
from prompt_toolkit.styles import Style
from typing import overload, List, Union
from datetime import datetime, date, timedelta
import prompt_toolkit.output.win32 as prompt_toolkit
from prompt_toolkit import HTML, print_formatted_text


def date_args_empty(args) -> bool:
    """ Check if arguments required to search are empty
    Returns
    -------
    empty : bool
        Return boolean value if all related args to search are empty
    """
    args_needed = [
        args.month,
        args.text,
        args.today,
        args.week,
        args.yesterday
    ]

    if any(args_needed):
        return False
    return True


@overload
def dates_to_search(args) -> List[date]: ...


@overload
def dates_to_search(args) -> date: ...


def dates_to_search(args) -> Union[List[date], date]:
    """ Returns date to search depending of the user selection
    Returns
    -------
    search_date : date
        Returns date to search
    """
    now = datetime.now().date()
    if args.today:
        return now

    elif args.yesterday:
        return now - timedelta(days=1)

    elif args.week:
        first_day = now - timedelta(days=now.weekday())
        last_day = first_day + timedelta(days=6)

        days = [first_day, last_day]

        return days

    elif args.month:
        num_days = calendar.monthrange(now.year, now.month)[1]
        days = [
            date(now.year, now.month, 1),
            date(now.year, now.month, num_days)
        ]

        return days


class PrintFormatted:

    def __init__(self, html_text: HTML, styles: Style):
        """ PrintFormatted Constructor """
        self.print = print_formatted_text
        try:
            self.print(html_text, style=styles)
        except prompt_toolkit.NoConsoleScreenBufferError:
            print(html_text.value)

    @classmethod
    def print_html(cls, html_text: HTML, styles: Style):
        """ Class method used to print custom formatted text
        Parameters
        ----------
        html_text : HTML
            HTML text that will be print 
        styles: Style
            Styles that will be use in the HTML text
        """
        return cls(html_text, styles)

    @classmethod
    def print_tasks_storage(cls, task_txt: str, task_category: str = 'TODO Tasks'):
        """ Class method used to print the process of tasks storage
        Parameters
        ----------
        task_txt : str
            Content of the task that is stored
        task_category : str
            Category where the task is stored
        """
        custom_html = HTML(
            u'<b>></b><msg>Task saved[{}]: </msg><task-txt>{}</task-txt>'.format(task_category, task_txt)
        )

        custom_style = Style.from_dict({  # Style use for prints related with saving process
            'msg': '#d898ed bold',
            'task-txt': '#616161 italic'
        })

        return cls(custom_html, custom_style)
