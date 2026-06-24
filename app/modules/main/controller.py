from app.db.db import db, Sensor

class MainController:
    def index(self):
        return {'message':'Hello, World!'}

    def add_sensor_value(self, ph_val, turbidity_val, temperature_val):
        # Create Sensor Object for inserting to database
        new_sensor_value = Sensor(ph_value = ph_val, turbidity_value = turbidity_val, temperature_value = temperature_val)

        # Adding object to database and commit the change
        # db.session.add(new_sensor_value)
        # db.session.commit()

        # Result to show
        result = {'message':'Sensor value has been added to Database',
        'ph':ph_val,
        'turbidity': turbidity_val,
        'temp':temperature_val}
        return result
