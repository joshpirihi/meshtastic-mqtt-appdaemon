# python3.6

from portnums_pb2 import ENVIRONMENTAL_MEASUREMENT_APP, POSITION_APP
import random
import json

import mesh_pb2 as mesh_pb2
import mqtt_pb2 as mqtt_pb2
import environmental_measurement_pb2

from paho.mqtt import client as mqtt_client

import requests

import hassapi as hass

class MeshtasticMQTT(hass.Hass):

    #MQTT Broker details:
    broker = '10.147.253.250'
    port = 1883
    topic = "msh/1/c/#"
    # generate client ID with pub prefix randomly
    client_id = f'python-mqtt-{random.randint(0, 100)}'
    usename = 'user'
    password = 'pass'

    traccarHost = '10.147.253.250'


    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client


    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            se = mqtt_pb2.ServiceEnvelope()
            se.ParseFromString(msg.payload)
            
            print(se)
            mp = se.packet
            if mp.decoded.portnum == POSITION_APP:
                pos = mesh_pb2.Position()
                pos.ParseFromString(mp.decoded.payload)
                print(getattr(mp, "from"))
                print(pos)
                owntracks_payload = {
                    "_type": "location",
                    "lat": pos.latitude_i * 1e-7,
                    "lon": pos.longitude_i * 1e-7,
                    "tst": pos.time,
                    "batt": pos.battery_level,
                    "alt": pos.altitude
                }
                if owntracks_payload["lat"] != 0 and owntracks_payload["lon"] != 0:
                    #client.publish("owntracks/"+str(getattr(mp, "from"))+"/meshtastic_node", json.dumps(owntracks_payload))
                    if len(self.traccarHost) > 0:
                        traccarURL = "http://"+self.traccarHost+":5055?id="+str(getattr(mp, "from"))+"&lat="+str(pos.latitude_i * 1e-7)+"&lon="+str(pos.longitude_i * 1e-7)+"&altitude="+str(pos.altitude)+"&battery_level="+str(pos.battery_level)+"&hdop="+str(pos.PDOP)+"&accuracy="+str(pos.PDOP*0.03)
                        print(traccarURL)
                        submitted = requests.get(traccarURL)
                        print(submitted)
                #lets also publish the battery directly
                if pos.battery_level > 0:
                    client.publish("/mesh/"+str(getattr(mp, "from"))+"/battery", pos.battery_level)
            elif mp.decoded.portnum == ENVIRONMENTAL_MEASUREMENT_APP:
                env = environmental_measurement_pb2.EnvironmentalMeasurement()
                env.ParseFromString(mp.decoded.payload)
                print(env)
                client.publish("/mesh/"+str(getattr(mp, "from"))+"/temperature", env.temperature)
                client.publish("/mesh/"+str(getattr(mp, "from"))+"/relative_humidity", env.relative_humidity)
                
        client.subscribe(self.topic)
        client.on_message = on_message


    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_forever()

    def initialize(self):
        self.run()

#if __name__ == '__main__':
#    mm = MeshtasticMQTT()
#    mm.run()
