from datetime import datetime, timezone, timedelta

from sqlalchemy import String, cast, func

from app.db.db import db, Sensor
from app.ml.predictor import predictor

# Timezone used when storing timestamps
LOCAL_TZ = timezone(timedelta(hours=8))

def _to_aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=LOCAL_TZ)
    return dt

def _serialize(sensor):
    """Convert a single Sensor row into a JSON-ready dict."""
    timestamp = _to_aware(sensor.timestamp)
    return {
        'id': sensor.id,
        'timestamp': timestamp.isoformat() if timestamp else None,
        'ph': sensor.ph_value,
        'turbidity': sensor.turbidity_value,
        'temp': sensor.temperature_value,
        'predicted_quality': sensor.predicted_quality,
    }

class MainController:
    def index(self):
        return {'message': 'Hello, World!'}

    def add_sensor_value(self, ph_val, turbidity_val, temperature_val):
        """ Predict water quality using the Random Forest model """
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
        """Predict water quality WITHOUT saving to the database"""
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

    def get_latest_reading(self):
        """Return the most recent sensor reading."""
        sensor = db.session.scalars(
            db.select(Sensor).order_by(Sensor.id.desc()).limit(1)
        ).first()

        if sensor is None:
            return {'message': 'No sensor data available yet', 'reading': None}

        return {'message': 'Latest sensor reading', 'reading': _serialize(sensor)}

    def get_sensor_history(self, limit=100, hours=None):
        """Return sensor reading history for time-series charts."""
        limit = self._validate_int(limit, 'limit', minimum=1, maximum=1000, default=100)

        query = db.select(Sensor)

        if hours is not None:
            hours = self._validate_int(hours, 'hours', minimum=1, maximum=8760)
            cutoff = datetime.now(LOCAL_TZ) - timedelta(hours=hours)
            query = query.where(Sensor.timestamp >= cutoff)

        rows = db.session.scalars(
            query.order_by(Sensor.id.desc()).limit(limit)
        ).all()
        rows = list(reversed(rows))

        return {
            'count': len(rows),
            'limit': limit,
            'hours': hours,
            'readings': [_serialize(row) for row in rows],
        }

    def get_statistics(self):
        """Return descriptive statistics for every sensor parameter."""
        total = db.session.scalar(db.select(func.count(Sensor.id))) or 0

        if total == 0:
            return {'total_records': 0, 'statistics': {}, 'period': None}

        columns = {
            'ph': Sensor.ph_value,
            'turbidity': Sensor.turbidity_value,
            'temperature': Sensor.temperature_value,
        }

        statistics = {}
        for name, column in columns.items():
            minimum, maximum, mean = db.session.execute(
                db.select(func.min(column), func.max(column), func.avg(column))
            ).first()

            values = db.session.scalars(db.select(column)).all()
            if len(values) > 1:
                average = sum(values) / len(values)
                variance = sum((v - average) ** 2 for v in values) / (len(values) - 1)
                std_dev = variance ** 0.5
            else:
                std_dev = 0.0

            statistics[name] = {
                'min': round(float(minimum), 3),
                'max': round(float(maximum), 3),
                'mean': round(float(mean), 3),
                'std': round(float(std_dev), 3),
            }

        first_seen = _to_aware(db.session.scalar(db.select(func.min(Sensor.timestamp))))
        last_seen = _to_aware(db.session.scalar(db.select(func.max(Sensor.timestamp))))

        return {
            'total_records': total,
            'statistics': statistics,
            'period': {
                'start': first_seen.isoformat() if first_seen else None,
                'end': last_seen.isoformat() if last_seen else None,
            },
        }

    def get_quality_distribution(self):
        """Return the record count for each water quality class."""
        rows = db.session.execute(
            db.select(Sensor.predicted_quality, func.count(Sensor.id))
            .group_by(Sensor.predicted_quality)
        ).all()

        distribution = {}
        total = 0
        for label, count in rows:
            key = label if label else 'Not predicted'
            distribution[key] = count
            total += count

        percentage = {
            key: round(count / total * 100, 2) for key, count in distribution.items()
        } if total else {}

        return {
            'total_records': total,
            'distribution': distribution,
            'percentage': percentage,
        }

    def get_hourly_trend(self, hours=24):
        """Return hourly averaged sensor values for the trend chart."""
        hours = self._validate_int(hours, 'hours', minimum=1, maximum=720, default=24)
        cutoff = datetime.now(LOCAL_TZ) - timedelta(hours=hours)

        hour_bucket = func.substr(cast(Sensor.timestamp, String), 1, 13) + ':00'

        rows = db.session.execute(
            db.select(
                hour_bucket.label('hour'),
                func.avg(Sensor.ph_value),
                func.avg(Sensor.turbidity_value),
                func.avg(Sensor.temperature_value),
                func.count(Sensor.id),
            )
            .where(Sensor.timestamp >= cutoff)
            .group_by(hour_bucket)
            .order_by(hour_bucket)
        ).all()

        trend = [
            {
                'hour': row[0],
                'avg_ph': round(float(row[1]), 3),
                'avg_turbidity': round(float(row[2]), 3),
                'avg_temp': round(float(row[3]), 3),
                'count': row[4],
            }
            for row in rows
        ]

        return {'hours': hours, 'count': len(trend), 'trend': trend}

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_int(value, name, minimum, maximum, default=None):
        """Validate an integer query parameter."""
        if value is None or value == '':
            if default is not None:
                return default
            raise ValueError(f"Parameter '{name}' is required")

        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Parameter '{name}' must be an integer")

        if parsed < minimum or parsed > maximum:
            raise ValueError(
                f"Parameter '{name}' must be between {minimum} and {maximum}"
            )
        return parsed
