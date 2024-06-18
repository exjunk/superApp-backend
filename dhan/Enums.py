from enum import Enum
class Index(Enum):
    BANKNIFTY = 1  # 25
    NIFTY = 2  #13
    SENSEX = 3 #51
    FINNIFTY = 4 #27
    NIFTYFUT1 = 5 #5
    SENSEX_FUT = 6 # 859479 #May_expiry
    BANKNIFTY_FUT = 7 # 46923 May_expiry
    NIFTY_FUT = 8 # 46930 May_EXPIRY

class Option_Type(Enum):
    CE = 1
    PE = 2

class Order_status(Enum):
    TRANSIT = 1
    PENDING = 2
    REJECTED = 3
    CANCELLED = 4
    TRADED = 5
    EXPIRED = 6