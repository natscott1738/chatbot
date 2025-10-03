from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal
from app.services.calculators import tbill_price, rediscount_proceeds

router = APIRouter()

class TBillPriceRequest(BaseModel):
    face: float = Field(gt=0)
    rate: float = Field(ge=0, le=1)
    days: int = Field(gt=0, le=366)
    convention: Literal["discount", "yield"]

class TBillPriceResponse(BaseModel):
    price: float
    inputs: TBillPriceRequest

class RediscountRequest(BaseModel):
    face: float | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, gt=0)
    rate: float = Field(ge=0, le=1)
    days_remaining: int = Field(gt=0, le=366)

class RediscountResponse(BaseModel):
    proceeds: float
    method: Literal["from_face", "from_price"]

@router.post("/calc/tbill/price", response_model=TBillPriceResponse)
def calc_tbill_price(req: TBillPriceRequest):
    price = tbill_price(req.face, req.rate, req.days, req.convention)
    return TBillPriceResponse(price=price, inputs=req)

@router.post("/calc/rediscount", response_model=RediscountResponse)
def calc_rediscount(req: RediscountRequest):
    proceeds, method = rediscount_proceeds(req.face, req.price, req.rate, req.days_remaining)
    return RediscountResponse(proceeds=proceeds, method=method)
