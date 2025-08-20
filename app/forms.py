from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SearchField
from wtforms.validators import DataRequired, Email, Optional
from wtforms_alchemy.fields import QuerySelectField
from wtforms_alchemy import ModelForm

from .models import *
from .helpers import subject_name

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class BuildingForm(FlaskForm, ModelForm):
  class Meta:
      model = Building
      


class PersonForm(FlaskForm, ModelForm):
    class Meta:
        model = Person


class CompanyForm(FlaskForm, ModelForm):
    class Meta:
        model = Company

class ContractTypeForm(FlaskForm, ModelForm):
    class Meta:
        model = ContractType


class ContractPointForm(FlaskForm, ModelForm):
    class Meta:
        model = ContractPoint


class ContractAnnexForm(FlaskForm, ModelForm):
    class Meta:
        model = ContractAnnex


class ContractImageForm(FlaskForm, ModelForm):
    class Meta:
        model = ContractImage


class ContractForm(FlaskForm, ModelForm):
    class Meta:
        model = Contract
        include_relationships = True
        include_foreign_keys = True
    
    seller = QuerySelectField("Seller", query_factory=lambda: Seller.query.all(), get_label=lambda s: subject_name(s.subject_id), allow_blank=True, blank_text='Select Seller')
    client = QuerySelectField("Client", query_factory=lambda: Client.query.all(), get_label=lambda c: subject_name(c.subject_id), allow_blank=True, blank_text='Select Client')


class PermissionForm(FlaskForm, ModelForm):
    class Meta:
        model = Permission
        include_relationships = True
        include_foreign_keys = True


class AssetForm(FlaskForm, ModelForm):
    class Meta:
        model = Asset
        include_relationships = True
        include_foreign_keys = True


class MaterialForm(FlaskForm, ModelForm):
    class Meta:
        model = Material
        include_relationships = True
        include_foreign_keys = True


class PlaceForm(FlaskForm, ModelForm):
    class Meta:
        model = Place
        include_relationships = True
        include_foreign_keys = True


class ServiceForm(FlaskForm, ModelForm):
    class Meta:
        model = Service
        include_relationships = True
        include_foreign_keys = True


