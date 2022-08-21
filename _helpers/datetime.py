import jdatetime


def month_range(year, month):
    now = jdatetime.date.today()
    try:
        last = jdatetime.date(year, month + 1, 1)
    except ValueError:
        last = jdatetime.date(year + 1, 1, 1)

    return now.day if year == now.year and month == now.month else 1, (last - jdatetime.timedelta(days=1)).day + 1
