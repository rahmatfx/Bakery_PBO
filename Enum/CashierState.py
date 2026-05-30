from enum import IntEnum

class CashierState(IntEnum):
    HIDDEN       = 0
    SLIDING_IN   = 1
    WAITING      = 2
    DIALOGUE     = 3
    CAKE_SELECT  = 4
    ORDER_ACTIVE = 5
    REACTING     = 6