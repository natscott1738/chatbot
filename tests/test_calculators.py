from app.services.calculators import tbill_price, rediscount_proceeds

def test_tbill_price_discount():
    assert tbill_price(face=1000000, rate=0.12, days=91, convention="discount") == 970082.19

def test_tbill_price_yield():
    assert tbill_price(face=1000000, rate=0.12, days=91, convention="yield") == 972597.0

def test_rediscount_face():
    proceeds, method = rediscount_proceeds(face=1000000, price=None, rate=0.10, days_remaining=30)
    assert method == "from_face"
    assert proceeds == 991780.82

def test_rediscount_price():
    proceeds, method = rediscount_proceeds(face=None, price=980000, rate=0.10, days_remaining=30)
    assert method == "from_price"
    assert proceeds == 971543.84
