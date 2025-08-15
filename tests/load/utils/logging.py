import json
import time
import os
from typing import Dict, List, Optional, Any

def log_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, log_prefix):
    log = {
        "timestamp": time.time(),
        "type": request_type,
        "endpoint": name,
        "status_code": getattr(response, "status_code", None),
        "response_time_ms": response_time,
        "response_length": response_length,
        "exception": str(exception) if exception else None,
        "url": url
    }
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{log_prefix}_results_{timestamp}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n") 