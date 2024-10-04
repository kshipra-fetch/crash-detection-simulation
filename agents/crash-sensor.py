
from uagents import Model, Context, Agent
from uagents.setup import fund_agent_if_low
import json

class SendCrashInfo(Model):
    impact: float

class CrashSimulationReq(Model):
    message:str


crash_detection_agent_address="agent1qvyktesgt7sp8j99zmr2x49y04snqmn0gkd9zwcehak8u3jgdtc0xj8p8ve"

AGENT_SEED = "crash-sensor-agent-seed"
PORT = 8005
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit"
)

fund_agent_if_low(agent.wallet.address())


@agent.on_event("startup")
async def print_address(ctx: Context):
    ctx.logger.info(agent.address)


@agent.on_query(model=CrashSimulationReq)
async def simulate_crash(ctx: Context, sender: str, msg: CrashSimulationReq):
    ctx.logger.info(msg.message)
    await ctx.send(crash_detection_agent_address, SendCrashInfo(impact=0.75))




if __name__ == "__main__":
    agent.run()