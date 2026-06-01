import unittest

import numpy as np
import pandas as pd

from explain import explain_anomaly
from mitre_mapping import map_to_mitre
from model import run_isolation_forest
from preprocessing import preprocess_data


class CoreBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "Source IP": ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"],
                "Destination IP": ["192.168.1.10"] * 4,
                "Flow Duration": [1000, 1200, np.inf, 10],
                "Flow Packets/s": [10, 12, 11, 9000],
                "Total Length of Fwd Packets": [500, 520, np.nan, 900000],
                "Destination Port": [80, 443, 53, 22],
                "Protocol": ["TCP", "TCP", "UDP", "TCP"],
            }
        )

    def test_preprocess_data_selects_numeric_features_and_scales_values(self):
        matrix, cleaned_df, metadata = preprocess_data(self.df)

        self.assertEqual(matrix.shape[0], 4)
        self.assertGreaterEqual(matrix.shape[1], 2)
        self.assertIn("Flow Duration", metadata["numeric_features"])
        self.assertIn("Flow Packets/s", metadata["numeric_features"])
        self.assertFalse(cleaned_df[metadata["numeric_features"]].isna().any().any())
        self.assertTrue(np.isfinite(matrix).all())

    def test_isolation_forest_attaches_predictions_and_scores(self):
        matrix, cleaned_df, _ = preprocess_data(self.df)

        result = run_isolation_forest(
            cleaned_df,
            matrix,
            contamination=0.25,
            n_estimators=50,
            random_state=42,
        )

        self.assertIn("prediction", result.columns)
        self.assertIn("prediction_label", result.columns)
        self.assertIn("anomaly_score", result.columns)
        self.assertTrue(set(result["prediction_label"]).issubset({"Normal", "Anomaly"}))
        self.assertEqual((result["prediction"] == -1).sum(), 1)

    def test_explain_anomaly_returns_top_unusual_features_and_text(self):
        _, cleaned_df, metadata = preprocess_data(self.df)
        row = cleaned_df.loc[3]

        explanation = explain_anomaly(row, cleaned_df, metadata["numeric_features"], top_n=3)

        self.assertEqual(len(explanation["top_features"]), 3)
        self.assertIn("Flow", explanation["explanation"])
        feature_names = [item["feature"] for item in explanation["top_features"]]
        self.assertIn("Flow Packets/s", feature_names)

    def test_mitre_mapping_returns_matching_rules_for_scan_and_exfiltration(self):
        _, cleaned_df, metadata = preprocess_data(self.df)
        row = cleaned_df.loc[3]

        mappings = map_to_mitre(row, metadata["numeric_features"], cleaned_df)
        techniques = {item["technique"] for item in mappings}

        self.assertIn("Active Scanning", techniques)
        self.assertIn("Exfiltration Over Network", techniques)


if __name__ == "__main__":
    unittest.main()
