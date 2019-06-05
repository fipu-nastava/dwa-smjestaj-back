from flask import Flask, Response, jsonify, request
from flask.json import JSONEncoder
import datetime as dt
from domain import Units, UnitPrices, Reservations
from decimal import Decimal
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def error(status=500, text="An error happened"):
    return jsonify({"error": text}), status

def handle_get_post(request, Class):
    if request.method == "POST":
        data = request.get_json()
        id_ = Class.create(data)
        if id_ is None:
            return error()

        r = Response(status=201)
        r.headers["Location"] = f"/unit/{id_}"
        return r
    elif request.method == "GET":
        units = Class.listall()
        if units is None:
            return error()

        return jsonify({"data": units})

def handle_get_put_delete(request, Class, id_):
    if request.method == "GET":
        data = Class.get(id_)
        if data is None:
            return error(404, "Not found")
        return jsonify({"data": data})
    elif request.method == "DELETE":
        response = Class.delete(id_)
        if response is None:
            return error()
        return Response(status=202)
    elif request.method == "PUT":
        data = request.get_json()
        if data is None or "id" not in data or id_ != data["id"]:
            return error(400, "Non-matching 'id' in body and URL")
        response = Class.update(data)
        if response is None:
            return error()
        return Response(status=202)


@app.route("/", methods=["GET"])
def main():
    r = Response(status=200)
    r.set_data("Welcome to Booking REST API")
    return r


@app.route("/unit/<id_>", methods=["GET", "PUT", "DELETE"])
def unit_read_id(id_):
    return handle_get_put_delete(request, Units, id_)


@app.route("/unit", methods=["GET", "POST"])
def unit_read_new():
    return handle_get_post(request, Units)


@app.route("/unit/<unit_id>/unit-prices/<id_>", methods=["GET", "PUT", "DELETE"])
def unit_prices_read_id(unit_id, id_):
    if request.method == "PUT":
        data = request.get_json()
        if not unit_id == data["unit_id"]:
            return error(400, "Non-matching 'unit_id' in body and URL")
    return handle_get_put_delete(request, UnitPrices, id_)


@app.route("/unit/<unit_id>/unit-prices", methods=["GET", "POST"])
def unit_prices_read_new(unit_id):
    if request.method == "GET":
        if not unit_id:
            return error(400, "Missing 'unit_id'")
        data = UnitPrices.listall(unit_id)
        return jsonify({"data": data})
    elif request.method == "POST":
        data = request.get_json()
        if not unit_id == data["unit_id"]:
            return error(400, "Non-matching 'unit_id' in body and URL")
    return handle_get_post(request, UnitPrices)


@app.route("/unit/<unit_id>/get-blocked-days", methods=["GET"])
def get_blocked_days(unit_id):
    date_from = request.args.get("date_from", type=str)
    date_to = request.args.get("date_to", type=str)
    if date_from is None or date_to is None:
        return error(400, "Missing params 'date_from' and 'date_to'")
    date_from = dt.datetime.strptime(date_from, "%Y-%m-%d").date()
    date_to = dt.datetime.strptime(date_to, "%Y-%m-%d").date()

    retval = Units.get_blocked_days(unit_id, date_from, date_to)
    return jsonify({"data": retval})


@app.route("/unit/<unit_id>/calculate-price", methods=["GET"])
def get_price(unit_id):
    date_from = request.args.get("date_from", type=str)
    date_to = request.args.get("date_to", type=str)
    if date_from is None or date_to is None:
        return error(400, "Missing params 'date_from' and 'date_to'")
    date_from = dt.datetime.strptime(date_from, "%Y-%m-%d").date()
    date_to = dt.datetime.strptime(date_to, "%Y-%m-%d").date()

    retval = UnitPrices.calculate(unit_id, date_from, date_to)
    return jsonify({"data": retval})


@app.route("/unit/<unit_id>/reserve", methods=["POST"])
def reserve(unit_id):
    data = request.get_json()
    data["unit_id"] = unit_id
    status = Reservations.reserve(data)
    if status is not True:
        return error()
    return Response(status=202)


# serijaliziraj datume u ISO formatu
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, dt.date) or isinstance(obj, dt.datetime):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
