from app.db.db import db, Sensor
from app.ml.predictor import predictor

class MainController:
    def index(self):
        return {'message':'Hello, World!'}

    def add_sensor_value(self, ph_val, turbidity_val, temperature_val):
        # water quality prediction
        prediction = predictor.predict(
            ph=ph_val, temperature=temperature_val, turbidity=turbidity_val
        )

        # Create Sensor Object for inserting to database
        new_sensor_value = Sensor(
            ph_value=ph_val,
            turbidity_value=turbidity_val,
            temperature_value=temperature_val,
            predicted_quality=prediction['predicted_quality'],
        )

        # Adding object to database and commit the change
        db.session.add(new_sensor_value)
        db.session.commit()

        # Result to show
        result = {
            'message': 'Sensor value has been added to Database',
            'ph': ph_val,
            'turbidity': turbidity_val,
            'temp': temperature_val,
            'predicted_quality': prediction['predicted_quality'],
            'probabilities': prediction['probabilities'],
        }
        return result

    def predict_quality(self, ph_val, turbidity_val, temperature_val):
        """Water quality prediction WITHOUT saving to database
        for testing purposes
        """
        prediction = predictor.predict(
            ph=ph_val, temperature=temperature_val, turbidity=turbidity_val
        )
        return {
            'ph': ph_val,
            'turbidity': turbidity_val,
            'temp': temperature_val,
            'predicted_quality': prediction['predicted_quality'],
            'probabilities': prediction['probabilities'],
        }
