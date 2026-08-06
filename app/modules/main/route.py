from flask import Blueprint, make_response, jsonify, request, render_template
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

@main_bp.route('/latest_reading', methods=['GET'])
def latest_reading():
  """ Endpoint to get the most recent sensor reading.
    ---
    tags:
      - Visualization API
    responses:
      200:
        description: The latest sensor reading
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Latest sensor reading"
                reading:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1560
                    timestamp:
                      type: string
                      example: "2025-01-15T10:30:00+08:00"
                    ph:
                      type: number
                      example: 7.25
                    turbidity:
                      type: number
                      example: 3.7
                    temp:
                      type: number
                      example: 28.56
                    predicted_quality:
                      type: string
                      example: "Baik"
  """
  result = main_controller.get_latest_reading()
  return make_response(jsonify(data=result), 200)


@main_bp.route('/sensor_history', methods=['GET'])
def sensor_history():
  """ Endpoint to get sensor reading history for time-series charts.
    ---
    tags:
      - Visualization API
    parameters:
      - in: query
        name: limit
        type: integer
        required: false
        default: 100
        description: Maximum number of readings to return (1-1000)
      - in: query
        name: hours
        type: integer
        required: false
        description: Only return readings from the last N hours (1-8760)
    responses:
      200:
        description: List of sensor readings ordered from oldest to newest
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                count:
                  type: integer
                  example: 100
                limit:
                  type: integer
                  example: 100
                hours:
                  type: integer
                  example: 24
                readings:
                  type: array
                  items:
                    type: object
      400:
        description: Invalid query parameter
  """
  try:
    result = main_controller.get_sensor_history(
        limit=request.args.get('limit', 100),
        hours=request.args.get('hours'),
    )
  except ValueError as e:
    return make_response(jsonify(error=str(e)), 400)

  return make_response(jsonify(data=result), 200)


@main_bp.route('/statistics', methods=['GET'])
def statistics():
  """ Endpoint to get descriptive statistics of all sensor parameters.
    ---
    tags:
      - Visualization API
    responses:
      200:
        description: Descriptive statistics per sensor parameter
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                total_records:
                  type: integer
                  example: 1560
                statistics:
                  type: object
                  example:
                    ph: {"min": 3.57, "max": 9.87, "mean": 7.187, "std": 0.478}
                    turbidity: {"min": 0.0, "max": 15.0, "mean": 3.996, "std": 2.686}
                    temperature: {"min": 18.44, "max": 32.56, "mean": 25.233, "std": 2.116}
                period:
                  type: object
                  example:
                    start: "2025-01-01T08:00:00+08:00"
                    end: "2025-01-31T17:45:00+08:00"
  """
  result = main_controller.get_statistics()
  return make_response(jsonify(data=result), 200)


@main_bp.route('/quality_distribution', methods=['GET'])
def quality_distribution():
  """ Endpoint to get the distribution of predicted water quality classes.
    ---
    tags:
      - Visualization API
    responses:
      200:
        description: Count and percentage per water quality class
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                total_records:
                  type: integer
                  example: 1560
                distribution:
                  type: object
                  example: {"Baik": 1201, "Sedang": 303, "Buruk": 38}
                percentage:
                  type: object
                  example: {"Baik": 77.9, "Sedang": 19.6, "Buruk": 2.5}
  """
  result = main_controller.get_quality_distribution()
  return make_response(jsonify(data=result), 200)


@main_bp.route('/trend', methods=['GET'])
def trend():
  """ Endpoint to get hourly averaged sensor values for trend charts.
    ---
    tags:
      - Visualization API
    parameters:
      - in: query
        name: hours
        type: integer
        required: false
        default: 24
        description: Number of hours to look back (1-720)
    responses:
      200:
        description: Hourly averaged sensor values
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                hours:
                  type: integer
                  example: 24
                count:
                  type: integer
                  example: 24
                trend:
                  type: array
                  items:
                    type: object
                    properties:
                      hour:
                        type: string
                        example: "2025-01-15 10:00"
                      avg_ph:
                        type: number
                        example: 7.213
                      avg_turbidity:
                        type: number
                        example: 3.842
                      avg_temp:
                        type: number
                        example: 25.47
                      count:
                        type: integer
                        example: 60
      400:
        description: Invalid query parameter
  """
  try:
    result = main_controller.get_hourly_trend(hours=request.args.get('hours', 24))
  except ValueError as e:
    return make_response(jsonify(error=str(e)), 400)

  return make_response(jsonify(data=result), 200)


@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
  """ Endpoint serving an HTML dashboard that visualizes the sensor data.
    ---
    tags:
      - Visualization API
    produces:
      - text/html
    responses:
      200:
        description: HTML dashboard page
  """
  return render_template('dashboard.html')
