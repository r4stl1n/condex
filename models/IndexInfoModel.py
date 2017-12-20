from peewee import *

from models.BaseModel import BaseModel

class IndexInfoModel(BaseModel):
    Active = BooleanField()
    TotalBTCVal = DoubleField()
    TotalUSDVal = DoubleField()
    TotalRealizedGain = DoubleField()
    TotalUnrealizedGain = DoubleField()
    BalanceThreshold = DoubleField()
    OrderTimeout = IntegerField()
    OrderRetryAmount = IntegerField()
    RebalanceTickSetting = IntegerField()
