from uagents import Model, Context, Agent
from uagents.setup import fund_agent_if_low
import json
from datetime import datetime  # Import datetime module


class SendCoordinates(Model):
    latitude: float
    longitude: float


class SendCrashInfo(Model):
    impact: float

class Notify(Model):
    message: str

AGENT_SEED = "crash-detection-agent-seed"
PORT = 8004
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit"
)

fund_agent_if_low(agent.wallet.address())
notify_agent_address="agent1qgh435x6ame9tz3qqzv66hqvqf44djywcxvmyjwm9t0k7h6akj0ccw77gv4"

@agent.on_event("startup")
async def print_address(ctx: Context):
    ctx.logger.info(agent.address)
    ctx.storage.set('latitude', None)
    ctx.storage.set('longitude', None)
    ctx.storage.set('crash_data', {})  # Initialize crash data storage


@agent.on_message(model=SendCoordinates)
async def simulate_data(ctx: Context, sender: str, msg: SendCoordinates):
    ctx.logger.info(msg.latitude)
    ctx.logger.info(msg.longitude)

    ctx.storage.set('latitude', msg.latitude)
    ctx.storage.set('longitude', msg.longitude)


@agent.on_message(model=SendCrashInfo)
async def simulate_data(ctx: Context, sender: str, msg: SendCrashInfo):
    ctx.logger.info(msg.impact)

    # Capture the current date and time as a single datetime object
    crash_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format datetime for JSON storage

    crash_impact = msg.impact
    crash_latitude = ctx.storage.get('latitude')
    crash_longitude = ctx.storage.get('longitude')

    # Create the JSON object with crash data
    crash_data = {
        "crash_impact": crash_impact,
        "crash_latitude": crash_latitude,
        "crash_longitude": crash_longitude
    }

    # Retrieve existing crash data (if any) and update it
    existing_data = ctx.storage.get('crash_data')
    if existing_data is None:
        existing_data = {}

    # Store the crash data against the crash_datetime
    existing_data[crash_datetime] = crash_data
    ctx.storage.set('crash_data', existing_data)

    ctx.logger.info(f"Crash recorded at {crash_datetime} with data: {crash_data}")

    # Dummy vehicle number
    vehicle_number = "XYZ1234"

    # Frame the dummy message with a disclaimer
    dummy_message = (
        f"DISCLAIMER: This is a dummy message. No actual crash has occurred."
        f"A crash has been detected with vehicle {vehicle_number}.\n"
        f"Impact: {crash_impact}.\n"
        f"Location: {crash_latitude}, {crash_longitude}.\n"
        f"Time: {crash_datetime}.\n"
        f"Please check on the driver immediately!\n\n"
    )


    await ctx.send(notify_agent_address, Notify(message=dummy_message))


if __name__ == "__main__":
    agent.run()
