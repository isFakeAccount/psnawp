"""Group package for the PlayStation API wrapper.

This package provides access to PlayStation group features, including user groups, messaging threads, and group
metadata.

Modules in this package include:

- Fetching and managing group details.
- Accessing member lists and activity.
- Handling group-specific interactions.

"""

from psnawp_api.models.group.group import Group

__all__ = ["Group"]
