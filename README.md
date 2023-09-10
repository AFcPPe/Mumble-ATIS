# Mumble-ATIS

Mumble-ATIS is a Python solution that allows you to play Air Traffic Information Services (ATIS) in Mumble using the Opus audio codec.

## Usage

To use Mumble-ATIS, follow these steps:

1. Change the address of `data.json` and the Mumble Server (Murmur) address in the `newATIS.py` file.
2. Run the `newATIS.py` file.
3. When a user with an ATIS suffix connects to the server, Mumble-ATIS will read the information lines and connect to Murmur to play the corresponding sound.

## Supported Platforms

Mumble-ATIS supports the Advanced Flight Server, which is a closed-source solution developed by myself. It is authorized to be used with several flight simulation platforms, using Vatsim FSD protocol. The Advanced Flight Server provides comprehensive support for almost all Vatsim features. The pricing for the Advanced Flight Server is negotiable.
