import requests
import json
from uagents import Model, Context, Agent
from uagents.setup import fund_agent_if_low
import os
from dotenv import load_dotenv


load_dotenv()

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")


class Location(Model):
    address: str


class Location_Response(Model):
    latitude: str
    longitude: str


AGENT_SEED = "geolocation-agent-seed"
PORT = 8001
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(agent.wallet.address())


@agent.on_event("startup")
async def print_address(ctx: Context):
    ctx.logger.info(agent.address)


async def find_Locations(ctx, address):
    ctx.logger.info('Request received')
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": address,
        "key": OPENCAGE_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            # location_data = {
            #     "latitude": data['results'][0]['geometry']['lat'],
            #     "longitude": data['results'][0]['geometry']['lng']
            # }
        else:
            location_data = {"error": "Address not found"}
    else:
        location_data = {"error": "Failed to connect to API"}

    return latitude, longitude


@agent.on_query(model=Location, replies={Location_Response})
async def get_repo_names(ctx: Context, sender: str, msg: Location):
    ctx.logger.info('Received message')
    ctx.logger.info(msg.address)

    lat, lon = await find_Locations(ctx, msg.address)
    ctx.logger.info(lat)
    await ctx.send(sender, Location_Response(latitude=lat, longitude=lon))
    ctx.logger.info("---------")


if __name__ == "__main__":
    agent.run()