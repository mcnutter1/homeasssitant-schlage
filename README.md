<div style="background-color:#f8d7da; color:#721c24; padding:10px; border:1px solid #f5c6cb; border-radius:5px;" align="center">

⚠️⚠️ **Migrate to native Schlage Home Assistant integration recommended!** ⚠️⚠️

Home Assistant now has a native integration for Schlage. Visit [the Schlage integration](https://www.home-assistant.io/integrations/schlage/) to learn more.

As of HA 2024.2, it is recommended to use the native integration over this integration.

No further maintenance or development will happen on this repository.

</div>

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
