# meshtastic-mqtt-appdaemon

A fork of joshpirihi/meshtastic-mqtt that will run under AppDaemon

## Installation

Copy the contents of this repo to your `/config/appdaemon/apps/` folder in Home Assistant

Add the following entry to `apps.yaml`:
```
meshtastic-mqtt:
  module: "meshtastic-mqtt"
    class: MeshtasticMQTT
```