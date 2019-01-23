from flask import Blueprint, jsonify, request, abort
from datetime import datetime
from app.models.incident import Incident

from app.helpers.validators import (
    validate_input,
    valid_url_input,
    set_incident_type
)

from app.helpers.authetication import (
    token_required,
    get_current_identity,
    non_admin,
    json_data_required
)


create_record = Blueprint("create_record", __name__, url_prefix="/api/v1")

response = None


@create_record.route("/<string:incident_type>", methods=["POST"])
@token_required
@non_admin
@json_data_required
def create_red_flag_record_of_given_user(incident_type):
    """Create an incident record of a given user"""
    if not valid_url_input(incident_type):
        return jsonify({
            "status": 404,
            "error": "Page Not found. Enter a valid URL"
        }), 404

    incident = request.get_json()
    incident["status"] = "draft"
    incident["createdOn"] = datetime.now().strftime("%Y-%m-%d")
    incident["createdBy"] = get_current_identity()
    incident["_type"] = set_incident_type(incident_type)

    location = incident.get("location")
    comment = incident.get("comment")
    _type = incident.get("_type")
    images = incident.get("images") if "images" in incident else []
    videos = incident.get("videos") if "videos" in incident else []
    errors = validate_input(
        location, comment, images, videos)

    incident_exists = Incident.incident_exists(comment, location)

    if errors:
        response = jsonify({"status": 400, "error": errors}), 400
    elif incident_exists:
        response = jsonify({
            "status": 400,
            "error": "Record already exists."
        }), 400
    else:
        incident = Incident(**incident)
        Incident.add_incident(**incident.convert_to_dict())
        incident_id = Incident.get_records(_type)[-1]["id"]  # get the id
        response = jsonify({
            "status": 201,
            "data": [{
                "message": f"Created {_type} record",
                "id": incident_id
            }]
        }), 201
    return response
