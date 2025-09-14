from functools import wraps
import re
from urllib.parse import urlparse, unquote_plus, parse_qs
import json

from flask import request, session, redirect, url_for, Response
from sqlalchemy import event, inspect
from sqlalchemy.ext.declarative import declarative_base

from app import db
from .models import *

model_dict = {
    "telegramid": TelegramID,
    "role": Role,
    "user": User,
    "permission": Permission,
    "subject": Subject,
    "person": Person,
    "company": Company,
    "owner": Owner,
    "seller": Seller,
    "client": Client,
    "building": Building,
    "buildingownerlink": BuildingOwnerLink,
    "buildingsellerlink": BuildingSellerLink,
    "sellerclientlink": SellerClientLink,
    "asset": Asset,
    "material": Material,
    "place": Place,
    "service": Service,
    "placemateriallink": PlaceMaterialLink,
    "placeservicelink": PlaceServiceLink,
    "materialservicelink": MaterialServiceLink,
    "contracttype": ContractType,
    "contractpoint": ContractPoint,
    "contractannex": ContractAnnex,
    "contractimage": ContractImage,
    "contract": Contract,
    "contractpointversion": ContractPointVersion,
    "contractannexversion": ContractAnnexVersion,
    "contractcontracttypelink": ContractContractTypeLink,
    "contractcontractpointlink": ContractContractPointLink,
    "contractcontractannexlink": ContractContractAnnexLink,
    "contracttypesellerlink": ContractTypeSellerLink,
    "contractpointsellerlink": ContractPointSellerLink,
    "contractannexsellerlink": ContractAnnexSellerLink,
    "contractimagesellerlink": ContractImageSellerLink,
    "contractpointcontractimagelink": ContractPointContractImageLink,
    "contractannexcontractimagelink": ContractAnnexContractImageLink,
}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

 
def approve_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_approved'):
            return redirect(url_for('user.user_login'))
        return f(*args, **kwargs)
    return decorated_function


def versioning_listener(mapper, connection, target):
    session = db.session.object_session(target)
    version_class_name = target.__class__.__name__ + 'Version'
    version_class = globals().get(version_class_name)
    target.create_version(session, version_class)


