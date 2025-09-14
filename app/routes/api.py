import json
from urllib.parse import parse_qs, unquote_plus, urlparse


import inflection
from sqlalchemy import inspect
from flask import Blueprint, Response, jsonify, request
from sqlalchemy.orm import selectinload, joinedload, subqueryload
from sqlalchemy.ext.declarative import declarative_base
from app import db

from ..models import *
from ..middleware import params_valid, model_dict, load_tables

api_bp = Blueprint('api', __name__)

_metadata = db.MetaData()

column_type_dict = {
    "int": db.Integer,
    "text": db.Text,
    "timestamp": db.TIMESTAMP,
    "datetime": db.DateTime,
    "date": db.Date
}

def _get_model_attributes(model):
    mapper = inspect(model).mapper
    return [prop.key for prop in mapper.attrs]

def _with_all_rels(model):
    return [selectinload(getattr(model, rel.key)) for rel in model.__mapper__.relationships]

def _model_to_dict(obj, seen=None):
    if obj is None:
        return None
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return None
    seen.add(id(obj))
    result = {}
    mapper = inspect(obj).mapper
    for c in mapper.column_attrs:
        value = getattr(obj, c.key)
        if isinstance(value, (int, float, str, bool)) or value is None:
            result[c.key] = value
        else:
            result[c.key] = str(value)
    for r in mapper.relationships:
        value = getattr(obj, r.key)
        if value is None:
            result[r.key] = None
        elif r.uselist:
            result[r.key] = [_model_to_dict(child, seen) for child in value]
        else:
            result[r.key] = _model_to_dict(value, seen)
    return result

def _register_dynamic_model(table_name):
    table = db.Table(inflection.underscore(table_name).lower(), _metadata, autoload_with=db.engine)
    class DynamicModel(declarative_base()):
        __table__ = table
    model_dict[inflection.underscore(table_name).lower().replace("_", "")] = DynamicModel
    return DynamicModel

@api_bp.route('/', methods=['GET'])
@params_valid
def api_index():
    response = {
        "version": "1",
        "request_params": [
            {
                f"GET": {
                    "paths": ["/api/models", "/api/model/<string:model>", "/api/model/<string:model>/<int:id>"],
                    "params": False,
                    "fragment": False
                }
            }, 
            {
                f"POST": {
                    "paths": ["/api/models", "/api/model/<string:model>"],
                    "params": {
                        "format": ["params", "json"],
                        "/api/models": {
                            "table": ["string"],
                            "column": ["string"],
                            "column_type": ["string"],
                            "ref": ["<table>.<column_name>"],
                        },
                        "/api/model/<string:model>": {
                            "column": ["string"],
                            "value": ["string", "int"]
                        }
                    },
                    "fragment": False
                }
            }, 
            {
                f"PUT": {
                    "paths": ["/api/model/<string:model>/<int:id>"],
                    "params": {
                        "format": ["params", "json"],
                        "/api/models/<string:model>/<int:id>": {
                            "column": ["string"],
                            "value": ["string", "int"],
                        }
                    },
                    "fragment": False
                }
            }, 
            {
                f"PATCH": {
                    "paths": ["/api/model/<string:model>/<int:id>"],
                    "params": {
                        "format": ["params", "json"],
                        "/api/models/<string:model>/<int:id>": {
                            "column": ["string"],
                            "value": ["string", "int"],
                        }
                    },
                    "fragment": False
                }
            }
        ],
        "request_methods": ["GET", "POST", "PUT", "PATCH"],
        "paths": ["/api/models", "/api/model/<string:model>", "/api/model/<string:model>/<int:id>"],
        "comment": {
            "params": "Fill the skip fields with None or null type in json format. Without <format> key request doesn\'t create or update model(s). Also look to [usage] for features in request params! Attention: if value contain dots then use default request format like [?column&column_type&value&ref] not [?column=Column.Column_Type.[Ref or Value]]",
            "json": "Except params you might send keys with list values is same formats [default] [features]",
            "default_format": "?format=params&column=Name&column_type=string&ref=None",
            "feature_format": "?format=params&column=Name.string.None",
            "attention": "In [feature] you should not use <column_type>, <value>, <ref> for prevent get error from server."
        },
        "usage": {
            "GET": "/api/...",
            "POST": [
                {
                    f"/api/models": [
                        "?format=params&table=Table&column=Name&column=Username&column_type=string&column_type=string",
                        "?format=params&table=Table&column=Name.string&column=Username.string",
                        "?format=params&table=Table&column=Name&column=Username&column=Role&column_type=string&column_type=string&column_type=int&ref=None&ref=None&ref=Role.id",
                        "?format=params&table=Table&column=Name.string&column=Username.string&column=Role.int&ref=None&ref=None&ref=Role.id",
                        "?format=params&table=Table&column=Name.string.None&column=Username.string.None&column=Role.int.Role.id",
                        "?format=json"
                    ],
                    "/api/model/<string:model>": [
                        "?format=params&column=Name&column=Username&value=Jonh&value=jonhdoe",
                        "?format=params&column=Name.Jonh&column=Username.jonhdoe",
                        "?format=json"
                    ]
                }
            ],
            "PUT": [
                {
                    "/api/model/<string:model>/<int:id>": [
                        "?format=params&column=Name&column=Username&value=Joe&value=joedoe",
                        "?format=params&column=Name.Joe&column=Username.joedoe",
                        "?format=json"
                    ]
                }
            ],
            "PATCH": [
                {
                    "/api/model/<string:model>/<int:id>": [
                        "?format=params&column=Name&value=Joe",
                        "?format=params&column=Name.Joe",
                        "?format=json"
                    ]
                }
            ]
        }
    }
    return Response(json.dumps(response), mimetype='application/json')

