from http.server import BaseHTTPRequestHandler
import json
import statistics

pp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

TELEMETRY_DATA = [
    {"region": "emea", "latency_ms": 120, "uptime": 0.998},
    {"region": "amer", "latency_ms": 95, "uptime": 0.995},
    {"region": "emea", "latency_ms": 210, "uptime": 0.997},
    {"region": "amer", "latency_ms": 88, "uptime": 0.999},
    {"region": "emea", "latency_ms": 165, "uptime": 0.996},
    {"region": "amer", "latency_ms": 192, "uptime": 0.994},
    {"region": "emea", "latency_ms": 145, "uptime": 0.998},
    {"region": "amer", "latency_ms": 78, "uptime": 0.997},
    {"region": "emea", "latency_ms": 130, "uptime": 0.995},
    {"region": "amer", "latency_ms": 105, "uptime": 0.996},
    {"region": "emea", "latency_ms": 155, "uptime": 0.998},
    {"region": "amer", "latency_ms": 82, "uptime": 0.997}
]

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests to /api/analyze"""
        if self.path == '/api/analyze':
            try:
                # Read and parse the request body
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data)
                
                regions = request_data.get('regions', [])
                threshold_ms = request_data.get('threshold_ms', 180)
                
                results = {}
                
                for region in regions:
                    # Filter records for this region
                    region_data = [item for item in TELEMETRY_DATA if item.get('region') == region]
                    
                    if not region_data:
                        results[region] = {
                            "avg_latency": 0,
                            "p95_latency": 0,
                            "avg_uptime": 0,
                            "breaches": 0
                        }
                        continue
                    
                    # Extract latencies and uptimes
                    latencies = [item['latency_ms'] for item in region_data]
                    uptimes = [item['uptime'] for item in region_data]
                    
                    # Calculate metrics
                    avg_latency = statistics.mean(latencies)
                    
                    # Calculate 95th percentile
                    sorted_latencies = sorted(latencies)
                    n = len(sorted_latencies)
                    p95_index = min(int(0.95 * n), n - 1)
                    p95_latency = sorted_latencies[p95_index]
                    
                    avg_uptime = statistics.mean(uptimes)
                    breaches = sum(1 for latency in latencies if latency > threshold_ms)
                    
                    results[region] = {
                        "avg_latency": round(avg_latency, 2),
                        "p95_latency": round(p95_latency, 2),
                        "avg_uptime": round(avg_uptime, 4),
                        "breaches": breaches
                    }
                
                # Send successful response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(results).encode())
                
            except Exception as e:
                # Send error response
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"error": f"Analysis failed: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        
        else:
            # Path not found
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
