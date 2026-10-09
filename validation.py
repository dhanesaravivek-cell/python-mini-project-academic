"""validation.py - checks the data typed by the user.
Every function returns the cleaned value, or raises ValueError with a message."""
from datetime import datetime, date


def check_date(text):
    """Convert 'YYYY-MM-DD' text to a date object."""
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format, e.g. 2026-07-15")


def check_past_date(text):
    """Same as check_date, but the date cannot be in the future."""
    d = check_date(text)
    if d > date.today():
        raise ValueError("Date cannot be in the future")
    return d


def check_location(text):
    """Location must not be empty and must be at most 50 characters."""
    name = " ".join(text.split())
    if name == "":
        raise ValueError("Location cannot be empty")
    if len(name) > 50:
        raise ValueError("Location must be 50 characters or less")
    return name.title()


def check_rainfall(text):
    """Rainfall must be a number between 0 and 2000 (mm)."""
    try:
        value = float(text)
    except ValueError:
        raise ValueError("Rainfall must be a number")
    if not 0 <= value <= 2000:      # also rejects 'nan'
        raise ValueError("Rainfall must be between 0 and 2000 mm")
    return round(value, 2)
