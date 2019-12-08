import aiohttp
from . import RAT_ROOT

TARGET = "http://localhost:6543"


async def do_api_action(query: str, mode='GET'):
    async with aiohttp.ClientSession() as client:
        async with client.request(mode, query) as response:
            return await response.json()


async def find_rat(name: str):
    return await do_api_action(query=f"{RAT_ROOT}?[name:eq]={name}".format(
        target=TARGET))
