import sys
import asyncio
from pywizlight import wizlight, PilotBuilder

def main(): 

    ip = sys.argv[1]

    if sys.argv[2]=="4":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scene(ip,4))
    elif sys.argv[2]=="5":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(scene(ip,5))
    elif sys.argv[2]=="18":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(scene(ip,18))
    elif sys.argv[2]=="23":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(scene(ip,23))
    elif sys.argv[2]=="27":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(scene(ip,27))
    elif sys.argv[2]=="28":
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(scene(ip,28))
    


async def scene(ip,value):
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(scene = value))

if __name__ == "__main__":
    main()