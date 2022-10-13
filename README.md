# homeasssitant-schlage
Schlage Encode implementation for Home Assistant

## Installation
### *Manual*
**(1)** Download the code zip file from Github

**(2)** Unzip the code and place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder).
It should look similar to this:
```
<config directory>/
|-- custom_components/
|   |-- homeasssitant-schlage/
|       |-- __init__.py
|       |-- config_flow.py
|       |-- const.py
|       |-- lock.py
|       |-- etc...
```

**(3)** Restart Home Assistant

**(4)** Install the new integration via the Home Assistant UI. "Settings --> Devices & Services --> Integrations" and then click "+ Add Integration" in the bottom right hand corner. Search for the Schlage integration.

**(5)** Enter your Schlage account information into the pop-up window.
