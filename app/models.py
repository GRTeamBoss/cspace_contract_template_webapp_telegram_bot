from collections import OrderedDict

from sqlalchemy import func
from sqlalchemy.inspection import inspect

from app import db

class BaseModel:
    def to_dict(self, include_relationships=False, backref_depth=1):
        data = OrderedDict()
        mapper = inspect(self.__class__)

        for column in mapper.columns:
            value = getattr(self, column.key)
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            data[column.key] = value

        if include_relationships and backref_depth > 0:
            for relationship in mapper.relationships:
                value = getattr(self, relationship.key)
                if value is None:
                    data[relationship.key] = None
                elif isinstance(value, list):
                    for item in value:
                        data[relationship.key] = item.to_dict(backref_depth=backref_depth-1)
                else:
                    data[relationship.key] = value.to_dict(backref_depth=backref_depth-1)
        return data

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.to_dict()}>"


class VersionModel:
    versions = None
    current_version = None

    def create_version(self, session, version_class):
        last_version = (session.query(func.max(version_class.version)).filter_by(original_id=self.id).scalar() or 0)
        data = {}
        for column in self.__table__.columns:
            if column.name not in ['id']:
                data[column.name] = getattr(self, column.name)
        new_version = version_class(original=self, current=self, version=last_version + 1, **data)
        session.add(new_version)


class TelegramID(db.Model, BaseModel):
    __tablename__ = 'telegram_id'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=True)
    username = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.Text, nullable=True)
    auth_date = db.Column(db.DateTime, nullable=False)
    hash_value = db.Column(db.Text, nullable=False)

    user = db.relationship('User', back_populates='telegramid')


class Role(db.Model, BaseModel):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    user = db.relationship('User', back_populates='role')
    permission = db.relationship('Permission', back_populates='role')


class User(db.Model, BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegramid_id = db.Column(db.Integer, db.ForeignKey('telegram_id.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)

    telegramid = db.relationship('TelegramID', back_populates='user')
    role = db.relationship('Role', back_populates='user')


class Permission(db.Model, BaseModel):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    name = db.Column(db.Text, nullable=False, unique=True)
    
    role = db.relationship('Role', back_populates='permission')


class Subject(db.Model, BaseModel):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=False)

    person = db.relationship('Person', back_populates='subject')
    company = db.relationship('Company', back_populates='subject')
    owner = db.relationship('Owner', back_populates='subject')
    seller = db.relationship('Seller', back_populates='subject')
    client = db.relationship('Client', back_populates='subject')
    building = db.relationship('Building', back_populates='subject')


class Person(db.Model, BaseModel):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    passport_id = db.Column(db.Text, nullable=False)
    personal_id = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    passport_given = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)

    subject = db.relationship('Subject', back_populates='person')


class Company(db.Model, BaseModel):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    legacy_name = db.Column(db.Text, nullable=False)
    stir = db.Column(db.Text, nullable=False)
    bank_account = db.Column(db.Text, nullable=False)
    bank_name = db.Column(db.Text, nullable=False)
    bank_mfo = db.Column(db.Text, nullable=False)
    bank_oked = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    director = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)

    subject = db.relationship('Subject', back_populates='company')


class Owner(db.Model, BaseModel):
    __tablename__ = 'owner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    subject = db.relationship('Subject', back_populates='owner')
    building = db.relationship('BuildingOwnerLink', back_populates='owner', uselist=False)


class Seller(db.Model, BaseModel):
    __tablename__ = 'seller'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    subject = db.relationship('Subject', back_populates='seller')
    building = db.relationship('BuildingSellerLink', back_populates='seller')
    client = db.relationship('SellerClientLink', back_populates='seller')
    asset = db.relationship('Asset', back_populates='seller')
    contract = db.relationship('Contract', back_populates='seller')
    contracttype = db.relationship('ContractTypeSellerLink', back_populates='seller')
    contractpoint = db.relationship('ContractPointSellerLink', back_populates='seller')
    contractimage = db.relationship('ContractImageSellerLink', back_populates='seller')
    contractannex = db.relationship('ContractAnnexSellerLink', back_populates='seller')


class Client(db.Model, BaseModel):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    subject = db.relationship('Subject', back_populates='client')
    contract = db.relationship('Contract', back_populates='client')
    seller = db.relationship('SellerClientLink', back_populates='client')

    
class Building(db.Model, BaseModel):
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    cadastre = db.Column(db.Text, nullable=False)

    subject = db.relationship('Subject', back_populates='building')
    owner = db.relationship('BuildingOwnerLink', back_populates='building')
    seller = db.relationship('BuildingSellerLink', back_populates='building')


