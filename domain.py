from pony.orm import db_session, select
import logging
from model import Unit, UnitPrice, Reservation, ReservationDay
import datetime as dt
from collections import deque
from decimal import Decimal

class Base:
    @classmethod
    @db_session()
    def get(cls, id_):
        try:
            unit = cls.model_class[id_]
            return unit.to_dict()
        except Exception as e:
            logging.exception("Error getting by id")

    @classmethod
    @db_session()
    def delete(cls, id_):
        try:
            cls.model_class[id_].delete()
            return True
        except Exception as e:
            logging.exception("Error deleting data")

    @classmethod
    @db_session()
    def create(cls, data):
        try:
            unit = cls.model_class(**data)
            return unit.id
        except Exception as e:
            logging.exception("Error saving data")

    @classmethod
    @db_session()
    def update(cls, data):
        try:
            data["updated_at"] = dt.datetime.now()
            unit = cls.model_class[data["id"]]
            unit.set(**data)
            return True
        except Exception as e:
            logging.exception("Error saving data")

    @classmethod
    @db_session()
    def listall(cls):
        try:
            units = select(u for u in cls.model_class)
            return [u.to_dict() for u in units]
        except Exception as e:
            logging.exception("Error saving data")


class Units(Base):
    model_class = Unit

    @classmethod
    @db_session()
    def get_blocked_days(cls, unit_id, date_from, date_to):
        try:
            rds = select(str(rd.date) for r in Reservation for rd in r.reservation_days
                         if r.unit_id.id == unit_id and
                         date_from <= rd.date and
                         date_to >= rd.date)
            return [d for d in rds]
        except Exception as e:
            logging.exception("Error saving data")


class UnitPrices(Base):
    model_class = UnitPrice

    @db_session()
    def listall(unit_id):
        try:
            units = select(u for u in UnitPrice if u.unit_id.id == unit_id)
            return [u.to_dict() for u in units]
        except Exception as e:

            logging.exception("Error saving data")

    @db_session()
    def calculate(unit_id, date_from, date_to):
        try:
            if date_from > date_to:
                raise Exception("Invalid dates")
            rules = select((up.date_from, up.date_to, up.price) for up in UnitPrice
                           if unit_id == up.unit_id.id and up.date_to >= date_from and up.date_from <= date_to).order_by("date_from")
            prices = rules[:]
            total = Decimal("0.00")
            breakdown = []
            if len(prices):
                deq = deque(prices)
                min_date_to = None
                while len(deq) > 0 and min_date_to != date_to:
                    cur_from, cur_to, price = deq.popleft()
                    price = Decimal(price)
                    min_date_to = min(cur_to, date_to)
                    max_date_from = max(cur_from, date_from)
                    print(f"{max_date_from} --> {min_date_to} = {price}")
                    days = (min_date_to - max_date_from).days + 1
                    print(f"{days} days at {price}kn")
                    total += days * price
                    breakdown.append({"date_from": max_date_from, "date_to": min_date_to, "price": price, "days": days,
                                      "total": "%.2f" % (days * price)})
            
            if total == 0:
                return None
            else:
                return {"breakdown": breakdown, "total": "%.2f" % total}

        except Exception as e:
            logging.exception("Error in calculating price")


class Reservations(Base):
    model_class = Reservation

    @db_session()
    def reserve(data):
        try:
            if "date_from" not in data or "date_to" not in data:
                raise Exception("Missing dates")

            date_from = dt.datetime.strptime(data["date_from"], "%Y-%m-%d").date()
            date_to = dt.datetime.strptime(data["date_to"], "%Y-%m-%d").date()
            del data["date_from"]
            del data["date_to"]
                
            r = Reservation(**data)

            delta = date_to - date_from
            for i in range(delta.days):
                date = date_from + dt.timedelta(days=i)
                ReservationDay(reservation_id=r.id, date=date, price=0)

            return True
        except Exception as e:
            logging.exception("Error saving data")

