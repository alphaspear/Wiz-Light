import asyncio

from pywizlight import wizlight, PilotBuilder, discovery

async def main():
    bulbs = await discovery.discover_lights(broadcast_space="192.168.29.189")
    light = wizlight("192.168.29.189")
    await light.turn_on(PilotBuilder())
    await light.turn_on(PilotBuilder(brightness = 255))
    await light.turn_on(PilotBuilder(warm_white = 255))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