class BuildingOwnerLink(db.Model, BaseModel):
    __tablename__ = 'building_owner_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)

    building = db.relationship('Building', back_populates='owner')
    owner = db.relationship('Owner', back_populates='building')


class BuildingSellerLink(db.Model, BaseModel):
    __tablename__ = 'building_seller_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)

    building = db.relationship('Building', back_populates='seller')
    seller = db.relationship('Seller', back_populates='building')


class SellerClientLink(db.Model, BaseModel):
    __tablename__ = 'seller_client_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    seller = db.relationship('Seller', back_populates='client', uselist=False)
    client = db.relationship('Client', back_populates='seller', uselist=False)


class Asset(db.Model, BaseModel):
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)

    seller = db.relationship('Seller', back_populates='asset')
    material = db.relationship('Material', back_populates='asset')
    place = db.relationship('Place', back_populates='asset')
    service = db.relationship('Service', back_populates='asset')


class Material(db.Model, BaseModel):
    __tablename__ = 'material'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)

    asset = db.relationship('Asset', back_populates='material')
    place = db.relationship('PlaceMaterialLink', back_populates='material')
    service = db.relationship('MaterialServiceLink', back_populates='material')

    
class Place(db.Model, BaseModel):
    __tablename__ = 'place'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    square = db.Column(db.Float, nullable=False)

    asset = db.relationship('Asset', back_populates='place')
    material = db.relationship('PlaceMaterialLink', back_populates='place')
    service = db.relationship('PlaceServiceLink', back_populates='place')

    
class Service(db.Model, BaseModel):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)

    asset = db.relationship('Asset', back_populates='service')
    material = db.relationship('MaterialServiceLink', back_populates='service')
    place = db.relationship('PlaceServiceLink', back_populates='service')


class PlaceMaterialLink(db.Model, BaseModel):
    __tablename__ = 'place_material_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)

    place = db.relationship('Place', back_populates='material')
    material = db.relationship('Material', back_populates='place')


class PlaceServiceLink(db.Model, BaseModel):
    __tablename__ = 'place_service_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    place = db.relationship('Place', back_populates='service')
    service = db.relationship('Service', back_populates='place')


class MaterialServiceLink(db.Model, BaseModel):
    __tablename__ = 'material_service_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    material = db.relationship('Material', back_populates='service')
    service = db.relationship('Service', back_populates='material')


class ContractType(db.Model, BaseModel):
    __tablename__ = 'contract_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    contract = db.relationship('ContractContractTypeLink', back_populates='contracttype')
    seller = db.relationship('ContractTypeSellerLink', back_populates='contracttype')

    
class ContractPoint(db.Model, BaseModel, VersionModel):
    __tablename__ = 'contract_point'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    number = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

    contract = db.relationship('ContractContractPointLink', back_populates='contractpoint')
    seller = db.relationship('ContractPointSellerLink', back_populates='contractpoint')
    contractimage = db.relationship('ContractPointContractImageLink', back_populates='contractpoint')

    versions = db.relationship('ContractPointVersion', foreign_keys='ContractPointVersion.original_id', back_populates='original', cascade="all, delete-orphan")
    current_version = db.relationship('ContractPointVersion', foreign_keys='ContractPointVersion.current_id', back_populates='current', uselist=False)


class ContractAnnex(db.Model, BaseModel, VersionModel):
    __tablename__ = 'contract_annex'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    number = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

    contract = db.relationship('ContractContractAnnexLink', back_populates='contractannex')
    seller = db.relationship('ContractAnnexSellerLink', back_populates='contractannex')
    contractimage = db.relationship('ContractAnnexContractImageLink', back_populates='contractannex')

    versions = db.relationship('ContractAnnexVersion', foreign_keys='ContractAnnexVersion.original_id', back_populates='original', cascade="all, delete-orphan")
    current_version = db.relationship('ContractAnnexVersion', foreign_keys='ContractAnnexVersion.current_id', back_populates='current', uselist=False)


class ContractImage(db.Model, BaseModel):
    __tablename__ = 'contract_image'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    byte = db.Column(db.Text, nullable=False)

    seller = db.relationship('ContractImageSellerLink', back_populates='contractimage')
    contractpoint = db.relationship('ContractPointContractImageLink', back_populates='contractimage')
    contractannex = db.relationship('ContractAnnexContractImageLink', back_populates='contractimage')


