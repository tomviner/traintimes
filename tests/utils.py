import datetime


def date_in_range(backward=7, forward=90):
    """ Find a date within -7 to +90 days from current date.
    """
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    start = today - backward * day
    end = today + forward * day
    new_year = datetime.date(today.year, 1, 1)
    dates = [new_year + (mdelta * 31 * day) for mdelta in range(0, 15, 3)]
    in_range = [date for date in dates if start < date < end][0]
    return in_range
