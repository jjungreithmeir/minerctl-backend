# minerctl backend

In order to run this app you need `sqlite`, `virtualenv`, `make`, `python3-pip` and `python3` (this has been tested on 3.6.6). It is also recommended to run this application inside a virtual environment (with a virtualenv folder called `env`).

For the initial setup execute `make install`.

The backend confirms the identity of the frontend by checking the JWT signature of the frontend. To perform this check successfully the backend needs the public key of the frontend. The location of the key has to be configured in the config file named `config.ini`.

Run the flask JSON API with `make`.

## Future additions

Currently the backend has to run single-threaded because parallel route serving breaks the communication with the serial interface. It would probably be wise to change this behaviour to either lock the access to the serial interface or extract the serial interface access to an XMLRPC microservice that handles all serial requests. The current single-threaded execution -sadly- has severe performance impacts resulting in up to 2.5 times longer response times.
Additionally, it always helps to reduce the number of repeated accesses to the serial interface. So instead of requesting 120 miner states, I've added a method that returns all miner states which is more efficient even for requests that target a dozen miner states. This means the requests should be bundled on the microcontroller and requested/sent as one message.