class Contract(db.Model, BaseModel):
    __tablename__ = 'contract'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)

    seller = db.relationship('Seller', back_populates='contract')
    client = db.relationship('Client', back_populates='contract')
    contracttype = db.relationship('ContractContractTypeLink', back_populates='contract')
    contractpoint = db.relationship('ContractContractPointLink', back_populates='contract')
    contractannex = db.relationship('ContractContractAnnexLink', back_populates='contract')


class ContractPointVersion(db.Model, BaseModel):
    __tablename__ = 'contract_point_version'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_id = db.Column(db.Integer, db.ForeignKey('contract_point.id'), nullable=False)
    current_id = db.Column(db.Integer, db.ForeignKey('contract_point.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)

    original = db.relationship('ContractPoint', foreign_keys=[original_id], back_populates='versions')
    current = db.relationship('ContractPoint', foreign_keys=[current_id], back_populates='current_version')


class ContractAnnexVersion(db.Model, BaseModel):
    __tablename__ = 'contract_annex_version'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_id = db.Column(db.Integer, db.ForeignKey('contract_annex.id'), nullable=False)
    current_id = db.Column(db.Integer, db.ForeignKey('contract_annex.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)

    original = db.relationship('ContractAnnex', foreign_keys=[original_id], back_populates='versions')
    current = db.relationship('ContractAnnex', foreign_keys=[current_id], back_populates='current_version')


class ContractContractTypeLink(db.Model, BaseModel):
    __tablename__ = 'contract_contract_type_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    contract_type_id = db.Column(db.Integer, db.ForeignKey('contract_type.id'), nullable=False)

    contract = db.relationship('Contract', back_populates='contracttype')
    contracttype = db.relationship('ContractType', back_populates='contract')


class ContractContractPointLink(db.Model, BaseModel):
    __tablename__ = 'contract_contract_point_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    contract_point_id = db.Column(db.Integer, db.ForeignKey('contract_point.id'), nullable=False)

    contract = db.relationship('Contract', back_populates='contractpoint')
    contractpoint = db.relationship('ContractPoint', back_populates='contract')

    
class ContractContractAnnexLink(db.Model, BaseModel):
    __tablename__ = 'contract_contract_annex_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    contract_annex_id = db.Column(db.Integer, db.ForeignKey('contract_annex.id'), nullable=False)

    contract = db.relationship('Contract', back_populates='contractannex')
    contractannex = db.relationship('ContractAnnex', back_populates='contract')


class ContractTypeSellerLink(db.Model, BaseModel):
    __tablename__ = 'contract_type_seller_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_type_id = db.Column(db.Integer, db.ForeignKey('contract_type.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)

    contracttype = db.relationship('ContractType', back_populates='seller')
    seller = db.relationship('Seller', back_populates='contracttype')


class ContractPointSellerLink(db.Model, BaseModel):
    __tablename__ = 'contract_point_seller_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_point_id = db.Column(db.Integer, db.ForeignKey('contract_point.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)

    contractpoint = db.relationship('ContractPoint', back_populates='seller')
    seller = db.relationship('Seller', back_populates='contractpoint')


class ContractAnnexSellerLink(db.Model, BaseModel):
    __tablename__ = 'contract_annex_seller_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_annex_id = db.Column(db.Integer, db.ForeignKey('contract_annex.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)

    contractannex = db.relationship('ContractAnnex', back_populates='seller')
    seller = db.relationship('Seller', back_populates='contractannex')

class ContractImageSellerLink(db.Model, BaseModel):
    __tablename__ = 'contract_image_seller_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_image_id = db.Column(db.Integer, db.ForeignKey('contract_image.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)

    contractimage = db.relationship('ContractImage', back_populates='seller')
    seller = db.relationship('Seller', back_populates='contractimage')


class ContractPointContractImageLink(db.Model, BaseModel):
    __tablename__ = 'contract_point_contract_image_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_point_id = db.Column(db.Integer, db.ForeignKey('contract_point.id'), nullable=False)
    contract_image_id = db.Column(db.Integer, db.ForeignKey('contract_image.id'), nullable=False)

    contractimage = db.relationship('ContractImage', back_populates='contractpoint')
    contractpoint = db.relationship('ContractPoint', back_populates='contractimage')


class ContractAnnexContractImageLink(db.Model, BaseModel):
    __tablename__ = 'contract_annex_contract_image_link'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_annex_id = db.Column(db.Integer, db.ForeignKey('contract_annex.id'), nullable=False)
    contract_image_id = db.Column(db.Integer, db.ForeignKey('contract_image.id'), nullable=False)

    contractannex = db.relationship('ContractAnnex', back_populates='contractimage')
    contractimage = db.relationship('ContractImage', back_populates='contractannex')
