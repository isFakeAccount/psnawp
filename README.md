# <img src="docs/_static/psn_logo.png" alt="PlayStation Logo" height="35px"> PlayStation Network API Wrapper Python (PSNAWP)

Retrieve User Information, Trophies, Game and Store data from the PlayStation Network

[![PyPI version](https://badge.fury.io/py/PSNAWP.svg)](https://badge.fury.io/py/PSNAWP)
[![Downloads](https://static.pepy.tech/badge/psnawp)](https://www.pepy.tech/projects/psnawp)
[![python-logo](https://img.shields.io/badge/python-3.9_|_3.10_|_3.11_|_3.12-blue.svg)](https://www.python.org/)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Documentation Status](https://readthedocs.org/projects/psnawp/badge/?version=latest)](https://psnawp.readthedocs.io/en/latest/?badge=latest)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![pre-commit](https://github.com/isFakeAccount/psnawp/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/isFakeAccount/psnawp/actions/workflows/pre-commit.yaml)
[![pytest](https://github.com/isFakeAccount/psnawp/actions/workflows/pytest.yaml/badge.svg)](https://github.com/isFakeAccount/psnawp/actions/workflows/pytest.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/MIT)

<!-- Pytest Coverage Comment:Begin -->
\n<!-- Pytest Coverage Comment:End -->

## How to install

### From PyPI

```
pip install PSNAWP
```

## Important Links
> PyPI: https://pypi.org/project/PSNAWP/
>
> Read the Docs: https://psnawp.readthedocs.io/en/latest/

## Getting Started

> [!CAUTION]
> This library is an unofficial and reverse-engineered API wrapper for the PlayStation Network (PSN). It has been developed based on the reverse engineering of the PSN Android app. At the moment the library doesn't implement automatic rate limiting. It is crucial for users to manually manage their request rate to avoid sending too many requests in a short period. Excessive use or bulk requests may lead to your PSN account being temporarily or permanently banned.
>
> You can also create a dedicated account to use this library so that in the worst-case scenario you do not lose access to your primary account, along with your video games and progress.

To get started you need to obtain npsso <64 character code>. You need to follow the following steps

1. Login into your [My PlayStation](https://my.playstation.com/) account.
2. In another tab, go to `https://ca.account.sony.com/api/v1/ssocookie`
3. If you are logged in you should see a text similar to this

```json
{"npsso":"<64 character npsso code>"}
```
This npsso code will be used in the api for authentication purposes. The refresh token that is generated from npsso lasts about 2 months. After that you have to get a new npsso token. The bot will print a warning if there are less than 3 days left in refresh token expiration.

Following is the quick example on how to use this library

```py
from psnawp_api import PSNAWP
from psnawp_api.models import SearchDomain
from psnawp_api.models.trophies import PlatformType

psnawp = PSNAWP("<64 character npsso code>")

# Your Personal Account Info
client = psnawp.me()
print(f"Online ID: {client.online_id}")
print(f"Account ID: {client.account_id}")
print(f"Profile: {client.get_profile_legacy()} \n")

# Your Registered Devices
devices = client.get_account_devices()
for device in devices:
    print(f"Device: {device} \n")

# Your Friends List
friends_list = client.friends_list()
for friend in friends_list:
    print(f"Friend: {friend} \n")

# Your Players Blocked List
blocked_list = client.blocked_list()
for blocked_user in blocked_list:
    print(f"Blocked User: {blocked_user} \n")

# Your Friends in "Notify when available" List
available_to_play = client.available_to_play()
for user in available_to_play:
    print(f"Available to Play: {user} \n")

# Your trophies (PS4)
for trophy in client.trophies("NPWR22810_00", PlatformType.PS4):
    print(trophy)

# Your Chat Groups
groups = client.get_groups()
first_group_id = None  # This will be used later to test group methods
for id, group in enumerate(groups):
    if id == 0:  # Get the first group ID
        first_group_id = group.group_id

    group_info = group.get_group_information()
    print(f"Group {id}: {group_info} \n")

# Your Playing time (PS4, PS5 above only)
titles_with_stats = client.title_stats()
for title in titles_with_stats:
    print(
        f" \
        Game: {title.name} - \
        Play Count: {title.play_count} - \
        Play Duration: {title.play_duration} \n"
    )


# Other User's
example_user_1 = psnawp.user(online_id="VaultTec-Co")  # Get a PSN player by their Online ID
print(f"User 1 Online ID: {example_user_1.online_id}")
print(f"User 1 Account ID: {example_user_1.account_id}")

print(example_user_1.profile())
print(example_user_1.prev_online_id)
print(example_user_1.get_presence())
print(example_user_1.friendship())
print(example_user_1.is_blocked())

# Example of getting a user by their account ID
user_account_id = psnawp.user(account_id="9122947611907501295")
print(f"User Account ID: {user_account_id.online_id}")


# Messaging and Groups Interaction
group = psnawp.group(group_id=first_group_id)  # This is the first group ID we got earlier - i.e. the first group in your groups list
print(group.get_group_information())
print(group.get_conversation(10))  # Get the last 10 messages in the group
print(group.send_message("Hello World"))
print(group.change_name("API Testing 3"))
# print(group.leave_group()) # Uncomment to leave the group

# Create a new group with other users - i.e. 'VaultTec-Co' and 'test'
example_user_2 = psnawp.user(online_id="test")
new_group = psnawp.group(users_list=[example_user_1, example_user_2])
print(new_group.get_group_information())
# You can use the same above methods to interact with the new group - i.e. send messages, change name, etc.

# Searching for Game Titles
search = psnawp.search(search_query="GTA 5", search_domain=SearchDomain.FULL_GAMES)
for search_result in search:
    print(search_result["result"]["invariantName"])

 ```

**Note: If you want to create multiple instances of psnawp you need to get npsso code from separate PSN accounts. If you generate a new npsso with same account your previous npsso will expire immediately.**

## Contribution

All bug reposts and features requests are welcomed, although I am new at making python libraries, so it may take me a while to implement some features. Suggestions are welcomes if I am doing something that is an unconventional way of doing it.

## Disclaimer

This project was not intended to be used for spam, abuse, or anything of the sort. Any use of this project for those purposes is not endorsed. Please keep this in mind when creating applications using this API wrapper.

## Credit

This project contains code from PlayStationNetwork::API and PSN-PHP Wrapper that was translated to Python. Also, special thanks @andshrew for documenting the PlayStation Trophy endpoints. All licenses are included in this repository.
