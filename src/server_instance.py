from cache import Cache
import random

PENALTI_PER_KONEKSI = 0.05  

class ServerInstance:
    """
    Kelas untuk merepresentasikan satu instansi server.
    """
    def __init__(self, name, cache_policy='LRU', location=0, cache_size=10):
        self.name = name
        self.cache = Cache(cache_size, cache_policy)
        self.active_connections = 0
        self.requests_handled = 0
        self.total_response_time = 0
        self.location = location
        self.connections = [] # daftar waktu tersisa untuk koneksi yang aktif
        self.responses = []  # daftar waktu respons yang telah dihitung
        self.approx_response_time = 0

    def handle_request(self, request_key, client_location, miss_penalty=0.1, hit_benefit=0.005):
        """
        Mensimulasikan proses penanganan request.
        """
        self.connections = [c - 1 for c in self.connections if c > 1]  # Hapus koneksi yang sudah selesai
        self.connections.append(random.randint(50, 250))  # Simulasi waktu tersisa untuk koneksi
        self.active_connections = len(self.connections)
        self.requests_handled += 1
        
        is_hit = self.cache.get(request_key) is not None
        
        waktu_dasar = hit_benefit if is_hit else miss_penalty
        
        # Hitung faktor beban: semakin banyak koneksi, semakin lambat server merespons.
        faktor_beban = 1 + ((self.active_connections) * PENALTI_PER_KONEKSI)
        # Hitung latensi geografis 
        geographic_latency = abs(self.location - client_location) * 0.01

        response_time = waktu_dasar * faktor_beban + geographic_latency
        self.responses.append(response_time)
        if len(self.responses) > 10:
            self.responses.pop(0)        
        self.approx_response_time = sum(self.responses) / len(self.responses) if self.responses else 0
        
        if not is_hit:
            self.cache.set(request_key, f"data_for_{request_key}")
            
        self.total_response_time += response_time
        return is_hit, response_time
