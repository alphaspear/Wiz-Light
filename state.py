import sys
import asyncio
from pywizlight import wizlight, PilotBuilder

def main(): 

    ip = sys.argv[1]

    if sys.argv[2]=="on":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(on(ip))
    else:
        loop2 = asyncio.get_event_loop()
        loop2.run_until_complete(off(ip))


async def off(ip):
    light = wizlight(ip)
    await light.turn_off()
    

async def on(ip):
    light = wizlight(ip)
    await light.turn_on(PilotBuilder())

if __name__ == "__main__":
    main()