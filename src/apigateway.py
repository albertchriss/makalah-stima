import hashlib

class APIGateway:
    """
    Kelas untuk merepresentasikan Load Balancer.
    """
    def __init__(self, servers):
        self.servers = servers
        self.round_robin_index = 0

    def dispatch(self, strategy, request_key, client_location=0):
        """Memilih server berdasarkan strategi yang diberikan."""
        if strategy == "Sticky Session":
            server_index = int(hashlib.sha1(request_key.encode("utf-8")).hexdigest(), 16) % len(self.servers)
            return self.servers[server_index]
        
        elif strategy == "Least Connections":
            return min(self.servers, key=lambda s: s.active_connections)

        elif strategy == "Least Response Time":
            avg_response_times = [s.approx_response_time for s in self.servers]
            best_server_index = avg_response_times.index(min(avg_response_times))
            return self.servers[best_server_index]

        elif strategy == "Geographic":
            return min(self.servers, key=lambda s: abs(s.location - client_location))
            
        elif strategy == "Round Robin":
            server = self.servers[self.round_robin_index]
            self.round_robin_index = (self.round_robin_index + 1) % len(self.servers)
            return server