import sys
import asyncio
from pywizlight import wizlight, PilotBuilder

def main(): 

    ip = sys.argv[1]

    if sys.argv[2]=="warmwhite":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(warm(ip))

    elif sys.argv[2]=="coolwhite":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(cool(ip))


    elif sys.argv[2]=="red":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(color(ip,255,0,0))

    elif sys.argv[2]=="blue":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(color(ip,0,0,255))

    elif sys.argv[2]=="green":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(color(ip,0,255,0))


async def color(ip,r,g,b):
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(rgb = (r,g,b)))

async def warm(ip):
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(warm_white = 255))

async def cool(ip):
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(cold_white = 255))

if __name__ == "__main__":
    main()