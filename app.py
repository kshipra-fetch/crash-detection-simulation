from flask import Flask, request, jsonify, render_template
from uagents.envelope import Envelope
from uagents import Model
from uagents.query import query
import json

app = Flask(__name__)

class Location(Model):
    address: str

class Location_Response(Model):
    latitude: str
    longitude:str

class RouteFinderRequest(Model):
    from_latitude: str
    from_longitude:str
    to_latitude: str
    to_longitude:str

class RouteFinderResponse(Model):
    coordinates:str

class SimulationRequest(Model):
    coordinates: str

class CrashSimulationReq(Model):
    message:str



geolocation_agent_address="agent1qdwpgnr8gltg39ev9ej2smvxlpr0dt4d34ndcdw9q6xm2wup78kesd4mjcf"
route_finder_agent_address="agent1qw0xtgsr0wjvkfwq2c6wvqyq7p6c8y6c6unrnhuq0dglkvvxdfnscfz2qcu"
simulator_agent_address="agent1qvrw7apdk4tuwv3xd55k9sak5qtekj8y3hguaj09genm5d06n9htudurhxs"
crash_sensor_agent_address="agent1qd2d7ausuhjywa2t9fjpy2jl6la7h6z00uyskxrvkptr8mzuwk565xfscy7"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_route', methods=['POST'])
async def get_route():
    address1 = request.form['address1']
    address2 = request.form['address2']

    try:
        # Query geolocation agent for address 1
        print("Sending address 1 to geolocation agent")
        response = await query(geolocation_agent_address, message=Location(address=address1),timeout=15.0)
        print(f"Response for address 1: {response}")

        if isinstance(response, Envelope):
            data = json.loads(response.decode_payload())
            from_latitude = data.get('latitude', '')
            from_longitude = data.get('longitude', '')
            print(f'from latitude : {from_latitude}')
            print(f'from longitude : {from_longitude}')

        # Query geolocation agent for address 2
        print("Sending address 2 to geolocation agent")
        response = await query(geolocation_agent_address, message=Location(address=address2), timeout=15.0)
        print(f"Response for address 2: {response}")

        if isinstance(response, Envelope):
            data = json.loads(response.decode_payload())
            to_latitude = data.get('latitude', '')
            to_longitude = data.get('longitude', '')
            print(f'to latitude : {to_latitude}')
            print(f'to longitude : {to_longitude}')

        # Query route finder agent
        print("Sending query to route finder")
        response = await query(route_finder_agent_address, message=RouteFinderRequest(from_latitude=from_latitude, from_longitude=from_longitude, to_latitude=to_latitude, to_longitude=to_longitude), timeout=15.0)
        print(f"Response from route finder: {response}")

        if isinstance(response, Envelope):
            data = json.loads(response.decode_payload())
            coordinates = data.get('coordinates', '')
            print(f"Route coordinates: {coordinates}")

        print('Sending query to simulation agent')
        await query(simulator_agent_address, message=SimulationRequest(coordinates=str(coordinates)), timeout=15.0)

        return jsonify({
            "coordinates": coordinates  # Convert coordinates list to JSON string
        })

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/simulate_crash', methods=['POST'])
async def simulate_crash():
    try:
        print('Sending crash simulation to simulation agent')
        await query(crash_sensor_agent_address, message=CrashSimulationReq(message='simulate crash'), timeout=15.0)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