def params_valid(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PATCH", "PUT", "DELETE"]:
            path = urlparse(request.url).path
            params = parse_qs(unquote_plus(urlparse(request.url).query))
            format_key = params.get("format", None)
            missing_key = {"status": 403, "missing_keys": []}
            if format_key is None:
                missing_key = {"status": 403, "missing_keys": ["format"]}
                return Response(json.dumps(missing_key), mimetype="application/json"), 403
            else:
                if format_key[0] == "json":
                    params = request.get_json(silent=True)
                elif format_key[0] == "params":
                    pass
                else:
                    missing_key = {"status": 403, "keys": ["format"], "wrong_value": format_key, "reason": "wrong_value"}
                    return Response(json.dumps(missing_key), mimetype="application/json"), 403
            match request.method:
                case "POST":
                    match path:
                        case "/api/models":
                            table_name = params.get("table", None)
                            column = params.get("column", None)
                            column_type= params.get("column_type", None)
                            ref = params.get("ref", None)
                            if table_name is None: missing_key["missing_keys"].append("table")
                            if column is None: missing_key["missing_keys"].append("column")
                            if column_type is None: missing_key["missing_keys"].append("column_type")
                            if ref is None: missing_key["missing_keys"].append("ref")
                            if any((column_type, ref)) is False:
                                if column is not None:
                                    if table_name is None:
                                        return Response(json.dumps(missing_key), mimetype="application/json"), 403
                                    if column[0].count(".") == 2:
                                        _, _, ref_id = column[0].split(".", 2)
                                        if ref_id == "None":
                                            pass
                                        else:
                                            return Response(json.dumps({"status": 403, "keys": ["column"], "wrong_value": column, "reason": "<ref> should have ID like User.int.Role.id"})), 403
                                    else:
                                        if column[0].count(".") == 3:
                                            return f(*args, **kwargs)
                                        elif column[0].count(".") == 0:
                                            return Response(json.dumps(missing_key), mimetype="application/json"), 403
                                        else:
                                            return Response(json.dumps({"status": 403, "keys": ["column"], "wrong_value": column, "reason": "for feature request <column> key should contain in each value only 2 dots! with <ref> only 3"})), 403
                                else:
                                    return Response(json.dumps(missing_key), mimetype="application/json"), 403
                            else:
                                if column is not None:
                                    if table_name is None:
                                        return Response(json.dumps(missing_key), mimetype="application/json"), 403
                                    if len(column) == len(column_type) and len(column) == len(ref_id):
                                        pass
                                    else:
                                        return Response(json.dumps({"status": 403, "keys": ["column", "column_type", "ref"], "reason": "value lengths not matched to each other."}), mimetype="application/json"), 403
                                else:
                                    return Response(json.dumps(missing_key), mimetype="application/json"), 403
                        case _ if re.match(r"/api/model/[\w]*", path):
                            column = params.get("column", None)
                            value = params.get("value", None)
                            if all((column, value)) is False:
                                if column is not None:
                                    if column[0].count(".") == 1:
                                        pass
                                    else:
                                        return Response(json.dumps(missing_key), mimetype="application/json"), 403
                                else:
                                    return Response(json.dumps(missing_key), mimetype="application/json"), 403
                            else:
                                if len(column) == len(value):
                                    pass
                                else:
                                    return Response(json.dumps({"status": 403, "keys": ["column", "value"], "reason": "value lengths not matched to each other."}), mimetype="application/json"), 403
                        case _:
                            return Response(json.dumps({"status": 403, "path": path, "reason": "unavailable path to this method"})), 403
                case "PUT":
                    match path:
                        case _ if re.match(r"/api/model/[\w]*/[\d]*", path):
                            column = params.get("column", None)
                            value = params.get("value", None)
                            if all((column, value)) is False:
                                if column is not None:
                                    if column[0].count(".") == 1:
                                        pass
                                    else:
                                        return Response(json.dumps(missing_key), mimetype="application/json"), 403
                                else:
                                    return Response(json.dumps(missing_key), mimetype="application/json"), 403
                            else:
                                if len(column) == len(value):
                                    pass
                                else:
                                    return Response(json.dumps({"status": 403, "keys": ["column", "value"], "reason": "value lengths not matched to each other."}), mimetype="application/json"), 403
                        case _:
                            return Response(json.dumps({"status": 403, "path": path, "reason": "unavailable path to this method"})), 403
                case "PATCH":
                    match path:
                        case _ if re.match(r"/api/model/[\w]*/[\d]*", path):
                            column = params.get("column", None)
                            value = params.get("value", None)
                            if all((column, value)) is False:
                                if column is not None:
                                    if column[0].count(".") == 1:
                                        pass
                                    else:
                                        return Response(json.dumps(missing_key), mimetype="application/json"), 403
                                else:
                                    return Response(json.dumps(missing_key), mimetype="application/json"), 403
                            else:
                                if len(column) == len(value):
                                    pass
                                else:
                                    return Response(json.dumps({"status": 403, "keys": ["column", "value"], "reason": "value lengths not matched to each other."}), mimetype="application/json"), 403
                        case _:
                            return Response(json.dumps({"status": 403, "path": path, "reason": "unavailable path to this method"})), 403
                case "DELETE":
                    match path:
                        case _ if re.match(r"/api/model/[\w]*", path):
                            pass
                        case _:
                            return Response(json.dumps({"status": 403, "path": path, "reason": "unavailable path to this method"})), 403
                case _:
                    return Response(json.dumps({"status": 403, "method": request.method, "reason": "unavailable method"})), 403
        return f(*args, **kwargs)
    return decorated_function


def load_tables(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _metadata = db.MetaData()
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table_name in tables:
            if model_dict.get(table_name.replace("_", ""), None) is None:
                table = db.Table(table_name, _metadata, autoload_with=db.engine)
                class DynamicModel(declarative_base()):
                    __table__ = table
                model_dict[table_name.replace("_", "")] = DynamicModel
        return f(*args, **kwargs)
    return decorated_function


def register_versioning_events():
    from .models import ContractPoint, ContractAnnex

    for cls in [ContractAnnex, ContractPoint]:
        event.listen(cls, "before_update", versioning_listener)