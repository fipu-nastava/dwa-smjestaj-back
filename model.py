from pony.orm import Database, PrimaryKey, Required, Set, db_session, Optional
from uuid import uuid4
import datetime as dt
from decimal import Decimal
import os


db = Database()

# ukoliko želiš da se svaki puta briše baza
# if os.path.exists("database.sqlite"):
#    os.remove("database.sqlite")

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)


class Unit(db.Entity):
    _table_ = "units"
    id = PrimaryKey(str, default=lambda: str(uuid4()))
    created_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    updated_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    name = Required(str)
    photo = Required(str)
    description = Required(str)
    max_persons = Required(int)
    unit_prices = Set("UnitPrice")
    unit_reservations = Set("Reservation")

class UnitPrice(db.Entity):
    _table_ = "unit_prices"
    id = PrimaryKey(str, default=lambda: str(uuid4()))
    created_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    updated_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    unit_id = Required(Unit)
    date_from = Required(dt.date)
    date_to = Required(dt.date)
    price = Required(Decimal)


class Reservation(db.Entity):
    _table_ = "reservations"
    id = PrimaryKey(str, default=lambda: str(uuid4()))
    created_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    updated_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    unit_id = Required(Unit)
    persons = Required(int)
    customer_email = Required(str)
    customer_name = Required(str)
    customer_address = Required(str)
    customer_country = Required(str)
    customer_phone = Required(str)
    reservation_days = Set("ReservationDay")


class ReservationDay(db.Entity):
    _table_ = "reservation_days"
    id = PrimaryKey(str, default=lambda: str(uuid4()))
    created_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    updated_at = Required(dt.datetime, default=lambda: dt.datetime.now())
    reservation_id = Required(Reservation)
    date = Required(dt.date)
    price = Required(Decimal)


db.generate_mapping(create_tables=True, check_tables=True)


if __name__ == "__main__":
    with db_session() as s:
        u = Unit(id="2", name="A", photo="OK", description="i", max_persons=2)
