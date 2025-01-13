class TranspositionTable:
    def __init__(self, max_size=1000000):
        self.table = {}
        self.max_size = max_size

    def store(self, position_hash, depth, value, move):
        if len(self.table) >= self.max_size:
            # Hapus 10% entri terlama jika table penuh
            old_entries = int(self.max_size * 0.1)
            for _ in range(old_entries):
                self.table.popitem()
        
        self.table[position_hash] = (depth, value, move)

    def lookup(self, position_hash):
        return self.table.get(position_hash)

    def clear(self):
        self.table.clear() 