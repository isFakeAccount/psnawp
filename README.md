
# PlayStation Network API Wrapper Python (PSNAWP)

[![pytest](https://github.com/isFakeAccount/psnawp/actions/workflows/pytest.yaml/badge.svg)](https://github.com/isFakeAccount/psnawp/actions/workflows/pytest.yaml)
[![pre-commit](https://github.com/isFakeAccount/psnawp/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/isFakeAccount/psnawp/actions/workflows/pre-commit.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/isFakeAccount/psnawp/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-0%25-red.svg" /></a><br/><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>src/psnawp_api</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/__init__.py">__init__.py</a></td><td>1</td><td>1</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/__init__.py#L1">1</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/authenticator.py">authenticator.py</a></td><td>40</td><td>40</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/authenticator.py#L1-L125">1&ndash;125</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/base.py">base.py</a></td><td>3</td><td>3</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/base.py#L1-L5">1&ndash;5</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/client.py">client.py</a></td><td>32</td><td>32</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/client.py#L1-L87">1&ndash;87</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/endpoints.py">endpoints.py</a></td><td>2</td><td>2</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/endpoints.py#L1-L7">1&ndash;7</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/message_thread.py">message_thread.py</a></td><td>37</td><td>37</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/message_thread.py#L4-L109">4&ndash;109</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/psnawp.py">psnawp.py</a></td><td>22</td><td>22</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/psnawp.py#L1-L59">1&ndash;59</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/psnawp_exceptions.py">psnawp_exceptions.py</a></td><td>9</td><td>9</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/psnawp_exceptions.py#L3-L21">3&ndash;21</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/request_builder.py">request_builder.py</a></td><td>51</td><td>51</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/request_builder.py#L1-L106">1&ndash;106</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/search.py">search.py</a></td><td>11</td><td>11</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/search.py#L1-L35">1&ndash;35</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/user.py">user.py</a></td><td>58</td><td>58</td><td>0%</td><td><a href="https://github.com/isFakeAccount/psnawp/blob/main/src/psnawp_api/user.py#L1-L149">1&ndash;149</a></td></tr><tr><td><b>TOTAL</b></td><td><b>266</b></td><td><b>266</b></td><td><b>0%</b></td><td>&nbsp;</td></tr></tbody></table></details>
"| Tests | Skipped | Failures | Errors | Time |
| ----- | ------- | -------- | -------- | ------------------ |
| 6 | 1 :zzz: | 0 :x: | 0 :fire: | 1.046s :stopwatch: |
"
<!-- Pytest Coverage Comment:End -->

Retrieve User Information, Trophies, Game and Store data from the PlayStation Network

## How to install

### From PyPI

```
pip install PSNAWP
```
### Using setup.py
To install the library into python. First you need to clone the repo at your local machine and run the following command from the root directory of the repo

```
python setup.py install
```

## Getting Started

To get started you need to obtain npsso <64 character code>. You need to follow the following steps

1. Login into your [My PlayStation](https://my.playstation.com/) account.
2. In another tab, go to https://ca.account.sony.com/api/v1/ssocookie
3. If you are logged in you should see a text similar to this

```
{"npsso":"<64 character npsso code>"}
```
This npsso code will be used in the api for authentication purposes. The refresh token that is generated from npsso lasts about 2 months. After that you have to get a new npsso token. The bot will print a warning if there are less than 3 days left in refresh token expiration.

Following is the quick example on how to use this library

```
from psnawp_api import psnawp

psnawp = psnawp.PSNAWP('<64 character npsso code>')

# Client that is you
client = psnawp.me()
print(client.get_online_id())
print(client.get_account_id())
print(client.get_account_devices())
print(client.get_friends())
print(client.blocked_list())

# Getting user from online
user_online_id = psnawp.user(online_id="VaultTec_Trading")
print(user_online_id.online_id)
print(user_online_id.account_id)
print(user_online_id.profile())
print(user_online_id.get_presence())
print(user_online_id.friendship())
print(user_online_id.is_available_to_play())
print(user_online_id.is_blocked())

# Sending Message
user_online_id.send_private_message("Hello World!")
messages = user_online_id.get_messages_in_conversation(message_count=1)
# If you want to leave the conversation
user_online_id.leave_private_message_group()

# Getting user from Account ID
user_account_id = psnawp.user(account_id='1802043923080044300')
# Same functions as shown above
 ```
Sending private message only works if the message group between you and user already exists otherwise it will throw HTTP Status Code 429. Basically you would have to create the group yourself through the APP or ask the user to send you message first.

**Note: If you want to create multiple instances of psnawp you need to get npsso code from separate PSN accounts. If you generate a new npsso with same account your previous npsso will expire immediately.**

## Contribution

All bug reposts and features requests are welcomed although I am new at making python libraries, so it may take me a while to implement some features. Suggestions are welcomes if I am doing something that is an unconventional way of doing it.

## Disclaimer

This project was not intended to be used for spam, abuse, or anything of the sort. Any use of this project for those purposes is not endorsed. Please keep this in mind when creating applications using this API wrapper.

## Credit

This project contains code from PlayStationNetwork::API and PSN-PHP Wrapper that was translated to Python. See more in [LICENSE](LICENSE.md)
