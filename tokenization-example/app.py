import requests
import base64

from flask import Flask
from flask import request
"""
This variable defines which port the test app is running at
"""
APPLICATION_PORT = 5000
"""
This defines which Midtrans API environment to target.
Set to `True` for production or `False` for Sandbox.
"""
IS_PRODUCTION = False

"""
Put your server key in this section accordingly to the environment
"""
server_key = {
    "sandbox": "sandbox-server-key",
    "production": "production-server-key"
}

host_url = {
    "sandbox": "https://app.sandbox.midtrans.com/v2",
    "production": "https://app.sandbox.midtrans.com/v2"
}

partner_endpoint = {
    "account_linking": "/pay/account",
    "enquire_account": "/pay/account/{}",
    "create_transaction": "/charge",
    "unlink_account": "/pay/account/{}/unbind"
}


def get_environment():
    return "production" if IS_PRODUCTION else "sandbox"


def generate_auth_header_value():
    key = base64.b64encode(bytes(server_key[get_environment()], 'utf-8'))
    return "Basic {}".format(key.decode("ascii"))


def prepare_headers(existing_headers, json=True):
    if json:
        existing_headers["Content-Type"] = "application/json"
    existing_headers["Accept"] = "application/json"
    existing_headers["Authorization"] = generate_auth_header_value()
    return existing_headers


app = Flask(__name__)


@app.route("/pay/account", methods=["POST"])
def link_account():
    body = request.json
    headers = prepare_headers(dict(request.headers))
    url = "{}{}".format(
        host_url[get_environment()],
        partner_endpoint["account_linking"]
    )
    response = requests.post(url=url, headers=headers, data=body)
    return response, response.status_code


@app.route("/pay/account/<account_id>", methods=["GET"])
def enquire_account(account_id):
    headers = prepare_headers(dict(request.headers), json=False)
    endpoint = partner_endpoint["enquire_account"].format(account_id)
    url = "{}{}".format(
        host_url[get_environment()],
        endpoint
    )
    response = requests.get(url=url, headers=headers)
    return response.json(), response.status_code


@app.route("/charge", methods=["POST"])
def create_transaction():
    body = request.json
    headers = prepare_headers(dict(request.headers))
    url = "{}{}".format(
        host_url[get_environment()],
        partner_endpoint["create_transaction"]
    )
    response = requests.post(url=url, headers=headers, data=body)
    return response.json(), response.status_code


@app.route("/pay/account/<account_id>/unbind", methods=["POST"])
def unlink_account(account_id):
    body = request.json
    headers = prepare_headers(dict(request.headers))
    endpoint = partner_endpoint["unlink_account"].format(account_id)
    url = "{}{}".format(
        host_url[get_environment()],
        endpoint
    )
    response = requests.post(url=url, headers=headers, data=body)
    return response.json(), response.status_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=APPLICATION_PORT)
