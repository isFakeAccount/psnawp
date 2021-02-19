```
(function(open) {
    XMLHttpRequest.prototype.open = function(method, url, async, user, pass) {

        this.addEventListener("readystatechange", function() {
            if (this.readyState == XMLHttpRequest.DONE) {
                let response = JSON.parse(this.responseText);

                if (response && "npsso" in response) {
                    console.log('found npsso', response.npsso);
                }
            }
        }, false);

        open.call(this, method, url, async, user, pass);
    };

    window.onbeforeunload = function(){
        return 'Are you sure you want to leave?';
    };

})(XMLHttpRequest.prototype.open);
```
1. Navigate to https://account.sonyentertainmentnetwork.com/ in your browser and open your browser’s developer console (typically CTRL + Shift + J).
2. Paste the above Javascript into the console and then login.
3. After the login flow is completed, you should see a new log in the developer console that looks like: found npsso <64 character code>. Copy that 64 character code.
4. Login using the python code below:

```
                                                V code from above
psn_python_api = psn_python_api.PSNPythonAPI('<64 character npsso code>')
psn_python_api.authenticate()
```