from enum import Enum


class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class MaritalStatus(Enum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"


class Role(Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class TransactionStatus(Enum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class TransactionChannel(Enum):
    WEB = "WEB"
    MOBILE = "MOBILE"
    POS = "POS"
    OTHER = "OTHER"
