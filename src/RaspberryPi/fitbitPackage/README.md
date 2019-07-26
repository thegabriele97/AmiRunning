# FITBIT PYTHON API for AmiRunning

Provide a useful fitbit python api class for [AmIRunning](https://github.com/AmI-2019/AmIRunning-code). Based on [Python Fitbit Api](https://github.com/orcasgit/python-fitbit)

### Prerequisites

For this library u need to have at least Python 3.7 installed on your system:
```console
   sudo apt install python3.7 python3-pip
```

To use the library, you need to install the runtime requirements:

```console
   sudo pip3 install -r requirements.txt
```

Be sure to have this packages installed on your system. Try do do:
```console
   sudo apt install python3-gdbm python3-tk
```


you need a .json file with this structure:
```json
   {
      "fitbit_client_id": "<your client id>",
      "fitbit_client_secret": "<your client secred>",
      "fitbit_oauth_callback": "https://<your callback url>",
      "...": ...,
      "cherrypy_fitbit_oauth_address": "127.0.0.1",
      "cherrypy_fitbit_oauth_port": 9076
      "...": ...,
      ....
   }
```

## How to use it

Let's start your code with:

```python
from fitbitPackage import *
```

this will create a fitbit_api object.

### Obtain Authorization URL

You can obtain the corrent Authorization url for your app by using:

```python
fitbit_api.get_authorize_url()
```

### Waiting for authetication by the user

You can start a polling, waiting for authetication by the user, with:

```python
fitbit_api.start_response_poll()
```

This will start a cherrpy server with settings specified in your json file, waiting for redirect by User authetication. The redirect url specified on app setting (on fitbit.com) needs to point to your public ip and a nat table on your router must redirect it on your local machine running the server at the port specified in your json.

## Start working

Now that the user is logged in, you can create a client object with

```python
client = fitbit_api.get_auth_client()
```

On client var you can execute your query on user's data.

### Datetime support

The original fitbit api use a particular date format for query. You can create a corrent date using

```python
date = get_right_dateFormat(0)
```

with 'offset' as offset parameter starting from today date. '0' means today, '-1' means yesterday.