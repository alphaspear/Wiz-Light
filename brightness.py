import sys
import asyncio
from pywizlight import wizlight, PilotBuilder

def main(): 

    ip = sys.argv[1]

    if sys.argv[2]=="25":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(brightness(ip,63))
    elif sys.argv[2]=="50":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(brightness(ip,127))
    elif sys.argv[2]=="75":
        loop3 = asyncio.get_event_loop()
        loop3.run_until_complete(brightness(ip,190))
    elif sys.argv[2]=="100":
        loop4 = asyncio.get_event_loop()
        loop4.run_until_complete(brightness(ip,255))


async def brightness(ip,value):
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(brightness = value))

if __name__ == "__main__":
    main()