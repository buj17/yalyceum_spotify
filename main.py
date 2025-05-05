from db import create_session
from sqlalchemy import text

session = create_session()
print(session.execute(text('SHOW TABLES')).fetchall())

