import calendar
from typing import overload, List, Union, final
from datetime import datetime, date, timedelta

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


def format_argument_text(arg_text: List[str]) -> str:
    """ Function use to join the list of strings passed in the arguments"""
    text = ' '.join(arg_text)

    return text.strip()
