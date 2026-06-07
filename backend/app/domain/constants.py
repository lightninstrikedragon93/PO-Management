import enum

class RoleEnum(str, enum.Enum):
    REQUESTER = "requester"
    MANAGER = "manager"
    IT_REP = "it_rep"
    FINANCE = "finance"
    ADMIN = "admin"

class POStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_MANAGER = "PENDING_MANAGER"
    PENDING_IT = "PENDING_IT"
    PENDING_FINANCE = "PENDING_FINANCE"
    APPROVED = "APPROVED"
    NEEDS_REWORK = "NEEDS_REWORK"
    INVOICED = "INVOICED"

class POCategoryEnum(str, enum.Enum):
    SERVICES = "Services"
    OFFICE_SUPPLIES = "Office Supplies"
    IT_EQUIPMENT = "IT Equipment"