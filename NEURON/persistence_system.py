"""
Persistence System - Save and load network state across sessions

Enables the network to learn and evolve over time, maintaining knowledge between runs.
"""

import json
import pickle
import time
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import gzip


class PersistenceManager:
    """
    Manages saving and loading of network state
    
    Saves:
    - Neuron genomes and fitness
    - Connection weights
    - Learned patterns
    - Evolution history
    - Learning statistics
    """
    
    def __init__(self, storage_path: str = "./neuron_state"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.storage_path / "network_state.json.gz"
        self.weights_file = self.storage_path / "connection_weights.pkl.gz"
        self.memory_file = self.storage_path / "memory_patterns.json.gz"
        self.evolution_file = self.storage_path / "evolution_history.json.gz"
        
        self.autosave_enabled = True
        self.autosave_interval = 300
        self.last_save_time = time.time()
    
    def save_network_state(
        self,
        neurons: Dict[str, Any],
        genomes: Dict[str, Dict],
        fitness: Dict[str, Dict],
        metadata: Dict[str, Any]
    ) -> bool:
        """Save complete network state"""
        try:
            state = {
                'version': '1.0',
                'timestamp': time.time(),
                'metadata': metadata,
                'neurons': {
                    nid: {
                        'type': n.type.value if hasattr(n.type, 'value') else str(n.type),
                        'function': n.function,
                        'specialization': getattr(n, 'specialization', 'general'),
                        'threshold': n.threshold,
                        'creation_time': n.creation_time,
                        'fire_count': n.state.fire_count
                    }
                    for nid, n in neurons.items()
                },
                'genomes': genomes,
                'fitness': fitness
            }
            
            with gzip.open(self.state_file, 'wt', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            self.last_save_time = time.time()
            return True
            
        except Exception as e:
            print(f"Error saving network state: {e}")
            return False
    
    def load_network_state(self) -> Optional[Dict[str, Any]]:
        """Load network state from disk"""
        if not self.state_file.exists():
            return None
        
        try:
            with gzip.open(self.state_file, 'rt', encoding='utf-8') as f:
                state = json.load(f)
            
            return state
            
        except Exception as e:
            print(f"Error loading network state: {e}")
            return None
    
    def save_connection_weights(self, weights: Dict[Tuple[str, str], float]) -> bool:
        """Save connection weights"""
        try:
            weights_serializable = {
                f"{pre}_{post}": weight
                for (pre, post), weight in weights.items()
            }
            
            with gzip.open(self.weights_file, 'wb') as f:
                pickle.dump(weights_serializable, f)
            
            return True
            
        except Exception as e:
            print(f"Error saving weights: {e}")
            return False
    
    def load_connection_weights(self) -> Optional[Dict[Tuple[str, str], float]]:
        """Load connection weights"""
        if not self.weights_file.exists():
            return None
        
        try:
            with gzip.open(self.weights_file, 'rb') as f:
                weights_serializable = pickle.load(f)
            
            weights = {}
            for key, weight in weights_serializable.items():
                pre, post = key.split('_', 1)
                weights[(pre, post)] = weight
            
            return weights
            
        except Exception as e:
            print(f"Error loading weights: {e}")
            return None
    
    def save_memory_patterns(self, patterns: List[Dict[str, Any]]) -> bool:
        """Save learned memory patterns"""
        try:
            memory_data = {
                'timestamp': time.time(),
                'pattern_count': len(patterns),
                'patterns': patterns
            }
            
            with gzip.open(self.memory_file, 'wt', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving memory patterns: {e}")
            return False
    
    def load_memory_patterns(self) -> Optional[List[Dict[str, Any]]]:
        """Load memory patterns"""
        if not self.memory_file.exists():
            return None
        
        try:
            with gzip.open(self.memory_file, 'rt', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            return memory_data.get('patterns', [])
            
        except Exception as e:
            print(f"Error loading memory patterns: {e}")
            return None
    
    def save_evolution_history(self, history: List[Dict[str, Any]]) -> bool:
        """Save evolution history"""
        try:
            evolution_data = {
                'timestamp': time.time(),
                'generation_count': len(history),
                'history': history
            }
            
            with gzip.open(self.evolution_file, 'wt', encoding='utf-8') as f:
                json.dump(evolution_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving evolution history: {e}")
            return False
    
    def load_evolution_history(self) -> Optional[List[Dict[str, Any]]]:
        """Load evolution history"""
        if not self.evolution_file.exists():
            return None
        
        try:
            with gzip.open(self.evolution_file, 'rt', encoding='utf-8') as f:
                evolution_data = json.load(f)
            
            return evolution_data.get('history', [])
            
        except Exception as e:
            print(f"Error loading evolution history: {e}")
            return None
    
    def should_autosave(self) -> bool:
        """Check if it's time for autosave"""
        if not self.autosave_enabled:
            return False
        
        return (time.time() - self.last_save_time) >= self.autosave_interval
    
    def create_checkpoint(self, checkpoint_name: str, data: Dict[str, Any]) -> bool:
        """Create named checkpoint"""
        try:
            checkpoint_file = self.storage_path / f"checkpoint_{checkpoint_name}.json.gz"
            
            checkpoint_data = {
                'name': checkpoint_name,
                'timestamp': time.time(),
                'data': data
            }
            
            with gzip.open(checkpoint_file, 'wt', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error creating checkpoint: {e}")
            return False
    
    def list_checkpoints(self) -> List[str]:
        """List available checkpoints"""
        checkpoints = []
        for file in self.storage_path.glob("checkpoint_*.json.gz"):
            checkpoint_name = file.stem.replace('checkpoint_', '').replace('.json', '')
            checkpoints.append(checkpoint_name)
        
        return sorted(checkpoints)
    
    def load_checkpoint(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """Load named checkpoint"""
        checkpoint_file = self.storage_path / f"checkpoint_{checkpoint_name}.json.gz"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with gzip.open(checkpoint_file, 'rt', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            return checkpoint_data.get('data')
            
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None
    
    def export_for_analysis(self, export_path: str) -> bool:
        """Export network data for external analysis"""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            state = self.load_network_state()
            if state:
                with open(export_dir / "network_state.json", 'w') as f:
                    json.dump(state, f, indent=2)
            
            weights = self.load_connection_weights()
            if weights:
                weights_list = [
                    {'pre': pre, 'post': post, 'weight': weight}
                    for (pre, post), weight in weights.items()
                ]
                with open(export_dir / "connection_weights.json", 'w') as f:
                    json.dump(weights_list, f, indent=2)
            
            patterns = self.load_memory_patterns()
            if patterns:
                with open(export_dir / "memory_patterns.json", 'w') as f:
                    json.dump(patterns, f, indent=2)
            
            history = self.load_evolution_history()
            if history:
                with open(export_dir / "evolution_history.json", 'w') as f:
                    json.dump(history, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about stored data"""
        info = {
            'storage_path': str(self.storage_path),
            'files': {}
        }
        
        for file_attr in ['state_file', 'weights_file', 'memory_file', 'evolution_file']:
            file_path = getattr(self, file_attr)
            if file_path.exists():
                info['files'][file_attr] = {
                    'exists': True,
                    'size_bytes': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                }
            else:
                info['files'][file_attr] = {'exists': False}
        
        info['checkpoints'] = self.list_checkpoints()
        
        return info
