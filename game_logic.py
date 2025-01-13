class GameLogic:

    def __init__(self, canvas, positions, player_choice):
        self.canvas = canvas
        self.positions = positions  # Daftar semua titik di papan
        self.player_choice = player_choice  # "Manusia" atau "Macan"
        self.manusia_pieces = []    # Pion manusia (biru)
        self.macan_piece = None     # Pion macan (merah)
        self.current_phase = "placement"  # Tahap awal: penempatan pion
        self.selected_piece = None  # Pion yang dipilih untuk digerakkan
        self.canvas.bind("<Button-1>", self.place_or_move_piece)
        self.current_player = "You"  # Set starting player
        self.turn_count = 0  # Initialize turn count
        
        # Ubah format label turn
        self.turn_label = self.canvas.create_text(
            250, 20, 
            text="Fase Penempatan: Letakkan 9 pion Manusia", 
            font=("Arial", 14), 
            fill="black"
        )
        self.game_over = False
        self.winner = None
        self.game_over_label = None

    def update_turn_label(self):
        """Update label sesuai fase dan giliran saat ini."""
        if self.current_phase == "placement":
            if len(self.manusia_pieces) == 0:
                text = "Fase Penempatan: Letakkan 9 pion Manusia"
            elif self.macan_piece is None:
                text = "Fase Penempatan: Letakkan pion Macan"
            else:
                text = "Fase Penempatan: Selesai"  # Tambahkan default text untuk fase placement
        else:  # fase game
            player_text = "Manusia" if self.player_choice == "Manusia" else "Macan"
            ai_text = "Macan" if self.player_choice == "Manusia" else "Manusia"
            
            if self.current_player == "You":
                text = f"Giliran {player_text} | Ronde: {self.turn_count}"
            else:
                text = f"Giliran {ai_text} | Ronde: {self.turn_count}"

        # Pastikan text selalu ada nilai default
        if not 'text' in locals():
            text = "Permainan Macanan"

        self.canvas.itemconfig(self.turn_label, text=text)

    def change_turn(self):
        """Ganti giliran pemain dan increment turn count."""
        if self.current_phase == "game":  # Hanya increment turn pada fase game
            if self.current_player == "AI":  # Increment hanya saat giliran AI selesai
                self.turn_count += 1
            
            if self.current_player == "You":
                self.current_player = "AI"
            else:
                self.current_player = "You"

        self.update_turn_label()

    def can_player_move_piece(self, piece):
        """Cek apakah player bisa menggerakkan pion tersebut."""
        if self.current_player != "You":
            return False
            
        if self.player_choice == "Manusia":
            return piece in self.manusia_pieces
        else:  # player_choice == "Macan"
            return piece == self.macan_piece

    def place_or_move_piece(self, event):
        """Menangani klik pada papan untuk menempatkan pion atau memilih pion yang akan digerakkan."""
        if self.game_over:
            return

        nearest_node = self.get_nearest_node(event.x, event.y)
        if not nearest_node:
            return

        turn_changed = False

        if self.current_phase == "placement":
            # Fase penempatan: semua player menempatkan pionnya
            if len(self.manusia_pieces) == 0:
                # Selalu biarkan player menempatkan pion manusia dulu
                self.place_manusia(nearest_node)
                turn_changed = True
            elif self.macan_piece is None:
                # Selalu biarkan player menempatkan pion macan
                self.place_macan(nearest_node)
                turn_changed = True
                
            # Cek apakah fase penempatan selesai
            if len(self.manusia_pieces) > 0 and self.macan_piece is not None:
                self.start_game()  # Mulai fase permainan

        else:  # current_phase == "game"
            if self.current_player == "AI":
                self.make_ai_move()
                return
            
            # Cek apakah player bisa menggerakkan pion yang dipilih
            if self.selected_piece is None:
                if self.can_player_move_piece(nearest_node):
                    self.select_piece(nearest_node)
            else:
                if self.move_piece(self.selected_piece, nearest_node):
                    turn_changed = True
                    self.make_ai_move()

        if turn_changed:
            self.change_turn()
            self.update_turn_label()  # Update label setelah setiap gerakan

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
        self.update_turn_label()  # Update label setelah penempatan
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
        self.update_turn_label()  # Update label setelah penempatan
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
        self.turn_count = 1  # Mulai dari ronde 1
        
        # Set giliran pertama sesuai pilihan player
        if self.player_choice == "Manusia":
            self.current_player = "You"
        else:
            self.current_player = "AI"
            self.make_ai_move()
            
        self.update_turn_label()

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
            for move in valid_moves:  # Ubah untuk mengakomodasi tuple (target, eaten)
                valid_node = move[0]  # Ambil target node dari tuple
                self.canvas.create_rectangle(
                    valid_node[0] - 8, valid_node[1] - 8,
                    valid_node[0] + 8, valid_node[1] + 8,
                    outline="green", width=2, tags="highlight"
                )

    def get_valid_moveable_positions(self, node):
        """Mendapatkan semua posisi valid yang bisa dituju mengikuti garis pada papan."""
        if not node:
            return []
        
        valid_moves = []
        try:
            node_index = self.positions.index(node)
            row, col = node_index // 5, node_index % 5
        except ValueError:
            print(f"Node tidak valid: {node}")
            return []

        # Definisi garis yang valid pada papan 5x5
        valid_lines = [
            # Garis horizontal
            [(0, -1), (0, 1)],  # kiri, kanan
            # Garis vertikal
            [(-1, 0), (1, 0)],  # atas, bawah
            # Garis diagonal (hanya untuk posisi yang memiliki garis diagonal)
            [(-1, -1), (1, 1)],  # diagonal kiri atas ke kanan bawah
            [(-1, 1), (1, -1)]   # diagonal kanan atas ke kiri bawah
        ]

        # Cek apakah posisi memiliki garis diagonal
        has_diagonal = self._has_diagonal_lines(row, col)
        
        for line_directions in valid_lines:
            if not has_diagonal and (line_directions[0][0] != 0 and line_directions[0][1] != 0):
                continue  # Skip diagonal jika posisi tidak memiliki garis diagonal
            
            for dx, dy in line_directions:
                new_row, new_col = row + dx, col + dy
                
                # Cek apakah masih dalam papan
                if 0 <= new_row < 5 and 0 <= new_col < 5:
                    new_node = self.positions[new_row * 5 + new_col]
                    
                    # Untuk macan, cek kemungkinan melompat
                    if node == self.macan_piece:
                        if new_node in self.manusia_pieces:
                            # Cek posisi setelah lompatan
                            jump_row, jump_col = new_row + dx, new_col + dy
                            if 0 <= jump_row < 5 and 0 <= jump_col < 5:
                                jump_node = self.positions[jump_row * 5 + jump_col]
                                if jump_node not in self.manusia_pieces and jump_node != self.macan_piece:
                                    valid_moves.append((jump_node, new_node))
                        elif new_node not in self.manusia_pieces:
                            valid_moves.append((new_node, None))
                    
                    # Untuk pion manusia, hanya gerakan normal
                    elif node in self.manusia_pieces:
                        if new_node not in self.manusia_pieces and new_node != self.macan_piece:
                            valid_moves.append((new_node, None))

        return valid_moves

    def _has_diagonal_lines(self, row, col):
        """Cek apakah posisi memiliki garis diagonal."""
        # Posisi yang memiliki garis diagonal:
        diagonal_positions = [
            # Posisi di dalam grid 5x5 yang memiliki garis diagonal
            (1, 1), (1, 3),  # Baris 1
            (2, 0), (2, 2), (2, 4),  # Baris 2
            (3, 1), (3, 3),  # Baris 3
            # Tambahkan posisi lain sesuai dengan desain papan
        ]
        
        return (row, col) in diagonal_positions

    def move_piece(self, selected_piece, target_node):
        """Pindahkan pion yang dipilih ke target node dengan kemampuan makan untuk macan."""
        valid_moves = self.get_valid_moveable_positions(selected_piece)
        valid_targets = [move[0] for move in valid_moves]
        
        if target_node not in valid_targets:
            print("Gerakan tidak valid!")
            self.selected_piece = None
            self.canvas.delete("highlight")
            return False

        # Cari apakah ada pion yang dimakan
        eaten_piece = None
        for move in valid_moves:
            if move[0] == target_node:
                eaten_piece = move[1]
                break

        # Hapus pion yang dimakan (jika ada)
        if eaten_piece:
            self.manusia_pieces.remove(eaten_piece)
            self.canvas.create_oval(
                eaten_piece[0] - 8, eaten_piece[1] - 8,
                eaten_piece[0] + 8, eaten_piece[1] + 8,
                fill="black"
            )

        # Lakukan perpindahan pion
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

        # Update posisi pion
        if selected_piece in self.manusia_pieces:
            self.manusia_pieces.remove(selected_piece)
            self.manusia_pieces.append(target_node)
        else:
            self.macan_piece = target_node

        # Cek kondisi menang setelah gerakan
        self.check_win_condition()

        # Reset selection dan hapus highlight
        self.selected_piece = None
        self.canvas.delete("highlight")

        return True

    def check_win_condition(self):
        """Cek kondisi menang untuk kedua pemain."""
        if len(self.manusia_pieces) <= 3:
            self.game_over = True
            self.winner = "Macan"
            self.show_game_over()
        elif self.is_macan_trapped():
            self.game_over = True
            self.winner = "Manusia"
            self.show_game_over()

    def is_macan_trapped(self):
        """Cek apakah macan terkepung dan tidak bisa bergerak."""
        if not self.macan_piece:  # Tambah pengecekan untuk macan_piece None
            return False
        valid_moves = self.get_valid_moveable_positions(self.macan_piece)
        return len(valid_moves) == 0

    def show_game_over(self):
        """Tampilkan pesan game over."""
        if not self.game_over_label:
            self.game_over_label = self.canvas.create_text(
                250, 50,
                text=f"Game Over! {self.winner} Menang!",
                font=("Arial", 20),
                fill="green"
            )

    def make_ai_move(self):
        """Membuat gerakan AI dengan analisis performa."""
        from ai_logic import MacananAI
        
        if not self.game_over:
            ai = MacananAI(self)
            is_macan = self.player_choice == "Manusia"
            
            # Analisis gerakan sebelumnya
            ai.analyze_last_moves()
            
            best_move = ai.get_best_move(is_macan)
            
            if best_move:
                from_pos, to_pos = best_move
                self.selected_piece = from_pos
                self.move_piece(from_pos, to_pos)
                self.change_turn()

