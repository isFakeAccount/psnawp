
# PlayStation Network API Wrapper Python (PSNAWP)  
  
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
{"npsso":"'<64 character npsso code>"}  
```   
This npsso code will be used in the api for authentication purposes. Following is the quick example on how to use this library  
  
```  
from psnawp_api import psnawp

psnawp = psnawp.PSNAWP('<64 character npsso code>')   

# Client that is you  
client = psnawp.me() 
print(client.get_account_id()) 
print(client.get_account_devices()) 
print(client.get_friends())

# User: Another user  
user = psnawp.user("VaultTec_Trading") 
print(user.profile()) 
print(user.get_presence()) 
print(user.friendship()) 
print(user.is_available_to_play()) 
print(user.is_blocked())
user.send_private_message("Hello World!")
messages = user.get_messages_in_conversation(message_count=1)  
 ```   
Sending private message only works if the message group between you and user already exists otherwise it will throw HTTP Status Code 429. Basically you would have to create the group yourself through the APP or ask the user to send you message first.

**Note: If you want to create multiple instances of psnawp you need to get npsso code from separate PSN accounts. If you generate a new npsso with same account your previous npsso will expire immediately.**  
  
## Contribution  
  
All bug reposts and features requests are welcomed although I am new at making python libraries, so it may take me a while to implement some features. Suggestions are welcomes if I am doing something that is an unconventional way of doing it.  
  
## Disclaimer  
  
This project was not intended to be used for spam, abuse, or anything of the sort. Any use of this project for those purposes is not endorsed. Please keep this in mind when creating applications using this API wrapper.

## Credit

This project contains code from PlayStationNetwork::API and PSN-PHP Wrapper that was translated to Python. See more in [LICENSE](LICENSE.md)