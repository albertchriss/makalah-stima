from collections import defaultdict

class Cache:
    """
    Kelas untuk merepresentasikan cache. Mendukung kebijakan LRU, LFU, dan FIFO.
    """
    def __init__(self, size, policy='LRU'):
        self.size = size
        self.policy = policy
        self.data = {}
        self.lru_order = []
        self.lfu_freq = defaultdict(int)
        self.fifo_order = []

    def get(self, key):
        """Mengambil data dari cache dan memperbarui metrik kebijakan."""
        if key in self.data:
            if self.policy == 'LRU':
                self.lru_order.remove(key)
                self.lru_order.append(key)
            elif self.policy == 'LFU':
                self.lfu_freq[key] += 1
            return self.data.get(key)
        return None

    def set(self, key, value):
        """Menyimpan data ke cache dan menerapkan kebijakan eviksi jika penuh."""
        if self.size == 0: return

        if key not in self.data and len(self.data) >= self.size:
            key_to_evict = None
            if self.policy == 'LRU':
                key_to_evict = self.lru_order.pop(0)
            elif self.policy == 'LFU':
                min_freq = float('inf')
                for k, v_freq in self.lfu_freq.items():
                    if v_freq < min_freq and k in self.data: # Pastikan kunci masih di data
                        min_freq = v_freq
                        key_to_evict = k
                if key_to_evict:
                    del self.lfu_freq[key_to_evict]
            elif self.policy == 'FIFO':
                key_to_evict = self.fifo_order.pop(0)
            
            if key_to_evict and key_to_evict in self.data:
                del self.data[key_to_evict]

        if key not in self.data:
            self.data[key] = value
            if self.policy == 'LRU':
                self.lru_order.append(key)
            elif self.policy == 'LFU':
                self.lfu_freq[key] = 1 # Inisialisasi frekuensi
            elif self.policy == 'FIFO':
                self.fifo_order.append(key)