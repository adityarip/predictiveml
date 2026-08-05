import os
import joblib

# models folder location
_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

_MODEL_PATH = os.path.join(_MODEL_DIR, "model_kualitas_air_rf.pkl")
_LABEL_ENCODER_PATH = os.path.join(_MODEL_DIR, "label_encoder.pkl")
_FEATURE_NAMES_PATH = os.path.join(_MODEL_DIR, "feature_names.pkl")

class WaterQualityPredictor:
    """Wrapper untuk model Random Forest prediksi kualitas air akuarium."""

    def __init__(self):
        self._model = None
        self._label_encoder = None
        self._feature_names = None
        self._load_error = None
        self._load()

    def _load(self):
        try:
            self._model = joblib.load(_MODEL_PATH)
            self._label_encoder = joblib.load(_LABEL_ENCODER_PATH)
            self._feature_names = joblib.load(_FEATURE_NAMES_PATH)
        except FileNotFoundError as e:
            self._load_error = str(e)

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def predict(self, ph: float, temperature: float, turbidity: float) -> dict:
        """
        Memprediksi kualitas air akuarium.

        Args:
            ph: nilai pH air
            temperature: suhu air dalam Celsius
            turbidity: kekeruhan air dalam NTU

        Returns:
            dict berisi label prediksi dan probabilitas tiap kelas.

        Raises:
            RuntimeError: jika model gagal dimuat.
            ValueError: jika salah satu input tidak valid.
        """
        if not self.is_ready:
            raise RuntimeError(
                f"Model belum berhasil dimuat: {self._load_error}"
            )

        for name, value in [("ph", ph), ("temperature", temperature), ("turbidity", turbidity)]:
            if value is None:
                raise ValueError(f"Parameter '{name}' wajib diisi")
            try:
                float(value)
            except (TypeError, ValueError):
                raise ValueError(f"Parameter '{name}' harus berupa angka")

        import pandas as pd

        new_data = pd.DataFrame(
            [[float(ph), float(temperature), float(turbidity)]],
            columns=self._feature_names,
        )

        pred_encoded = self._model.predict(new_data)[0]
        pred_label = self._label_encoder.inverse_transform([pred_encoded])[0]

        proba = self._model.predict_proba(new_data)[0]
        proba_dict = {
            label: round(float(p), 4)
            for label, p in zip(self._label_encoder.classes_, proba)
        }

        return {
            "predicted_quality": str(pred_label),
            "probabilities": proba_dict,
        }


predictor = WaterQualityPredictor()