# minerctl backend

In order to run this app you need `sqlite` and `virtualenv`.

For the initial setup execute `make install`.

The backend confirms the identity of the frontend by checking the JWT signature of the frontend. To perform this check successfully the backend needs the public key of the frontend. The location of the key has to be configured in the config file named `config.ini`.

Run the flask JSON API with `make`.
