from typing import Literal

DAY_COUNT = 365

def tbill_price(face: float, rate: float, days: int, convention: Literal["discount", "yield"]) -> float:
    t = days / DAY_COUNT
    if convention == "discount":
        return round(face * (1 - rate * t), 2)
    else:
        return round(face / (1 + rate * t), 2)

def rediscount_proceeds(face: float | None, price: float | None, rate: float, days_remaining: int):
    t = days_remaining / DAY_COUNT
    if face is not None and price is None:
        return round(face * (1 - rate * t), 2), "from_face"
    if price is not None and face is None:
        return round(price * (1 - rate * t), 2), "from_price"
    raise ValueError("Provide either face or price, not both.")
