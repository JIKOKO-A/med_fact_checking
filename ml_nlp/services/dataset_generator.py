import logging
from typing import List, Dict
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class DatasetGenerator:
    def __init__(self):
        self.dataset = []
        self.domains = ["cardiology", "oncology", "neurology"]
        logger.info("? Dataset Generator initialized")
    
    def generate_sample_dataset(self, size: int = 1000) -> List[Dict]:
        self.dataset = []
        for i in range(size):
            self.dataset.append({
                "id": i,
                "claim": f"Medical claim {i}",
                "darija_latin": f"darija_latin_{i}",
                "darija_arabic": f"عربي_{i}",
                "label": random.choice(["true", "false", "partially_true"]),
                "domain": random.choice(self.domains),
                "confidence": random.uniform(0.5, 0.99)
            })
        return self.dataset
    
    def get_statistics(self) -> Dict:
        return {
            "total_records": len(self.dataset),
            "labels": {},
            "domains": {},
            "avg_confidence": 0.75,
            "languages": ["ar"]
        }

_generator_instance = None
def get_dataset_generator():
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = DatasetGenerator()
    return _generator_instance
