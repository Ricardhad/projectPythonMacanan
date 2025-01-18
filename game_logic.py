import random

class GameLogic:

    def __init__(self, canvas, positions, player_choice, mode="AI", pvp_roles=None):
        self.canvas = canvas
        self.positions = positions
        self.player_choice = player_choice
        self.mode = mode
        self.pvp_roles = pvp_roles  # Tambahkan roles untuk PvP
        self.manusia_pieces = []
        self.macan_piece = []
        self.current_phase = "placement"
        self.selected_piece = None
        self.canvas.bind("<Button-1>", self.place_or_move_piece)
        self.current_player = "Macan"  # Selalu mulai dengan Macan
        self.turn_count = 1  # Mulai dari turn 1
        
        self.turn_label = self.canvas.create_text(
            250, 20, 
            text="Turn 1: Letakkan pion Macan pertama", 
            font=("Arial", 14), 
            fill="black"
        )
        self.game_over = False
        self.winner = None
        self.game_over_label = None
        self._reached_max_manusia = False  # Tambahkan flag ini di __init__
        self._max_manusia_count = 0  # Tambahkan counter untuk tracking jumlah maksimal
        
        # Jika player memilih manusia, buat AI langsung bergerak di turn pertama
        if mode == "AI" and player_choice == "Manusia":
            self.make_ai_move()

        self.game_over_overlay = None
        self.game_over_frame = None
        self.restart_button = None
        self.menu_button = None

        # Tambahkan label role untuk mode PvP
        if mode == "PVP" and pvp_roles:
            self.role_label = self.canvas.create_text(
                600, 20,
                text=f"{pvp_roles[0]} | {pvp_roles[1]}",
                font=("Arial", 12),
                fill="black"
            )

    def update_turn_label(self):
        """Update label sesuai turn saat ini."""
        if self.turn_count <= 3:  # Turn 1-3: Fase penempatan macan dan manusia pertama
            if self.current_player == "Macan":
                text = f"Turn {self.turn_count}: Letakkan pion Macan ke-{len(self.macan_piece) + 1}"
            else:
                text = f"Turn {self.turn_count}: Letakkan pion Manusia ke-{len(self.manusia_pieces) + 1}"
        else:  # Turn 4+
            if self.current_phase == "placement":  # Masih fase penempatan
                if self.current_player == "Manusia":
                    text = f"Turn {self.turn_count}: Letakkan pion Manusia ke-{len(self.manusia_pieces) + 1}"
                else:  # Macan's turn
                    text = f"Turn {self.turn_count}: Giliran Macan bergerak"
            else:  # Fase movement
                if self.current_player == "Macan":
                    text = f"Turn {self.turn_count}: Giliran Macan bergerak"
                else:
                    text = f"Turn {self.turn_count}: Giliran Manusia bergerak"
            
        self.canvas.itemconfig(self.turn_label, text=text)

    def place_or_move_piece(self, event):
        """Menangani klik pada papan."""
        if self.game_over:
            return

        nearest_node = self.get_nearest_node(event.x, event.y)
        if not nearest_node:
            return

        # Dalam mode PVP, semua giliran valid
        if self.mode == "PVP":
            is_player_turn = True
        else:
            # Dalam mode AI, cek giliran player
            is_player_turn = ((self.player_choice == "Macan" and self.current_player == "Macan") or
                             (self.player_choice == "Manusia" and self.current_player == "Manusia"))
        
        if not is_player_turn:
            return

        # Fase penempatan awal (2 macan dan manusia pertama)
        if self.turn_count <= 3:
            if self.current_player == "Macan" and len(self.macan_piece) < 2:
                if self.place_macan(nearest_node):
                    self.current_player = "Manusia"
                    self.turn_count += 1
                    self.update_turn_label()
                    if self.mode == "AI" and self.player_choice == "Macan":
                        self.make_ai_move()
            elif self.current_player == "Manusia" and len(self.manusia_pieces) < 8:
                if self.place_manusia(nearest_node):
                    self.current_player = "Macan"
                    self.turn_count += 1
                    self.update_turn_label()
                    if self.mode == "AI" and self.player_choice == "Manusia":
                        self.make_ai_move()
        # Fase setelah penempatan awal
        else:
            # Jika masih dalam fase penempatan manusia (belum mencapai 8)
            if self.current_phase == "placement" and self.current_player == "Manusia" and len(self.manusia_pieces) < 8:
                if self.place_manusia(nearest_node):
                    self.current_player = "Macan"
                    self.turn_count += 1
                    self.update_turn_label()
                    if self.mode == "AI" and self.player_choice == "Manusia":
                        self.make_ai_move()
            # Fase pergerakan
            else:
                if self.selected_piece is None:
                    if self.can_player_move_piece(nearest_node):
                        self.select_piece(nearest_node)
                else:
                    if self.move_piece(self.selected_piece, nearest_node):
                        self.current_player = "Manusia" if self.current_player == "Macan" else "Macan"
                        self.turn_count += 1
                        self.update_turn_label()
                        if self.mode == "AI":
                            if ((self.player_choice == "Macan" and self.current_player == "Manusia") or
                                (self.player_choice == "Manusia" and self.current_player == "Macan")):
                                self.make_ai_move()

    def get_nearest_node(self, x, y, threshold=10):
        """Cari titik terdekat dari posisi klik, dalam jarak threshold piksel."""
        for node in self.positions:
            if abs(node[0] - x) <= threshold and abs(node[1] - y) <= threshold:
                return node
        return None

    def _is_valid_placement_position(self, node):
        """Cek apakah posisi valid untuk penempatan pion (hanya dalam kotak 5x5)."""
        try:
            node_index = self.positions.index(node)
            # Hanya posisi 0-24 yang merupakan kotak 5x5
            return 0 <= node_index < 25
        except ValueError:
            return False

    def place_macan(self, node):
        """Menempatkan pion macan jika valid."""
        if len(self.macan_piece) >= 2:
            print("Sudah mencapai batas maksimal pion macan!")
            return False

        if not self._is_valid_placement_position(node):
            print("Pion hanya boleh ditempatkan di dalam kotak 5x5!")
            return False

        if node in self.manusia_pieces or node in self.macan_piece:
            print("Posisi sudah ditempati!")
            return False

        # Cek jarak dengan macan lain jika sudah ada macan pertama
        if len(self.macan_piece) == 1:
            macan1_pos = self.macan_piece[0]
            dist = abs(macan1_pos[0] - node[0]) + abs(macan1_pos[1] - node[1])
            print(dist)
            if dist <= 160:  # Pastikan jarak minimal 50
                print("Macan kedua harus ditempatkan jauh dari macan pertama!")
                return False

        # Tambahkan macan baru
        self.macan_piece.append(node)
        self.canvas.create_oval(
            node[0] - 8, node[1] - 8,
            node[0] + 8, node[1] + 8,
            fill="red"
        )
        print(f"Pion macan ke-{len(self.macan_piece)} berhasil ditempatkan.")
        return True

    def place_manusia(self, node):
        """Menempatkan satu pion manusia pada posisi yang valid."""
        if len(self.manusia_pieces) >= 8:
            print("Sudah mencapai batas maksimal pion manusia!")
            return False

        if not self._is_valid_placement_position(node):
            print("Pion hanya boleh ditempatkan di dalam kotak 5x5!")
            return False

        if node in self.manusia_pieces or node in self.macan_piece:
            print("Posisi sudah ditempati!")
            return False

        # Tambahkan pion manusia
        self.manusia_pieces.append(node)
        self.canvas.create_oval(
            node[0] - 8, node[1] - 8,
            node[0] + 8, node[1] + 8,
            fill="blue"
        )
        print(f"Pion manusia ke-{len(self.manusia_pieces)} berhasil ditempatkan.")
        return True

    def remove_macan(self):
        """Hapus pion macan jika sudah ada."""
        if self.macan_piece:
            self.canvas.create_oval(
                self.macan_piece[0] - 8, self.macan_piece[1] - 8,
                self.macan_piece[0] + 8, self.macan_piece[1] + 8,
                fill="black"
            )
            self.macan_piece = None


    def is_safe_distance(self, node, min_distance=80):
        """Periksa apakah pion macan tidak bersebelahan dengan pion manusia."""
        # Cek jarak dengan pion manusia
        for piece in self.manusia_pieces:
            if abs(piece[0] - node[0]) <= min_distance and abs(piece[1] - node[1]) <= min_distance:
                print(abs(piece[0] - node[0]) <= min_distance and abs(piece[1] - node[1]))
                print("Pion manusia tidak boleh diletakkan bersebelahan dengan macan!")
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
        else:  # player_choice == "Macan"
            self.current_player = "You"  # Ubah dari AI ke You agar player macan bisa jalan duluan
            
        self.update_turn_label()

    def select_piece(self, node):
        """Pilih pion untuk digerakkan."""
        if ((self.player_choice == "Manusia" and node in self.manusia_pieces) or 
            (self.player_choice == "Macan" and node in self.macan_piece)):
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
            for move in valid_moves:
                valid_node = move[0]
                self.canvas.create_rectangle(
                    valid_node[0] - 8, valid_node[1] - 8,
                    valid_node[0] + 8, valid_node[1] + 8,
                    outline="green", width=2, tags="highlight"
                )

    def get_valid_moveable_positions(self, node):
        """Mendapatkan semua posisi valid yang bisa dituju."""
        if not node or node not in self.positions:
            print(f"Node tidak valid: {node}")
            return []
            
        valid_moves = []
        try:
            node_index = self.positions.index(node)
            row, col = node_index // 5, node_index % 5
        except ValueError:
            print(f"Node tidak valid: {node}")
            return []

        # Definisi arah pergerakan dasar
        orthogonal = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Vertikal & horizontal
        diagonal = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonal
        
        # Tentukan arah yang valid berdasarkan posisi
        directions = orthogonal.copy()
        if self._has_diagonal_lines(row, col):
            directions.extend(diagonal)

        # Periksa setiap arah
        for dx, dy in directions:
            new_row, new_col = row + dx, col + dy
            if self._is_valid_position(new_row, new_col, node, dx, dy):
                new_node = self._get_node_at_position(new_row, new_col)
                
                if not new_node or new_node not in self.positions:
                    continue
                    
                if node in self.macan_piece:  # Logika untuk Macan
                    # Cek gerakan normal - tidak boleh ke posisi macan lain
                    if (new_node not in self.manusia_pieces and 
                        new_node not in self.macan_piece):  # Tambah pengecekan macan lain
                        valid_moves.append((new_node, None))
                        
                    # Cek gerakan makan
                    elif new_node in self.manusia_pieces:
                        jump_row, jump_col = new_row + dx, new_col + dy
                        jump_node = self._get_node_at_position(jump_row, jump_col)
                        if (jump_node and 
                            jump_node in self.positions and
                            jump_node not in self.manusia_pieces and 
                            jump_node not in self.macan_piece and  # Tambah pengecekan macan lain
                            self._is_valid_position(jump_row, jump_col, new_node, dx, dy)):
                            valid_moves.append((jump_node, new_node))
                            
                else:  # Logika untuk Manusia
                    if new_node not in self.manusia_pieces and new_node not in self.macan_piece:
                        # Manusia hanya bisa bergerak satu langkah
                        valid_moves.append((new_node, None))

        return valid_moves

    def _has_diagonal_lines(self, row, col):
        """Cek apakah posisi memiliki garis diagonal."""
        # Posisi dalam grid 5x5 yang memiliki garis diagonal
        diagonal_positions = [
            # Baris pertama (indeks 0)
            (0, 0), (0, 2), (0, 4),
            # Baris kedua (indeks 1)
            (1, 1), (1, 3),
            # Baris ketiga (indeks 2)
            (2, 0), (2, 2), (2, 4),
            # Baris keempat (indeks 3)
            (3, 1), (3, 3),
            # Baris kelima (indeks 4)
            (4, 0), (4, 2), (4, 4)
        ]
        
        # Periksa posisi dalam grid 5x5
        if (row, col) in diagonal_positions:
            return True
            
        # Periksa area segitiga kiri dan kanan
        node_index = row * 5 + col
        if node_index >= len(self.positions):  # Node berada di area segitiga
            node = self.positions[node_index]
            # Area segitiga kiri
            if 100 <= node[0] <= 200 and 150 <= node[1] <= 250:
                return True
            # Area segitiga kanan
            if 600 <= node[0] <= 700 and 150 <= node[1] <= 250:
                return True
            

    def _is_valid_position(self, row, col, current_node, dx, dy):
        """Cek apakah posisi valid dalam papan permainan."""
        # Cek papan utama 5x5
        if 0 <= row < 5 and 0 <= col < 5:
            return True

        # Hitung posisi target
        target_x = current_node[0] + dx * 50
        target_y = current_node[1] + dy * 50

        # Cek area segitiga kiri
        if (100 <= current_node[0] <= 200 and 150 <= current_node[1] <= 250 and
            100 <= target_x <= 200 and 150 <= target_y <= 250):
            return True

        # Cek area segitiga kanan
        if (600 <= current_node[0] <= 700 and 150 <= current_node[1] <= 250 and
            600 <= target_x <= 700 and 150 <= target_y <= 250):
            return True

        return False

    def _get_node_at_position(self, row, col):
        """Dapatkan node pada posisi tertentu."""
        # Cek dalam grid 5x5
        if 0 <= row < 5 and 0 <= col < 5:
            return self.positions[row * 5 + col]

        # Cek dalam daftar node segitiga
        for node in self.positions[25:]:  # Node setelah grid 5x5 adalah node segitiga
            if abs(node[0] - (200 + col * 50)) < 10 and abs(node[1] - (200 + row * 50)) < 10:
                return node

        return None

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
        else:  # Macan
            macan_index = self.macan_piece.index(selected_piece)
            self.macan_piece[macan_index] = target_node

        # Cek kondisi menang setelah gerakan
        self.check_win_condition()

        # Reset selection dan hapus highlight
        self.selected_piece = None
        self.canvas.delete("highlight")

        return True

    def check_win_condition(self):
        """Cek kondisi menang untuk kedua pemain."""
        # Track jumlah maksimal pion manusia yang pernah ada
        if len(self.manusia_pieces) > self._max_manusia_count:
            self._max_manusia_count = len(self.manusia_pieces)
        
        # Jika sudah pernah mencapai 8 pion, set flag
        if self._max_manusia_count >= 8:
            self._reached_max_manusia = True
            # Setelah mencapai 8, pion hanya bisa bergerak
            self.current_phase = "movement"

        # Cek kondisi menang
        if self._reached_max_manusia:  # Hanya cek setelah pernah mencapai 8 pion
            if len(self.manusia_pieces) <= 3:  # Manusia kalah jika tersisa 3 atau kurang
                self.game_over = True
                self.winner = "Macan"
                self.show_game_over()
            elif self.is_macan_trapped():  # Macan kalah jika terkepung
                self.game_over = True
                self.winner = "Manusia"
                self.show_game_over()

    def is_macan_trapped(self):
        """Cek apakah semua macan terkepung dan tidak bisa bergerak."""
        if not self.macan_piece:  # Jika tidak ada macan
            return False
        
        # Cek apakah ada macan yang bisa bergerak
        for macan in self.macan_piece:
            valid_moves = self.get_valid_moveable_positions(macan)
            if len(valid_moves) > 0:
                return False
        return True

    def show_game_over(self):
        """Tampilkan layar game over."""
        if not self.game_over_label:
            # Buat overlay semi-transparan
            self.game_over_overlay = self.canvas.create_rectangle(
                0, 0, 800, 600,
                fill="black", stipple="gray50",
                tags="game_over"
            )

            # Buat frame untuk pesan
            self.game_over_frame = self.canvas.create_rectangle(
                200, 150, 500, 350,
                fill="white", outline="gold",
                width=3,
                tags="game_over"
            )

            # Tentukan pesan berdasarkan mode
            if self.mode == "PVP":
                if self.winner == "Macan":
                    message = "Macan Wins!"
                else:
                    message = "Manusia Wins!"
                text_color = "green"
            else:
                # Tentukan apakah player menang
                is_player_win = ((self.player_choice == "Macan" and self.winner == "Macan") or
                                (self.player_choice == "Manusia" and self.winner == "Manusia"))
                if is_player_win:
                    message = "Congratulations!\nYou Win!"
                    text_color = "green"
                else:
                    message = "Game Over!\nYou Lose!"
                    text_color = "red"

            self.game_over_label = self.canvas.create_text(
                350, 200,
                text=message,
                font=("Arial", 24, "bold"),
                fill=text_color,
                justify="center",
                tags="game_over"
            )

            # Buat tombol Main Lagi
            restart_btn = self.canvas.create_rectangle(
                250, 250, 450, 285,
                fill="lightblue", outline="blue",
                tags="game_over"
            )
            restart_text = self.canvas.create_text(
                350, 267,
                text="Main Lagi",
                font=("Arial", 14, "bold"),
                fill="blue",
                tags="game_over"
            )

            # Buat tombol Kembali ke Menu
            menu_btn = self.canvas.create_rectangle(
                250, 300, 450, 335,
                fill="lightgreen", outline="green",
                tags="game_over"
            )
            menu_text = self.canvas.create_text(
                350, 317,
                text="Kembali ke Menu",
                font=("Arial", 14, "bold"),
                fill="green",
                tags="game_over"
            )

            # Bind event click untuk tombol
            self.canvas.tag_bind(restart_btn, "<Button-1>", self.restart_game)
            self.canvas.tag_bind(restart_text, "<Button-1>", self.restart_game)
            self.canvas.tag_bind(menu_btn, "<Button-1>", self.back_to_menu)
            self.canvas.tag_bind(menu_text, "<Button-1>", self.back_to_menu)

    def restart_game(self, event=None):
        """Mulai permainan baru dengan pilihan yang sama."""
        # Hapus semua elemen game over
        self.canvas.delete("game_over")
        
        # Reset semua variabel game
        self.manusia_pieces = []
        self.macan_piece = []
        self.current_phase = "placement"
        self.selected_piece = None
        self.current_player = "Macan"
        self.turn_count = 1
        self.game_over = False
        self.winner = None
        self.game_over_label = None
        self._reached_max_manusia = False
        self._max_manusia_count = 0

        # Hapus semua pion dari papan
        self.canvas.delete("all")
        
        # Gambar ulang papan dan label
        from draw_board import draw_board
        draw_board(self.canvas, 400, 200)
        
        self.turn_label = self.canvas.create_text(
            250, 20, 
            text="Turn 1: Letakkan pion Macan pertama", 
            font=("Arial", 14), 
            fill="black"
        )

        # Jika player memilih manusia, buat AI langsung bergerak
        if self.player_choice == "Manusia":
            self.make_ai_move()

    def back_to_menu(self, event=None):
        """Kembali ke menu utama."""
        # Hapus semua elemen game
        self.canvas.delete("all")
        
        # Import dan tampilkan menu
        from catur_macanan import show_start_screen
        root = self.canvas.winfo_toplevel()
        show_start_screen()

    def make_ai_move(self):
        """Membuat gerakan AI."""
        if self.game_over:
            return

        max_attempts = 5
        for _ in range(max_attempts):
            if self.turn_count <= 3:  # Fase penempatan awal
                available_positions = [pos for pos in self.positions[:25]  # Hanya posisi 0-24
                                     if pos not in self.manusia_pieces 
                                     and pos not in self.macan_piece]
                if available_positions:
                    pos = random.choice(available_positions)
                    success = False
                    
                    if self.current_player == "Macan":
                        success = self.place_macan(pos)
                        if success:
                            self.current_player = "Manusia"
                            self.turn_count += 1
                    else:
                        success = self.place_manusia(pos)
                        if success:
                            self.current_player = "Macan"
                            self.turn_count += 1
                    
                    if success:
                        self.update_turn_label()
                        return
            else:  # Turn 4+
                from ai_logic import MacananAI
                ai = MacananAI(self)
                is_macan = self.player_choice == "Manusia"

                # Track jumlah maksimal pion manusia
                if len(self.manusia_pieces) > self._max_manusia_count:
                    self._max_manusia_count = len(self.manusia_pieces)
                if self._max_manusia_count >= 8:
                    self._reached_max_manusia = True

                # Jika manusia sudah pernah mencapai 8, harus bergerak
                if not is_macan and self._reached_max_manusia:
                    best_move = ai.get_movement_move(False)
                else:
                    best_move = ai.get_best_move(is_macan)

                if best_move:
                    from_pos, to_pos = best_move
                    success = False

                    # Jika AI adalah manusia dan belum pernah mencapai 8 pion
                    if from_pos is None and not is_macan and not self._reached_max_manusia:
                        success = self.place_manusia(to_pos)
                        if success:
                            self.current_player = "Macan"
                            self.turn_count += 1
                    # Jika AI adalah macan atau manusia yang sudah harus bergerak
                    else:
                        self.selected_piece = from_pos
                        success = self.move_piece(from_pos, to_pos)
                        if success:
                            self.current_player = "Manusia" if self.current_player == "Macan" else "Macan"
                            self.turn_count += 1
                    
                    if success:
                        self.update_turn_label()
                        return

            print("AI tidak dapat menemukan gerakan valid setelah beberapa percobaan")

    def can_player_move_piece(self, piece):
        """Cek apakah player bisa menggerakkan pion tersebut."""
        if self.mode == "PVP":
            # Dalam mode PVP, cek berdasarkan giliran saat ini
            if self.current_player == "Macan":
                return piece in self.macan_piece
            else:  # current_player == "Manusia"
                return piece in self.manusia_pieces
        else:
            # Mode AI: cek berdasarkan player_choice
            if self.player_choice == "Manusia":
                return piece in self.manusia_pieces and self.current_player == "Manusia"
            else:  # player_choice == "Macan"
                return piece in self.macan_piece and self.current_player == "Macan"

    def change_turn(self):
        """Ganti giliran pemain."""
        if self.current_player == "Macan":
            self.current_player = "Manusia"
        else:
            self.current_player = "Macan"
        self.update_turn_label()

