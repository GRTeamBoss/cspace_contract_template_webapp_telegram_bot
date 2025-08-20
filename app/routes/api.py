import json

from flask import Blueprint, Response

from ..models import *

api_bp = Blueprint('api', __name__)

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


@api_bp.route('/models', methods=['GET'])
def api_models():
    return Response(json.dumps({model: model_class.query.count() for model, model_class in model_dict.items()}), mimetype='application/json')


@api_bp.route('/model/<string:model>', methods=['GET'])
def api_model(model):
    model_class = model_dict.get(model.lower())
    if model_class:
        return Response(json.dumps([item.to_dict(include_relationships=True) for item in model_class.query.all()]), mimetype='application/json')
    else:
        return Response(json.dumps([]), mimetype='application/json'), 404


@api_bp.route('/model/<string:model>/<int:id>', methods=['GET'])
def api_model_detail(model, id):
    model_class = model_dict.get(model.lower())
    if model_class:
        item = model_class.query.get(id)
        if item:
            return Response(json.dumps(item.to_dict(include_relationships=True)), mimetype='application/json')
        else:
            return Response(json.dumps({"error": "Not Found"}), mimetype='application/json'), 404
    else:
        return Response(json.dumps({"error": "Empty"}), mimetype='application/json'), 404