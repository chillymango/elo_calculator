import uuid

import sqlalchemy as sa

from server.core.database import Base
from server.core.guid import GUID


class BaseModel(Base):
    __abstract__ = True
    uuid = sa.Column(GUID(), default=uuid.uuid4, primary_key=True)
