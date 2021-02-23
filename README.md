# smartbridge
A simple layer of abstraction over multiple smart-device services.

## Installation

Install the latest release from PyPi:

```shell

  pip install smartbridge
```


## Usage example

To get started with SmartBridge, export your smart device provider's access credentials (e.g., WYZE_USERNAME and WYZE_PASSWORD for your Wyze credentials) and log in via the API:

```python
from smartbridge.factory import ProviderFactory, ProviderList

provider = ProviderFactory().create_provider(ProviderList.WYZE, {})
credentials = provider.wyze_client.login('<your wyze.com email>', '<your wyze.com password>')
```

To explore the API, pass the generated credentials in the config object:

```python
from smartbridge.factory import ProviderFactory, ProviderList
  
config = {
    'access_token': <my access token>
}

provider = ProviderFactory().create_provider(ProviderList.WYZE, config)
print(provider.plug.list())
```

The exact same command (as well as any other SmartBridge method) will run with any of the supported providers: `ProviderList.[WYZE]`!
