from sqlalchemy import Column, Integer, String, BigInteger, Numeric, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column("name", String)
    category = Column("category", BigInteger)
    price = Column("price", Numeric)
    description = Column("description", String)
    image_path = Column("image_path", String)
    producer = Column("producer", String)
    characteristics = Column("characteristics", JSON)
    quantity = Column("quantity", Integer)
