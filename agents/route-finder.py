import requests
import json
from uagents import Model, Context, Agent
from uagents.setup import fund_agent_if_low


class RouteFinderRequest(Model):
    from_latitude: str
    from_longitude: str
    to_latitude: str
    to_longitude: str


class RouteFinderResponse(Model):
    coordinates: str


AGENT_SEED = "route-finder-agent-seed"
PORT = 8002
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

fund_agent_if_low(agent.wallet.address())


async def find_route(from_latitude, from_longitude, to_latitude, to_longitude):
    # Correct OSRM API URL format with longitude first
    osrm_url = "http://router.project-osrm.org/route/v1/driving/"
    route_url = f"{osrm_url}{from_longitude},{from_latitude};{to_longitude},{to_latitude}?overview=full&geometries=geojson"

    # Fetch the route from the OSRM API
    route_response = requests.get(route_url).json()

    # Extract the coordinates from the response
    coordinates = route_response['routes'][0]['geometry']['coordinates']

    return coordinates


@agent.on_event("startup")
async def print_address(ctx: Context):
    ctx.logger.info(agent.address)


@agent.on_query(model=RouteFinderRequest, replies={RouteFinderResponse})
async def get_route(ctx: Context, sender: str, msg: RouteFinderRequest):
    ctx.logger.info('Received message')
    ctx.logger.info(f"From: {msg.from_latitude}, {msg.from_longitude}")
    ctx.logger.info(f"To: {msg.to_latitude}, {msg.to_longitude}")

    # Fetch the route coordinates
    coordinates = await find_route(msg.from_latitude, msg.from_longitude, msg.to_latitude, msg.to_longitude)

    # Convert the coordinates list to a JSON string for transmission
    coordinates_str = json.dumps(coordinates)

    # Send the response back to the sender
    await ctx.send(sender, RouteFinderResponse(coordinates=coordinates_str))
    ctx.logger.info("Route sent successfully")


if __name__ == "__main__":
    agent.run()
