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
  """ Endpoint to add new sensor value.
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
        description: Sensor value has been added to Database
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
  """

  data = request.get_json()
  ph_val = data.get('ph_value')
  turbidity_val = data.get('turbidity_value')
  temperature_val = data.get('temperature_value')
  result = main_controller.add_sensor_value(ph_val, turbidity_val, temperature_val)
  return make_response(jsonify(data=result), 201)