@api_bp.route('/models', methods=['GET', 'POST'])
@load_tables
@params_valid
def api_models():
    match request.method:
        case "GET":
            response = []
            for model, model_class in model_dict.items():
                rows = db.session.query(model_class).options(*_with_all_rels(model_class)).all()
                result = {model: [ _model_to_dict(row) for row in rows]}
                response.append(result)
            return Response(json.dumps(response), mimetype='application/json')
        case "POST":
            params = parse_qs(unquote_plus(urlparse(request.url).query))
            format_key = params.get("format", None)
            if format_key[0] == "json":
                    params = request.get_json(silent=True)
            table_name = params.get("table", None)
            column = params.get("column", None)
            column_type= params.get("column_type", None)
            ref = params.get("ref", None)
            columns = []
            columns.append(db.Column("id", db.Integer, primary_key=True, autoincrement="auto"))
            if column_type is None:
                for item in column:
                    col, col_type, ref_id= item.split(".", 2)
                    if ref_id in ["None", "null"]:
                        columns.append(db.Column(col, column_type_dict.get(col_type, db.Text)))
                    else:
                        columns.append(db.Column(col, column_type_dict.get(col_type, db.Text)), db.ForeignKey(ref_id))
            else:
                for i in range(len(column)):
                    if ref[i] in ["None", None]:
                        columns.append(db.Column(column[i], column_type_dict.get(column_type[i], db.Text)))
                    else:
                        columns.append(db.Column(column[i], column_type_dict.get(column_type[i], db.Text)), db.ForeignKey(ref[i]))
            new_table = db.Table(table_name[0], _metadata, *columns, extend_existing=True)
            _metadata.create_all(db.engine, tables=[new_table])
            _register_dynamic_model(table_name[0])
            return Response(json.dumps({"table": table_name, "created": True, "path": f"/api/model/{inflection.underscore(table_name[0])}"}), mimetype='application/json')
    

