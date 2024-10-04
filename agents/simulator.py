from uagents import Model, Context, Agent
from uagents.setup import fund_agent_if_low
import json

class SimulationRequest(Model):
    coordinates: str


class SendCoordinates(Model):
    latitude: float
    longitude: float


AGENT_SEED = "simulation-agent-seed"
PORT = 8003
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit"
)

fund_agent_if_low(agent.wallet.address())


crash_detection_agent_address = "agent1qvyktesgt7sp8j99zmr2x49y04snqmn0gkd9zwcehak8u3jgdtc0xj8p8ve"


@agent.on_event("startup")
async def print_address(ctx: Context):
    ctx.logger.info(agent.address)
    ctx.storage.set('coordinates', None)
    ctx.storage.set("counter", 0)


@agent.on_query(model=SimulationRequest)
async def simulate_data(ctx: Context, sender: str, msg: SimulationRequest):
    ctx.logger.info(msg.coordinates)
    coordinates_list = json.loads(msg.coordinates)
    ctx.storage.set('coordinates', coordinates_list)


@agent.on_interval(period=2.0)
async def say_hello(ctx: Context):
    coords = ctx.storage.get('coordinates')
    count = ctx.storage.get('counter')
    if coords != None:
        ctx.logger.info(coords[count][0])
        ctx.logger.info(coords[count][1])
        latitude = coords[count][0]
        longitude = coords[count][1]
        await ctx.send(crash_detection_agent_address, SendCoordinates(latitude=latitude,longitude=longitude))
        count = count + 1
        ctx.storage.set('counter', count)



if __name__ == "__main__":
    agent.run()