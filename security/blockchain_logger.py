# Layer 7: Blockchain Logger - Immutable audit logs
import hashlib
from datetime import datetime
from typing import Dict
import json

class BlockchainLogger:
    """Layer 7: Blockchain Logger - Create immutable audit trail"""
    
    def __init__(self):
        """Initialize blockchain"""
        self.chain = []
        # Genesis block
        genesis_block = self.create_block(
            data={"type": "genesis", "message": "Blockchain initialized"},
            previous_hash="0"
        )
        self.chain.append(genesis_block)
    
    def create_block(self, data: Dict, previous_hash: str = None) -> Dict:
        """Create a new block"""
        if previous_hash is None and self.chain:
            previous_hash = self.chain[-1]["hash"]
        elif previous_hash is None:
            previous_hash = "0"
        
        block = {
            "index": len(self.chain),
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "previous_hash": previous_hash,
            "hash": ""
        }
        
        # Calculate hash
        block["hash"] = self.calculate_hash(block)
        return block
    
    @staticmethod
    def calculate_hash(block: Dict) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            "index": block["index"],
            "timestamp": block["timestamp"],
            "data": block["data"],
            "previous_hash": block["previous_hash"]
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def add_log(self, data: Dict) -> Dict:
        """Add new log to blockchain"""
        new_block = self.create_block(data)
        self.chain.append(new_block)
        return new_block
    
    def get_chain(self) -> list:
        """Get entire blockchain"""
        return self.chain
    
    def verify_integrity(self) -> bool:
        """Verify blockchain integrity"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block hash
            if current_block["hash"] != self.calculate_hash(current_block):
                return False
            
            # Verify previous hash link
            if current_block["previous_hash"] != previous_block["hash"]:
                return False
        
        return True

# Global blockchain instance
blockchain = BlockchainLogger()
