import requests
import logging
import websocket
import json
import logging
import asyncio
import aiohttp
import async_timeout
import boto3
from pycognito.aws_srp import AWSSRP
from pprint import pprint
import time

API_TIMEOUT = 60
_LOGGER = logging.getLogger(__name__)



class SchlageAPI:

    LOCK_STATUS_URL = "api.allegion.yonomi.cloud/v1/devices?archetype=lock"
    LOCK_STATE_URL = "api.allegion.yonomi.cloud/v1/devices/"


    REQUEST_TIMEOUT = 60

    LOCK_STATE = {
        '1': True,
	    '0': False
    }


    

    logger = logging.getLogger(__name__)

    cookie_jar = aiohttp.CookieJar(unsafe=True)

    def __init__(self, username, password, loop = None):
        """Initialize the API object."""
        self.username = username
        self.password = password
        self.apikey = "hnuu9jbbJr7MssFDWm5nU2Z7nG5Q5rxsaqWsE7e9"
        self.last_checkin = None
        self._api_timeout = API_TIMEOUT
        self._loop = loop or asyncio.get_event_loop()
        self._unitid = None
        self._sessionid = None
        self._token = None
        self.devices = {}
        self.states = {}



    def _get_token_request(self):
        client = boto3.client('cognito-idp',region_name='us-west-2')
        
        aws = AWSSRP(username=self.username, password=self.password,
                 client_id='t5836cptp2s1il0u9lki03j5', pool_id="us-west-2_2zhrVs9d4", client=client, client_secret="1kfmt18bgaig51in4j4v1j3jbe7ioqtjhle5o6knqc5dat0tpuvo")
        tokens = aws.authenticate_user()
        self._token = tokens['AuthenticationResult']['AccessToken']


    async def _get_token(self):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._get_token_request)

    async def _get_devices(self):


        HTTP_HEADERS = {"Authorization":f"Bearer {self._token}","x-api-key": self.apikey, "content-type": "application/json", "accept-encoding": "gzip", "user-agent": "okhttp/4.2.2" }                      
        try:
            
            with async_timeout.timeout(self._api_timeout):

                URI = "https://{}".format(self.LOCK_STATUS_URL)
                async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
                       async with  session.get(URI, timeout=self.REQUEST_TIMEOUT, headers=HTTP_HEADERS, allow_redirects=False) as resp:
                           response = await resp.text()
                           _LOGGER.debug("Login Load Call %s", response)
                           devices_dict = json.loads(response)
                           self.devices = devices_dict
                       await session.close()
        except asyncio.TimeoutError as error:
               _LOGGER.error("Timeout while calling %s: %s", self.LOCK_STATUS_URL, error)
               self.has_ping = False

    async def _change_lockstate(self, deviceId, lockState):
        data=f'''
{{
  "attributes": {{
    "lockState": {lockState}
  }}
}}
    '''

        HTTP_HEADERS = {"Authorization":f"Bearer {self._token}","x-api-key": self.apikey, "content-type": "application/json", "accept-encoding": "gzip", "user-agent": "okhttp/4.2.2" }                      
        try:
            
            with async_timeout.timeout(self._api_timeout):

                URI = "https://{}/{}".format(self.LOCK_STATE_URL,deviceId)
                async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
                       async with  session.put(URI, timeout=self.REQUEST_TIMEOUT, headers=HTTP_HEADERS, data=data, allow_redirects=False) as resp:
                           response = await resp.text()
                           _LOGGER.debug("Login Load Call %s", response)
                           print(response)
                       await session.close()
        except asyncio.TimeoutError as error:
               _LOGGER.error("Timeout while calling %s: %s", self.LOCK_STATE_URL, error)
               self.has_ping = False



    async def update(self):
        await self._get_token()
        await self._get_devices()
        device_states = {}
        for device in self.devices:
            device_state ={}
            device_state["lockState"] = bool(device['attributes']['lockState'])
            device_state["batteryLife"] = device['attributes']['batteryLevel']
            device_state["available"] = device['connected']
            device_states[device['deviceId']] = device_state
        self.states = device_states

    async def lock(self, deviceId):
        await self._change_lockstate(deviceId, 1)  

    async def unlock(self, deviceId):
        await self._change_lockstate(deviceId, 0)
        
    def devices(self):
        """Get device_id."""
        return self.devices
    
    def states(self):
        return self.states
