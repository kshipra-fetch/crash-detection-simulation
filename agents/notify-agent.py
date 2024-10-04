from uagents import Model, Context, Agent
from uagents.setup import fund_agent_if_low
import requests
import json
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv


load_dotenv()

CLICKSEND_USERNAME=os.getenv('CLICKSEND_USERNAME')
CLICKSEND_API_KEY=os.getenv('CLICKSEND_API_KEY')

class Notify(Model):
    message: str

AGENT_SEED = "notify-agent-seed"
PORT = 8006
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit"
)

fund_agent_if_low(agent.wallet.address())


async def notify_family(message):
    username = os.getenv("CLICKSEND_USERNAME")
    api_key = os.getenv("CLICKSEND_API_KEY")

    # The ClickSend SMS API URL
    url = 'https://rest.clicksend.com/v3/sms/send'

    # The payload containing the message details
    payload = {
        "messages": [
            {
                "source": "python",
                "body": message,
                "to": "+44999999999",
                "from": "PythonApp"
            }
        ]
    }

    # Send the POST request to the ClickSend API
    response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'},
                             auth=HTTPBasicAuth(username, api_key))

    # Check if the request was successful
    if response.status_code == 200:
        print('Message sent successfully!')
        print(response.json())
    else:
        print(f'Failed to send message. Status code: {response.status_code}')
        print(response.json())


@agent.on_event("startup")
async def print_address(ctx: Context):
    ctx.logger.info(agent.address)

@agent.on_message(model=Notify)
async def send_message(ctx: Context, sender: str, msg: Notify):
    response = await notify_family(msg.message)



if __name__ == "__main__":
    agent.run()
