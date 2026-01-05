"""
Data Storage Module - Stores datasets and predictions
Simple in-memory storage (can be extended to use database/file storage)
"""
import pandas as pd
from typing import Dict, Optional, List
import json
from datetime import datetime
import os

class DataStorage:
    """Simple storage for datasets and predictions"""
    
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.datasets = {}  # dataset_id -> dataframe
        self.models = {}  # dataset_id -> ML model
        self.predictions = []  # List of predictions
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def store_dataset(self, dataset_id: str, df: pd.DataFrame) -> bool:
        """Store a dataset"""
        try:
            self.datasets[dataset_id] = df.copy()
            # Also save to disk as backup
            csv_path = os.path.join(self.storage_dir, f"{dataset_id}.csv")
            df.to_csv(csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error storing dataset: {e}")
            return False
    
    def get_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Retrieve a dataset"""
        if dataset_id in self.datasets:
            return self.datasets[dataset_id].copy()
        
        # Try to load from disk
        csv_path = os.path.join(self.storage_dir, f"{dataset_id}.csv")
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                self.datasets[dataset_id] = df
                return df
            except:
                return None
        
        return None
    
    def store_model(self, dataset_id: str, model) -> bool:
        """Store ML model for a dataset"""
        try:
            self.models[dataset_id] = model
            return True
        except Exception as e:
            print(f"Error storing model: {e}")
            return False
    
    def get_model(self, dataset_id: str):
        """Retrieve ML model for a dataset"""
        return self.models.get(dataset_id)
    
    def store_prediction(self, dataset_id: str, input_data: Dict, prediction_result: Dict) -> str:
        """Store a prediction with unique ID"""
        prediction_id = f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        prediction_record = {
            "prediction_id": prediction_id,
            "dataset_id": dataset_id,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data,
            "prediction_result": prediction_result
        }
        
        self.predictions.append(prediction_record)
        
        # Also save to JSON file
        json_path = os.path.join(self.storage_dir, "predictions.json")
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    all_predictions = json.load(f)
            else:
                all_predictions = []
            
            all_predictions.append(prediction_record)
            
            with open(json_path, 'w') as f:
                json.dump(all_predictions, f, indent=2)
        except:
            pass  # Ignore file write errors
        
        return prediction_id
    
    def get_predictions(self, dataset_id: Optional[str] = None) -> List[Dict]:
        """Get all predictions, optionally filtered by dataset_id"""
        if dataset_id:
            return [p for p in self.predictions if p.get("dataset_id") == dataset_id]
        return self.predictions.copy()

# Global storage instance
storage = DataStorage()

