from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def date_add_days(value, days):
    """Add days to a date."""
    try:
        days = int(days)
        return value + timedelta(days=days)
    except (ValueError, TypeError):
        return value

@register.filter
def add_days(value, days):
    """Add days to a date (alias for date_add_days)."""
    return date_add_days(value, days)