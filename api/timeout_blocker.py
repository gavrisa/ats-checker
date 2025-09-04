"""
Simple timeout-based blocking system for problematic files
"""
import time
import asyncio
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class TimeoutBlocker:
    """Simple timeout-based blocking for files that take too long to process"""
    
    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout_seconds = timeout_seconds
    
    async def process_with_timeout(self, process_func, *args, **kwargs) -> Dict[str, Any]:
        """Process a function with timeout, blocking if it takes too long"""
        start_time = time.time()
        
        try:
            # Run the process function with timeout
            result = await asyncio.wait_for(
                process_func(*args, **kwargs),
                timeout=self.timeout_seconds
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Processing completed in {processing_time:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            logger.info(f"Processing timed out after {processing_time:.2f}s - blocking file")
            
            return {
                "status": "error",
                "message": "This file appears to be unreadable by automated systems. Please use a standard PDF or Word document format.",
                "preflight_details": {
                    "triggers": ["processing_timeout"],
                    "processing_time": processing_time,
                    "timeout_threshold": self.timeout_seconds
                }
            }
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing failed after {processing_time:.2f}s: {str(e)}")
            
            return {
                "status": "error",
                "message": "This file appears to be unreadable by automated systems. Please use a standard PDF or Word document format.",
                "preflight_details": {
                    "triggers": ["processing_error"],
                    "processing_time": processing_time,
                    "error": str(e)
                }
            }

# Global timeout blocker instance
timeout_blocker = TimeoutBlocker(timeout_seconds=1.0)
