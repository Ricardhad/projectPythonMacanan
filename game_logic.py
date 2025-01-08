class GameLogic:

    def __init__(self, canvas, positions):
        self.canvas = canvas
        self.positions = positions  # Daftar semua titik di papan
        self.manusia_pieces = []    # Pion manusia (biru)
        self.macan_piece = None     # Pion macan (merah)
        self.current_phase = "placement"  # Tahap awal: penempatan pion
        self.selected_piece = None  # Pion yang dipilih untuk digerakkan
        self.canvas.bind("<Button-1>", self.place_or_move_piece)
        self.current_player = "You"  # Set starting player
        self.turn_count = 0  # Initialize turn count
        self.turn_label = self.canvas.create_text(
            250, 20, text=f"Turn: {self.current_player} | Round: {self.turn_count}", font=("Arial", 14), fill="black"
        )

    def change_turn(self):
        """Ganti giliran pemain dan increment turn count."""
        if self.current_player == "You":
            self.current_player = "AI"
        else:
            self.current_player = "You"
        
        # Increment the turn count after each round
        self.turn_count += 1

        # Update the turn label text
        self.canvas.itemconfig(self.turn_label, text=f"Turn: {self.current_player} | Round: {self.turn_count}")

    def place_or_move_piece(self, event):
        """Menangani klik pada papan untuk menempatkan pion atau memilih pion yang akan digerakkan."""
        nearest_node = self.get_nearest_node(event.x, event.y)
        if not nearest_node:
            return  # If no valid node is found, do nothing

        turn_changed = False  # Flag to track if the turn should be changed

        if self.current_phase == "placement":
            # Logika penempatan yang sudah ada
            if len(self.manusia_pieces) == 0:
                self.place_manusia(nearest_node)
                turn_changed = True
            elif self.macan_piece is None:
                self.place_macan(nearest_node)
                self.start_game()
                turn_changed = True
        else:  # current_phase == "game"
            if self.selected_piece is None:
                # Pilih pion untuk digerakkan
                if nearest_node in self.manusia_pieces or nearest_node == self.macan_piece:
                    self.select_piece(nearest_node)
            else:
                # Coba gerakkan pion yang sudah dipilih
                if self.move_piece(self.selected_piece, nearest_node):
                    turn_changed = True

        # After handling the move or placement, switch turns only if the action was valid
        if turn_changed:
            self.change_turn()

    def get_nearest_node(self, x, y, threshold=10):
        """Cari titik terdekat dari posisi klik, dalam jarak threshold piksel."""
        for node in self.positions:
            if abs(node[0] - x) <= threshold and abs(node[1] - y) <= threshold:
                return node
        return None

    def place_manusia(self, node):
        """Menempatkan pion manusia dalam formasi 3x3 di dalam papan 5x5."""
        valid_3x3_nodes = []
        node_index = self.positions.index(node)
        row, col = node_index // 5, node_index % 5  # Menentukan baris dan kolom dari titik yang diklik

        # Pastikan formasi 3x3 hanya ditempatkan di dalam papan 5x5
        if 1 <= row <= 3 and 1 <= col <= 3:
            for r in range(row-1, row+2):  # Formasi 3x3, -1, 0, +1 baris
                for c in range(col-1, col+2):  # Formasi 3x3, -1, 0, +1 kolom
                    valid_3x3_nodes.append(self.positions[r * 5 + c])

        # Pastikan titik berada dalam formasi 3x3 yang valid
        if node not in valid_3x3_nodes:
            print("Pion manusia harus ditempatkan dalam formasi 3x3 yang valid di papan!")
            return

        # Tambahkan pion manusia dalam formasi 3x3 ke dalam daftar manusia_pieces
        self.manusia_pieces.extend(valid_3x3_nodes)
        for piece in valid_3x3_nodes:
            self.canvas.create_oval(
                piece[0] - 8, piece[1] - 8,
                piece[0] + 8, piece[1] + 8,
                fill="blue"
            )
        print("Pion manusia berhasil ditempatkan dalam formasi 3x3.")
        
    def place_macan(self, node):
        """Menempatkan pion macan jika valid. Hapus macan jika ditempatkan di sisi biru."""
        if node in self.manusia_pieces:
            print("Tidak bisa menaruh pion macan di titik yang sama dengan pion manusia!")
            return

        if not self.is_safe_distance(node):
            print("Pion macan harus ditempatkan jauh dari pion manusia!")
            return

        # Check if the macan piece is on the blue side and remove it if so
        if node in self.manusia_pieces:
            self.remove_macan()
            print("Pion macan dihapus karena ditempatkan di sisi biru.")
            return

        # If it's valid, proceed with placement
        self.macan_piece = node
        self.canvas.create_oval(
            node[0] - 8, node[1] - 8,
            node[0] + 8, node[1] + 8,
            fill="red"
        )
        print("Pion macan berhasil ditempatkan.")

    def remove_macan(self):
        """Hapus pion macan jika sudah ada."""
        if self.macan_piece:
            self.canvas.create_oval(
                self.macan_piece[0] - 8, self.macan_piece[1] - 8,
                self.macan_piece[0] + 8, self.macan_piece[1] + 8,
                fill="black"
            )
            self.macan_piece = None


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

    def select_piece(self, node):
        """Pilih pion untuk digerakkan."""
        if node in self.manusia_pieces or node == self.macan_piece:
            self.selected_piece = node
            # Hapus highlight sebelumnya
            self.canvas.delete("highlight")
            
            # Highlight pion yang dipilih
            self.canvas.create_oval(
                node[0] - 8, node[1] - 8,
                node[0] + 8, node[1] + 8,
                outline="yellow", width=2, tags="highlight"
            )
            
            # Highlight area yang bisa digerakkan
            valid_moves = self.get_valid_moveable_positions(node)
            for valid_node in valid_moves:
                self.canvas.create_rectangle(
                    valid_node[0] - 8, valid_node[1] - 8,
                    valid_node[0] + 8, valid_node[1] + 8,
                    outline="green", width=2, tags="highlight"
                )

    def get_valid_moveable_positions(self, node):
        """Mendapatkan semua posisi valid yang bisa dituju dalam formasi segitiga."""
        valid_moves = []
        node_index = self.positions.index(node)
        row, col = node_index // 5, node_index % 5

         
        directions = [
                (-1, 0),  # atas
                (1, 0),   # bawah
                (0, -1),  # kiri
                (0, 1),   # kanan
            ]

        for dx, dy in directions:
                new_row, new_col = row + dx, col + dy
                if 0 <= new_row < 5 and 0 <= new_col < 5:
                    new_node = self.positions[new_row * 5 + new_col]
                    # Pastikan posisi baru tidak ditempati pion lain
                    if new_node not in self.manusia_pieces and new_node != self.macan_piece:
                        # Add the new node to valid moves if within triangular grid constraints
                        valid_moves.append(new_node)

        return valid_moves

        
    def move_piece(self, selected_piece, target_node):
            """Pindahkan pion yang dipilih ke target node dengan posisi segitiga."""
            if target_node not in self.get_valid_moveable_positions(selected_piece):
                print("Gerakan tidak valid!")
                self.selected_piece = None
                self.canvas.delete("highlight")
                return False  # Invalid move, return False

            # Valid move, proceed with the movement
            piece_color = "blue" if selected_piece in self.manusia_pieces else "red"
            
            # Hapus pion dari posisi lama
            self.canvas.create_oval(
                selected_piece[0] - 8, selected_piece[1] - 8,
                selected_piece[0] + 8, selected_piece[1] + 8,
                fill="black"
            )

            # Gambar pion di posisi baru
            self.canvas.create_oval(
                target_node[0] - 8, target_node[1] - 8,
                target_node[0] + 8, target_node[1] + 8,
                fill=piece_color
            )

            # Update posisi pion dalam list
            if selected_piece in self.manusia_pieces:
                self.manusia_pieces.remove(selected_piece)
                self.manusia_pieces.append(target_node)
            else:  # Macan piece
                self.macan_piece = target_node

            # Reset selection dan hapus highlight
            self.selected_piece = None
            self.canvas.delete("highlight")

            return True  # Valid move, return True

