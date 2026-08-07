import json

class TestMain():
    def test_index(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert response.json == {'data': {'message': 'Hello, World!'}}

    def test_predict_quality_success(self, client):
        response = client.post(
            '/predict_quality',
            data=json.dumps({
                'ph_value': 7.2,
                'turbidity_value': 3.8,
                'temperature_value': 25.5,
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        body = response.json['data']
        assert body['predicted_quality'] in ('Baik', 'Sedang')
        assert 'probabilities' in body

    def test_predict_quality_missing_field(self, client):
        response = client.post(
            '/predict_quality',
            data=json.dumps({'ph_value': 7.2, 'turbidity_value': 3.8}),
            content_type='application/json',
        )
        assert response.status_code == 400

    def test_add_sensor_value_success(self, client):
        response = client.post(
            '/add_sensor_value',
            data=json.dumps({
                'ph_value': 7.1,
                'turbidity_value': 4.0,
                'temperature_value': 22.0,
            }),
            content_type='application/json',
        )
        assert response.status_code == 201
        body = response.json['data']
        assert 'predicted_quality' in body
        assert body['ph'] == 7.1
