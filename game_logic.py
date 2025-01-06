import tkinter as tk

class GameLogic:
    def __init__(self, canvas, positions):
        self.canvas = canvas
        self.positions = positions  # Daftar semua titik di papan
        self.manusia_pieces = []    # Pion manusia (biru)
        self.macan_piece = None     # Pion macan (merah)
        self.current_phase = "placement"  # Tahap awal: penempatan pion
        self.canvas.bind("<Button-1>", self.place_pieces)

    def place_pieces(self, event):
        """Menangani klik pada papan untuk menempatkan pion."""
        if self.current_phase != "placement":
            print("Pion sudah ditempatkan. Permainan dimulai!")
            return

        nearest_node = self.get_nearest_node(event.x, event.y)
        if not nearest_node:
            return  # Tidak ada titik terdekat (klik di luar papan)

        if len(self.manusia_pieces) == 0:
            self.place_manusia(nearest_node)
        elif self.macan_piece is None:
            self.place_macan(nearest_node)
            self.start_game()

    def get_nearest_node(self, x, y, threshold=10):
        """Cari titik terdekat dari posisi klik, dalam jarak threshold piksel."""
        for node in self.positions:
            if abs(node[0] - x) <= threshold and abs(node[1] - y) <= threshold:
                return node
        return None

    def place_manusia(self, node):
        """Menempatkan pion manusia dalam formasi 3x3."""
        valid_3x3_nodes = [
            (self.positions[6]), (self.positions[7]), (self.positions[8]),
            (self.positions[11]), (self.positions[12]), (self.positions[13]),
            (self.positions[16]), (self.positions[17]), (self.positions[18])
        ]

        # Pastikan klik berada di salah satu titik formasi 3x3
        if node not in valid_3x3_nodes:
            print("Pion manusia harus ditempatkan dalam formasi 3x3 di tengah papan!")
            return

        # Tambahkan semua pion 3x3 ke dalam daftar manusia_pieces
        self.manusia_pieces.extend(valid_3x3_nodes)
        for piece in valid_3x3_nodes:
            self.canvas.create_oval(
                piece[0] - 8, piece[1] - 8,
                piece[0] + 8, piece[1] + 8,
                fill="blue"
            )
        print("Pion manusia berhasil ditempatkan dalam formasi 3x3.")

    def place_macan(self, node):
        """Menempatkan pion macan jika valid."""
        if node in self.manusia_pieces:
            print("Tidak bisa menaruh pion macan di titik yang sama dengan pion manusia!")
            return

        if not self.is_safe_distance(node):
            print("Pion macan harus ditempatkan jauh dari pion manusia!")
            return

        self.macan_piece = node
        self.canvas.create_oval(
            node[0] - 8, node[1] - 8,
            node[0] + 8, node[1] + 8,
            fill="red"
        )
        print("Pion macan berhasil ditempatkan.")

    def is_safe_distance(self, node, min_distance=20):
        """Periksa apakah pion macan tidak bersebelahan dengan pion manusia."""
        for piece in self.manusia_pieces:
            if abs(piece[0] - node[0]) <= min_distance and abs(piece[1] - node[1]) <= min_distance:
                return False
        return True

    def start_game(self):
        """Memulai permainan setelah pion biru dan merah ditempatkan."""
        print("Semua pion sudah ditempatkan. Permainan dimulai!")
        self.current_phase = "game"
