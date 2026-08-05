from flask import Blueprint, make_response, jsonify, request
from .controller import MainController


main_bp = Blueprint('main', __name__)
main_controller = MainController()
@main_bp.route('/', methods=['GET'])
def index():
    """ Example endpoint with simple greeting.
    ---
    tags:
      - Example API
    responses:
      200:
        description: A simple greeting
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Hello World!"
    """
    result=main_controller.index()
    return make_response(jsonify(data=result))

@main_bp.route('/add_sensor_value', methods=['POST'])
def add_sensor_value():
  """ Endpoint to add new sensor value and predict water quality.
    ---
    tags:
      - Sensor API
    parameters:
    - in: body
      name: body
      required: true
      description: JSON structure containing sensor value
      schema:
        type: object
        properties:
          ph_value:
            type: number
          turbidity_value:
            type: number
          temperature_value:
            type: number
    responses:
      201:
        description: Sensor value has been added to Database, along with the predicted water quality
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Sensor value has been added to Database"
                ph:
                  type: number
                  example: 7.0
                turbidity:
                  type: number
                  example: 10.0
                temp:
                  type: number
                  example: 25.0
                predicted_quality:
                  type: string
                  example: "Baik"
                probabilities:
                  type: object
                  example: {"Baik": 0.95, "Sedang": 0.05}
      400:
        description: Invalid input
      503:
        description: ML model is not available
  """

  data = request.get_json(silent=True) or {}
  ph_val = data.get('ph_value')
  turbidity_val = data.get('turbidity_value')
  temperature_val = data.get('temperature_value')

  if ph_val is None or turbidity_val is None or temperature_val is None:
    return make_response(
        jsonify(error="ph_value, turbidity_value, dan temperature_value wajib diisi"),
        400,
    )

  try:
    result = main_controller.add_sensor_value(ph_val, turbidity_val, temperature_val)
  except ValueError as e:
    return make_response(jsonify(error=str(e)), 400)
  except RuntimeError as e:
    return make_response(jsonify(error=str(e)), 503)

  return make_response(jsonify(data=result), 201)


@main_bp.route('/predict_quality', methods=['POST'])
def predict_quality():
  """ Endpoint to predict water quality WITHOUT saving to database.
    ---
    tags:
      - Sensor API
    parameters:
    - in: body
      name: body
      required: true
      description: JSON structure containing sensor value
      schema:
        type: object
        properties:
          ph_value:
            type: number
            example: 7.2
          turbidity_value:
            type: number
            example: 3.8
          temperature_value:
            type: number
            example: 25.5
    responses:
      200:
        description: Predicted water quality
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                ph:
                  type: number
                turbidity:
                  type: number
                temp:
                  type: number
                predicted_quality:
                  type: string
                  example: "Baik"
                probabilities:
                  type: object
                  example: {"Baik": 0.95, "Sedang": 0.05}
      400:
        description: Invalid input
      503:
        description: ML model is not available
  """
  data = request.get_json(silent=True) or {}
  ph_val = data.get('ph_value')
  turbidity_val = data.get('turbidity_value')
  temperature_val = data.get('temperature_value')

  if ph_val is None or turbidity_val is None or temperature_val is None:
    return make_response(
        jsonify(error="ph_value, turbidity_value, dan temperature_value wajib diisi"),
        400,
    )

  try:
    result = main_controller.predict_quality(ph_val, turbidity_val, temperature_val)
  except ValueError as e:
    return make_response(jsonify(error=str(e)), 400)
  except RuntimeError as e:
    return make_response(jsonify(error=str(e)), 503)

  return make_response(jsonify(data=result), 200)