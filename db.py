from datetime import datetime
from typing import List

from sqlalchemy import (
    URL,
    VARCHAR,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from data.fake_data import (
    cities,
    contracts,
    provinces,
    vendor_information_evaluations,
    vendor_informations,
    vendor_selections,
    vendors,
)

MYSQL_DRIVER = "mysql+mysqlconnector"
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "M13121371m$"
MYSQL_HOST_NAME = "localhost"
MYSQL_PORT = 3306
DB_NAME = "digitalacquisitiondb"


url_object = URL.create(
    MYSQL_DRIVER,
    username=MYSQL_USERNAME,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST_NAME,
    port=MYSQL_PORT,
)
engine = create_engine(url_object)


with engine.connect() as conn:
    conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
    conn.execute(text(f"CREATE DATABASE {DB_NAME}"))

url_object = URL.create(
    MYSQL_DRIVER,
    username=MYSQL_USERNAME,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST_NAME,
    port=MYSQL_PORT,
    database=DB_NAME,
)

engine = create_engine(url_object)


class Base(DeclarativeBase):
    pass


class Province(Base):
    __tablename__ = "province"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(25))
    cities: Mapped[List["City"]] = relationship(back_populates="province")


class City(Base):
    __tablename__ = "city"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(20))
    province_id: Mapped[int] = mapped_column(ForeignKey("province.id"), nullable=False)
    province: Mapped["Province"] = relationship(back_populates="cities")
    vendorinformations: Mapped[List["VendorInformation"]] = relationship(
        back_populates="city"
    )


class Vendor(Base):
    __tablename__ = "vendor"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(50))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    vendorinformations: Mapped[List["VendorInformation"]] = relationship(
        back_populates="vendor"
    )
    contract: Mapped["Contract"] = relationship(back_populates="vendor")


class VendorInformation(Base):
    __tablename__ = "vendorinformation"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id"), nullable=False)
    vendor: Mapped["Vendor"] = relationship(back_populates="vendorinformations")
    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"), nullable=False)
    city: Mapped["City"] = relationship(back_populates="vendorinformations")
    address: Mapped[str] = mapped_column(Text())
    number_of_unique_products: Mapped[int] = mapped_column(Integer())
    mean_daily_sales: Mapped[float] = mapped_column(Float(), nullable=True)
    hygiene_score: Mapped[int] = mapped_column(Integer())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    vendorinformationevaluation: Mapped["VendorInformationEvaluation"] = relationship(
        back_populates="vendorinformation"
    )


class VendorInformationEvaluation(Base):
    __tablename__ = "vendorinformationevaluation"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    status: Mapped[str] = mapped_column(VARCHAR(10))
    vendorinformation_id: Mapped[int] = mapped_column(
        ForeignKey("vendorinformation.id")
    )
    vendorinformation: Mapped["VendorInformation"] = relationship(
        back_populates="vendorinformationevaluation"
    )
    vendorselection: Mapped["VendorSelection"] = relationship(
        back_populates="vendorinformationevaluation"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("vendorinformation_id"),)


class VendorSelection(Base):
    __tablename__ = "vendorselection"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    status: Mapped[str] = mapped_column(VARCHAR(10))
    vendorinformationevaluation_id: Mapped[int] = mapped_column(
        ForeignKey("vendorinformationevaluation.id"), nullable=False
    )
    vendorinformationevaluation: Mapped["VendorInformationEvaluation"] = relationship(
        back_populates="vendorselection"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("vendorinformationevaluation_id"),)


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id"), nullable=False)
    vendor: Mapped["Vendor"] = relationship(back_populates="contract")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("vendor_id"),)


Base.metadata.create_all(bind=engine)

###########################################
# INSERT DATA
###########################################
session = Session(engine)


###########################################
# INSERT PROVINCES
###########################################
for province in provinces:
    new_data = Province(
        id=province["id"],
        name=province["name"],
    )
    session.add(new_data)


###########################################
# INSERT CITIES
###########################################
for city in cities:
    new_data = City(
        id=city["id"],
        name=city["name"],
        province_id=city["province_id"],
    )
    session.add(new_data)


###########################################
# INSERT VENDORS
###########################################
for vendor in vendors:
    new_data = Vendor(
        id=vendor["id"],
        name=vendor["name"],
        is_active=vendor["is_active"],
    )
    session.add(new_data)


###########################################
# INSERT VENDOR INFORMATIONS
###########################################
for info in vendor_informations:
    new_data = VendorInformation(
        id=info["id"],
        vendor_id=info["vendor_id"],
        city_id=info["city_id"],
        address=info["address"],
        number_of_unique_products=info["number_of_unique_products"],
        mean_daily_sales=info["mean_daily_sales"],
        hygiene_score=info["hygiene_score"],
        created_at=info["created_at"],
    )
    session.add(new_data)


###########################################
# INSERT VENDOR INFORMATION EVALUATIONS
###########################################
for info in vendor_information_evaluations:
    new_data = VendorInformationEvaluation(
        id=info["id"],
        vendorinformation_id=info["vendor_information_id"],
        status=info["status"],
        created_at=info["created_at"],
        updated_at=info["updated_at"],
    )
    session.add(new_data)


###########################################
# INSERT VENDOR SELECTIONS
###########################################
for info in vendor_selections:
    new_data = VendorSelection(
        id=info["id"],
        vendorinformationevaluation_id=info["vendor_information_evaluation_id"],
        status=info["status"],
        created_at=info["created_at"],
        updated_at=info["updated_at"],
    )
    session.add(new_data)


###########################################
# INSERT CONTRACTS
###########################################
for contract in contracts:
    new_data = Contract(
        id=contract["id"],
        vendor_id=contract["vendor_id"],
        created_at=contract["created_at"],
    )
    session.add(new_data)


session.commit()
