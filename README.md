# Play Station API Python (PSNAP)    
Retrieve User Information, Trophies, Game and Store data from the PlayStation Network
## Getting Started
To get started you need to obtain npsso <64 character code>. You need to follow the following steps

1. Login into your [My PlayStation](https://my.playstation.com/) account. 
2. In another tab, go to https://ca.account.sony.com/api/v1/ssocookie
3. If you are logged in you should see a text similar to this
```
{"npsso":"'<64 character npsso code>"}
```
This npsso code will be used in the api for authentication purposes. Following is the quick example of how to use this library
```
from psnap_api import psnap  

psnap = psnap.PSNAP('<64 character npsso code>')  
  
client = psnap.client  
print(client.get_account_id())  
print(client.get_account_devices())
```
## Contribution
All bug reposts and features requests are welcomed although I am new at making python libraries so it may take me a while to implement some features. Suggestions are welcomes if I am doing something that is unconventional way of doing it.


## Disclaimer
This project was not intended to be used for spam, abuse, or anything of the sort. Any use of this project for those purposes is not endorsed. Please keep this in mind when creating applications using this API wrapper.
