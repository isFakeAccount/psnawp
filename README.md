
# PlayStation Network API Wrapper Python (PSNAWP)

Retrieve User Information, Trophies, Game and Store data from the PlayStation Network

[![PyPI version](https://badge.fury.io/py/psnawp.svg)](https://badge.fury.io/py/PSNAWP)
[![Downloads](https://pepy.tech/badge/psnawp)](https://pepy.tech/project/psnawp)
[![python-logo](https://img.shields.io/badge/python-3.9_|_3.10-blue.svg)](https://www.python.org/)
[![pytest](https://github.com/isFakeAccount/psnawp/actions/workflows/pytest.yaml/badge.svg)](https://github.com/isFakeAccount/psnawp/actions/workflows/pytest.yaml)
[![pre-commit](https://github.com/isFakeAccount/psnawp/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/isFakeAccount/psnawp/actions/workflows/pre-commit.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/psnawp/badge/?version=latest)](https://psnawp.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/isFakeAccount/psnawp/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-95%25-brightgreen.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>/opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/__init__.py">__init__.py</a></td><td>1</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/psnawp.py">psnawp.py</a></td><td>32</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>/opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/core</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/core/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/core/authenticator.py">authenticator.py</a></td><td>45</td><td>3</td><td>3</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/core/authenticator.py#L 93%"> 93%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/core/psnawp_exceptions.py">psnawp_exceptions.py</a></td><td>9</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>/opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/models</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/models/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/models/client.py">client.py</a></td><td>47</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/models/group.py">group.py</a></td><td>44</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/models/search.py">search.py</a></td><td>14</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/models/user.py">user.py</a></td><td>55</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>/opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/utils</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/utils/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/utils/endpoints.py">endpoints.py</a></td><td>2</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/utils/misc.py">misc.py</a></td><td>13</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/utils/request_builder.py">request_builder.py</a></td><td>71</td><td>15</td><td>15</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main//opt/hostedtoolcache/Python/3.10.7/x64/lib/python3.10/site-packages/psnawp_api/utils/request_builder.py#L 79%"> 79%</a></td></tr><tr><td><b>TOTAL</b></td><td><b>333</b></td><td><b>18</b></td><td><b>95%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

## How to install

### From PyPI

```
pip install PSNAWP
```
### Using `setup.py`
To install the library into python. First you need to clone the repo at your local machine and run the following command from the root directory of the repo

```
python setup.py install
```

## Important Links
> PyPI: https://pypi.org/project/PSNAWP/
>
> Read the Docs: https://psnawp.readthedocs.io/en/latest/

## Getting Started

To get started you need to obtain npsso <64 character code>. You need to follow the following steps

1. Login into your [My PlayStation](https://my.playstation.com/) account.
2. In another tab, go to https://ca.account.sony.com/api/v1/ssocookie
3. If you are logged in you should see a text similar to this

```json
{"npsso":"<64 character npsso code>"}
```
This npsso code will be used in the api for authentication purposes. The refresh token that is generated from npsso lasts about 2 months. After that you have to get a new npsso token. The bot will print a warning if there are less than 3 days left in refresh token expiration.

Following is the quick example on how to use this library

```py
from psnawp_api import PSNAWP

psnawp = PSNAWP('<64 character npsso code>')

# This is you
client = psnawp.me()
print(client.online_id)
print(client.account_id)
print(client.get_account_devices())
print(client.get_profile_legacy())
print(client.friends_list())
print(client.blocked_list())
print(client.available_to_play())
groups = client.get_groups()
print(groups)

# Getting user from online
example_user_1 = psnawp.user(online_id="VaultTec-Co")
example_user_2 = psnawp.user(online_id="test")
print(example_user_1.online_id)
print(example_user_1.account_id)
print(example_user_1.profile())
print(example_user_1.prev_online_id)
print(example_user_1.get_presence())
print(example_user_1.friendship())
print(example_user_1.is_blocked())

# Getting user from Account ID
user_account_id = psnawp.user(account_id='9122947611907501295')
print(user_account_id.online_id)

# Sending Message
group = psnawp.group(group_id='38335156987791a6750a33ae452ec8666177b65e-103')
print(group.get_group_information())
print(group.get_conversation(10))
print(group.send_message("Hello World"))
print(group.change_name("API Testing 3"))
print(group.leave_group())

# Creating new group
new_group = psnawp.group(users_list=[example_user_1, example_user_2])

search = psnawp.search()
print(search.get_title_details(title_id="PPSA03420_00"))
print(search.universal_search("GTA 5"))
 ```

**Note: If you want to create multiple instances of psnawp you need to get npsso code from separate PSN accounts. If you generate a new npsso with same account your previous npsso will expire immediately.**

## Contribution

All bug reposts and features requests are welcomed, although I am new at making python libraries, so it may take me a while to implement some features. Suggestions are welcomes if I am doing something that is an unconventional way of doing it.

## Disclaimer

This project was not intended to be used for spam, abuse, or anything of the sort. Any use of this project for those purposes is not endorsed. Please keep this in mind when creating applications using this API wrapper.

## Credit

This project contains code from PlayStationNetwork::API and PSN-PHP Wrapper that was translated to Python. See more in [LICENSE](LICENSE.md)