@api_bp.route('/model/<string:model>', methods=['GET', "POST", "DELETE"])
@load_tables
@params_valid
def api_model(model):
    model_class = model_dict.get(model)
    match request.method:
        case "GET":
            if model_class:
                return Response(json.dumps([_model_to_dict(item) for item in db.session.query(model_class).options(*_with_all_rels(model_class)).all()]), mimetype='application/json')
            else:
                return Response(json.dumps([]), mimetype='application/json'), 404
        case "POST":
            new_row = model_class()
            new_row.id = len(db.session.query(model_class).all()) + 1
            params = parse_qs(unquote_plus(urlparse(request.url).query))
            format_key = params.get("format", None)
            if format_key[0] == "json":
                params = request.get_json(silent=True)
            column = params.get("column", None)
            value = params.get("value", None)
            if value is None and column is not None:
                value = [x.split(".")[1] for x in column]
                column = [x.split(".")[0] for x in column]
            attrs = _get_model_attributes(model_class)
            attrs.remove("id")
            missing_keys = [x for x in attrs if x not in column]
            if len(missing_keys) == 0:
                for i in range(len(column)):
                    if hasattr(new_row, column[i]):
                        setattr(new_row, column[i], value[i])
                try:
                    db.session.add(new_row)
                    db.session.commit()
                except Exception as err:
                    return Response(json.dumps({"status": 500, "error": err})), 500
                return Response(json.dumps({f"status": 200, "id": new_row.id, "params": params, "model": _model_to_dict(new_row)})), 200
            else:
                return Response(json.dumps({"status": 403, "keys": missing_keys, "reason": "for create new row you should use all keys"})), 403
        case "DELETE":
            model_class.__table__.drop(db.engine)
            model_dict.pop(model)
            return Response(json.dumps({"model": model, "drop": True})), 200

@api_bp.route('/model/<string:model>/<int:id>', methods=['GET', 'PUT', 'PATCH'])
@load_tables
@params_valid
def api_model_detail(model, id):
    model_class = model_dict.get(model)
    if model_class:
        item = model_class().query.get(int(id))
    else:
        return Response(json.dumps({"error": "Not Found"}), mimetype='application/json'), 404
    params = parse_qs(unquote_plus(urlparse(request.url).query))
    format_key = params.get("format", None)
    if format_key is None:
        pass
    elif format_key[0] == "json":
        params = request.get_json(silent=True)
    column = params.get("column")
    value = params.get("value")
    if value is None and column is not None:
        value = [x.split(".")[1] for x in column]
        column = [x.split(".")[0] for x in column]
    match request.method:
        case 'GET':
            if item:
                return Response(json.dumps(_model_to_dict(item)), mimetype='application/json')
            else:
                return Response(json.dumps({"error": "Not exist"}), mimetype='application/json'), 404
        case 'PUT':
            if item:
                attrs = _get_model_attributes(model_class)
                attrs.remove("id")
                missing_keys = [x for x in attrs if x not in column]
                if len(missing_keys) == 0:
                    for i in range(len(column)):
                        if hasattr(item, column[i]):
                            setattr(item, column[i], value[i])
                    try:
                        db.session.commit()
                    except Exception as err:
                        return Response(json.dumps({"status": 500, "error": err})), 500
                    return Response(json.dumps({f"status": 200, "id": item.id, "params": params, "model": _model_to_dict(item)})), 200
                else:
                    return Response(json.dumps({"status": 403, "keys": missing_keys, "reason": "for create new row you should use all keys"})), 403
            else:
                return Response(json.dumps({"error": "Not exist"}), mimetype='application/json'), 404
        case 'PATCH':
            for i in range(len(column)):
                if hasattr(item, column[i]):
                    setattr(item, column[i], value[i])
            try:
                db.session.commit()
            except Exception as err:
                return Response(json.dumps({"status": 500, "error": err})), 500
            return Response(json.dumps({f"status": 200, "id": item.id, "params": params, "model": _model_to_dict(item)})), 200
