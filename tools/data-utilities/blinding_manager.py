import json
import logging
from pathlib import Path
from typing import Dict, List, Union

class BlindingManager:
    """
    Manages a persistent mapping of sensitive Entity Codes to blinded IDs (FAC_XXXXX).
    Supports auto-extension when new facilities are encountered.
    """
    
    def __init__(self, map_file: Union[str, Path]):
        self.map_file = Path(map_file)
        self.mapping = self._load_map()
        self.logger = logging.getLogger(__name__)

    def _load_map(self) -> Dict[str, str]:
        if not self.map_file.exists():
            return {}
        with open(self.map_file, 'r') as f:
            return json.load(f)

    def _save_map(self):
        with open(self.map_file, 'w') as f:
            json.dump(self.mapping, f, indent=2)

    def get_max_id(self) -> int:
        """Finds the highest currently assigned FAC number."""
        existing_values = [v for v in self.mapping.values() if v.startswith("FAC_")]
        if not existing_values:
            return 0
        return max([int(v.split('_')[1]) for v in existing_values])

    def blind_ids(self, entity_codes: List[str]) -> Dict[str, str]:
        """
        Takes a list of entity codes.
        Returns a dictionary {entity_code: blinded_id}.
        Updates the persistent map file if new codes are found.
        """
        # Filter out None/NaN and ensure strings
        clean_codes = sorted(list(set([str(c) for c in entity_codes if c and str(c) != 'nan'])))
        
        new_codes = [c for c in clean_codes if c not in self.mapping]
        
        if new_codes:
            max_id = self.get_max_id()
            self.logger.info(f"BlindingManager: Found {len(new_codes)} new facilities. Starting from FAC_{max_id + 1:05d}")
            
            for i, code in enumerate(new_codes, start=1):
                self.mapping[code] = f"FAC_{max_id + i:05d}"
            
            self._save_map()
        
        # Return sub-dictionary for just the requested codes
        return {code: self.mapping.get(code, "UNMAPPED") for code in clean_codes}

    def apply_to_dataframe(self, df, col_name: str = 'entity_code', out_col: str = 'blinded_facility_id'):
        """
        Applies blinding to a pandas DataFrame in place.
        """
        unique_codes = df[col_name].unique()
        # Ensure map is up to date
        self.blind_ids(unique_codes)
        # Apply
        df[out_col] = df[col_name].map(self.mapping)
        return df
