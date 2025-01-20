import random
from cache_manager import TranspositionTable

class MacananAI:
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.MAX_DEPTH = 3
        self.transposition_table = TranspositionTable()
        self.game_phase = "early"  # early, mid, late
        self.move_history = []

    def get_position_hash(self):
        """Generate hash unik untuk posisi saat ini."""
        macan_pos = str(sorted(self.game_logic.macan_piece))  # Sort untuk konsistensi
        manusia_pos = str(sorted(self.game_logic.manusia_pieces))
        return hash(macan_pos + manusia_pos)

    def update_game_phase(self):
        """Update fase permainan berdasarkan kondisi saat ini."""
        turn_count = self.game_logic.turn_count
        pieces_left = len(self.game_logic.manusia_pieces)
        
        if turn_count < 10:
            self.game_phase = "early"
        elif turn_count < 20 and pieces_left > 5:
            self.game_phase = "mid"
        else:
            self.game_phase = "late"

    def get_best_move(self, is_macan):
        """Mendapatkan gerakan terbaik."""
        # Fase penempatan awal (turn <= 3)
        if self.game_logic.turn_count <= 3:
            available_positions = [pos for pos in self.game_logic.positions 
                                 if pos not in self.game_logic.manusia_pieces 
                                 and pos not in self.game_logic.macan_piece]
            if available_positions:
                best_pos = self._get_strategic_placement(available_positions, is_macan)
                return (None, best_pos)
            return None

        # Fase pergerakan
        possible_moves = self.get_all_possible_moves(is_macan)
        if not possible_moves:
            return None

        # Jika manusia masih dalam fase penempatan
        if not is_macan and len(self.game_logic.manusia_pieces) < 8:
            best_pos = self._get_strategic_placement([move[1] for move in possible_moves], is_macan)
            return (None, best_pos)

        # Gunakan minimax untuk fase pergerakan
        best_score = float('-inf')
        best_move = None
        
        for move in possible_moves:
            old_state = self.save_game_state()
            self.make_move(move, is_macan)
            score = self.minimax(self.MAX_DEPTH - 1, False, is_macan, float('-inf'), float('inf'))
            self.restore_game_state(old_state)
            
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _get_strategic_placement(self, available_positions, is_macan):
        """Pilih posisi strategis untuk penempatan pion."""
        # Filter posisi yang hanya dalam kotak 5x5
        valid_positions = [pos for pos in available_positions 
                          if self.game_logic._is_valid_placement_position(pos)]
        
        if not valid_positions:  # Jika tidak ada posisi valid
            return None
        
        if is_macan:
            # Macan sebaiknya ditempatkan di posisi yang strategis
            # Prioritaskan posisi tengah
            center_positions = [pos for pos in valid_positions 
                              if 200 <= pos[0] <= 300 and 200 <= pos[1] <= 300]
            if center_positions:
                return random.choice(center_positions)
            
            # Atau posisi sudut dalam kotak 5x5
            corner_positions = [pos for pos in valid_positions
                              if (pos[0] in [150, 350] and pos[1] in [150, 350])]
            if corner_positions:
                return random.choice(corner_positions)
        else:
            # Manusia sebaiknya ditempatkan untuk membentuk formasi
            if self.game_logic.manusia_pieces:
                existing_pos = self.game_logic.manusia_pieces[0]
                nearby_positions = [pos for pos in valid_positions
                                  if 50 <= self._manhattan_distance(pos, existing_pos) <= 100]
                if nearby_positions:
                    return random.choice(nearby_positions)
        
        # Jika tidak ada posisi strategis yang valid, pilih random dari posisi valid
        return random.choice(valid_positions)

    def evaluate_position(self, is_macan):
        """Evaluasi posisi dengan mempertimbangkan fase permainan."""
        if is_macan:
            return self._evaluate_macan()
        else:
            return self._evaluate_manusia()

    def _evaluate_macan(self):
        """Evaluasi strategi macan berdasarkan fase permainan."""
        score = 0
        
        # Kondisi menang/kalah
        if len(self.game_logic.manusia_pieces) <= 3:
            return float('inf')  # Macan menang
        if self.game_logic.is_macan_trapped():
            return float('-inf')  # Macan kalah
        
        # Evaluasi berdasarkan fase permainan
        if self.game_phase == "early":
            # Fokus pada kontrol pusat dan mobilitas
            for macan in self.game_logic.macan_piece:
                center_control = self._evaluate_center_control(macan)
                mobility = len(self.game_logic.get_valid_moveable_positions(macan))
                score += (center_control * 40) + (mobility * 15)
                
        elif self.game_phase == "mid":
            # Fokus pada memakan pion manusia
            potential_victims = self._count_potential_victims()
            score += (potential_victims * 60)
            
        else:  # late game
            # Fokus pada menang
            if len(self.game_logic.manusia_pieces) <= 4:
                score += 500
        
        # Tambahan evaluasi umum
        score += 100 - (len(self.game_logic.manusia_pieces) * 10)  # Semakin sedikit manusia semakin bagus
        
        return score

    def _evaluate_manusia(self):
        """Evaluasi strategi manusia berdasarkan fase permainan."""
        score = 0
        
        # Kondisi menang/kalah
        if self.game_logic.is_macan_trapped():
            return float('inf')  # Manusia menang
        if len(self.game_logic.manusia_pieces) <= 3:
            return float('-inf')  # Manusia kalah
        
        # Evaluasi berdasarkan fase permainan
        if self.game_phase == "early":
            # Fokus pada formasi yang kuat
            formation_score = self._evaluate_manusia_formation()
            score += formation_score * 30
            
        elif self.game_phase == "mid":
            # Fokus pada pengepungan
            surrounding_score = self._evaluate_surrounding_macan()
            score += surrounding_score * 50
            
        else:  # late game
            # Fokus pada bertahan
            if len(self.game_logic.manusia_pieces) >= 6:
                score += 300
        
        # Tambahan evaluasi umum
        score += len(self.game_logic.manusia_pieces) * 50  # Semakin banyak manusia semakin bagus
        
        # Evaluasi jarak aman dari semua macan
        safe_distance_score = 0
        for piece in self.game_logic.manusia_pieces:
            for macan in self.game_logic.macan_piece:
                dist = self._manhattan_distance(piece, macan)
                if dist < 2:  # Terlalu dekat dengan macan
                    safe_distance_score -= 30
                elif 2 <= dist <= 3:  # Jarak ideal untuk pengepungan
                    safe_distance_score += 20
                else:  # Terlalu jauh untuk pengepungan efektif
                    safe_distance_score -= 10
        score += safe_distance_score
        
        return score

    def _evaluate_center_control(self, pos):
        """Evaluasi kontrol pusat papan."""
        center_x, center_y = 250, 250  # Sesuaikan dengan ukuran papan
        distance_to_center = self._manhattan_distance(pos, (center_x, center_y))
        return max(0, 100 - distance_to_center) / 100

    def _evaluate_manusia_formation(self):
        """Evaluasi kekuatan formasi pion manusia."""
        formation_score = 0
        manusia_pieces = self.game_logic.manusia_pieces
        
        # Hitung jarak antar pion manusia
        for i, piece1 in enumerate(manusia_pieces):
            connected_pieces = 0
            for j, piece2 in enumerate(manusia_pieces):
                if i != j:
                    dist = self._manhattan_distance(piece1, piece2)
                    if dist <= 50:  # Pion terhubung
                        connected_pieces += 1
            formation_score += connected_pieces
        
        return formation_score

    def _evaluate_surrounding_macan(self):
        """Evaluasi seberapa baik pion manusia mengepung macan."""
        surrounding_score = 0
        
        for macan_pos in self.game_logic.macan_piece:
            # Cek pion manusia di sekitar macan
            for piece in self.game_logic.manusia_pieces:
                dist = self._manhattan_distance(piece, macan_pos)
                if dist <= 50:  # Dalam jarak pengepungan
                    surrounding_score += 1
                    
                # Bonus untuk posisi strategis
                if self._is_strategic_position(piece, macan_pos):
                    surrounding_score += 2
                    
        return surrounding_score

    def _count_potential_victims(self):
        """Hitung jumlah pion manusia yang berpotensi dimakan."""
        count = 0
        for macan in self.game_logic.macan_piece:
            for piece in self.game_logic.manusia_pieces:
                if self._can_eat_piece(macan, piece):
                    count += 1
        return count

    def analyze_last_moves(self, num_moves=5):
        """Analisis gerakan terakhir untuk pembelajaran."""
        if len(self.move_history) < num_moves:
            return
            
        recent_moves = self.move_history[-num_moves:]
        phase_stats = {"early": 0, "mid": 0, "late": 0}
        
        for move, phase in recent_moves:
            phase_stats[phase] += 1
            
        # Sesuaikan MAX_DEPTH berdasarkan fase yang paling sering
        most_common_phase = max(phase_stats, key=phase_stats.get)
        if most_common_phase == "late":
            self.MAX_DEPTH = 4  # Tingkatkan kedalaman di late game
        else:
            self.MAX_DEPTH = 3 

    def get_sorted_moves(self, is_macan):
        """Dapatkan dan urutkan gerakan berdasarkan potensi."""
        moves = self.get_all_possible_moves(is_macan)
        
        # Evaluasi cepat untuk setiap gerakan
        move_scores = []
        for move in moves:
            score = self._quick_evaluate_move(move, is_macan)
            move_scores.append((score, move))
        
        # Urutkan gerakan berdasarkan skor
        move_scores.sort(reverse=True)
        return [move for score, move in move_scores]

    def _quick_evaluate_move(self, move, is_macan):
        """Evaluasi cepat untuk satu gerakan."""
        from_pos, to_pos = move
        score = 0
        
        if is_macan:
            # Prioritaskan gerakan makan
            for piece in self.game_logic.manusia_pieces:
                if self._can_eat_piece(from_pos, piece):
                    score += 1000
            # Prioritaskan gerakan ke pusat
            score -= self._manhattan_distance(to_pos, (250, 250)) * 0.1
        else:
            # Untuk manusia, prioritaskan gerakan yang menjauh dari semua macan
            for macan in self.game_logic.macan_piece:  # Iterasi semua macan
                dist = self._manhattan_distance(to_pos, macan)
                score += dist * 0.5 if dist > 2 else -dist
        
        return score

    def minimax(self, depth, is_maximizing, is_macan, alpha, beta):
        """Implementasi algoritma minimax dengan alpha-beta pruning."""
        if depth == 0 or self.game_logic.game_over:
            return self.evaluate_position(is_macan)

        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_sorted_moves(is_macan)[:5]:
                old_state = self.save_game_state()
                self.make_move(move, is_macan)
                eval = self.minimax(depth - 1, False, is_macan, alpha, beta)
                self.restore_game_state(old_state)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_sorted_moves(not is_macan)[:5]:
                old_state = self.save_game_state()
                self.make_move(move, not is_macan)
                eval = self.minimax(depth - 1, True, is_macan, alpha, beta)
                self.restore_game_state(old_state)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_all_possible_moves(self, is_macan):
        """Dapatkan semua gerakan yang mungkin."""
        moves = []
        
        # Fase penempatan (turn <= 3)
        if self.game_logic.turn_count <= 3:
            # Hanya gunakan posisi dalam kotak 5x5 (indeks 0-24)
            available_positions = [pos for pos in self.game_logic.positions[:25]
                                 if pos not in self.game_logic.manusia_pieces 
                                 and pos not in self.game_logic.macan_piece]
            return [(None, pos) for pos in available_positions]
        
        # Fase pergerakan
        if is_macan:
            for piece in self.game_logic.macan_piece:
                valid_moves = self.game_logic.get_valid_moveable_positions(piece)
                moves.extend([(piece, move[0]) for move in valid_moves])
        else:
            if len(self.game_logic.manusia_pieces) < 8:
                # Manusia masih dalam fase penempatan, hanya dalam kotak 5x5
                for pos in self.game_logic.positions[:25]:  # Hanya posisi 0-24
                    if (pos not in self.game_logic.manusia_pieces and 
                        pos not in self.game_logic.macan_piece):
                        moves.append((None, pos))
            else:
                # Manusia sudah bisa bergerak
                for piece in self.game_logic.manusia_pieces:
                    valid_moves = self.game_logic.get_valid_moveable_positions(piece)
                    moves.extend([(piece, move[0]) for move in valid_moves])
        
        return moves

    def _manhattan_distance(self, pos1, pos2):
        """Hitung jarak Manhattan antara dua posisi."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _can_eat_piece(self, macan_pos, manusia_pos):
        """Cek apakah macan bisa memakan pion manusia."""
        valid_moves = self.game_logic.get_valid_moveable_positions(macan_pos)
        for move in valid_moves:
            if move[1] == manusia_pos:  # move[1] adalah pion yang dimakan
                return True
        return False

    def save_game_state(self):
        """Simpan state game saat ini."""
        return {
            'manusia_pieces': self.game_logic.manusia_pieces.copy(),
            'macan_piece': self.game_logic.macan_piece.copy(),  # Gunakan copy() untuk list
            'game_over': self.game_logic.game_over,
            'winner': self.game_logic.winner
        }

    def restore_game_state(self, state):
        """Kembalikan state game ke kondisi sebelumnya."""
        self.game_logic.manusia_pieces = state['manusia_pieces'].copy()
        self.game_logic.macan_piece = state['macan_piece'].copy()  # Gunakan copy() untuk list
        self.game_logic.game_over = state['game_over']
        self.game_logic.winner = state['winner']

    def make_move(self, move, is_macan):
        """Buat gerakan untuk simulasi."""
        from_pos, to_pos = move
        
        # Fase penempatan (from_pos adalah None)
        if from_pos is None:
            if is_macan:
                self.game_logic.macan_piece.append(to_pos)
            else:
                self.game_logic.manusia_pieces.append(to_pos)
            return

        # Fase pergerakan
        if is_macan:
            # Update posisi macan yang dipindahkan
            macan_index = self.game_logic.macan_piece.index(from_pos)
            self.game_logic.macan_piece[macan_index] = to_pos
            
            # Cek apakah ada manusia yang dimakan
            dx = (to_pos[0] - from_pos[0]) // 2
            dy = (to_pos[1] - from_pos[1]) // 2
            eaten_pos = (from_pos[0] + dx, from_pos[1] + dy)
            
            if eaten_pos in self.game_logic.manusia_pieces:
                self.game_logic.manusia_pieces.remove(eaten_pos)
        else:
            if from_pos in self.game_logic.manusia_pieces:  # Pastikan pion ada sebelum dihapus
                self.game_logic.manusia_pieces.remove(from_pos)
                self.game_logic.manusia_pieces.append(to_pos)

    def _is_strategic_position(self, manusia_pos, macan_pos):
        """Cek apakah posisi pion manusia strategis untuk pengepungan."""
        # Hitung jarak dan arah relatif ke macan
        dx = abs(manusia_pos[0] - macan_pos[0])
        dy = abs(manusia_pos[1] - macan_pos[1])
        
        # Posisi strategis adalah:
        # 1. Berada dalam jarak pengepungan ideal (2 langkah)
        # 2. Membentuk formasi pengepungan dengan pion lain
        # 3. Mengontrol jalur pelarian macan
        
        # Cek jarak pengepungan ideal
        if dx == 2 or dy == 2:
            # Cek apakah ada pion lain yang mendukung pengepungan
            for piece in self.game_logic.manusia_pieces:
                if piece != manusia_pos:
                    other_dx = abs(piece[0] - macan_pos[0])
                    other_dy = abs(piece[1] - macan_pos[1])
                    
                    # Pion lain juga dalam posisi pengepungan
                    if (other_dx == 2 or other_dy == 2):
                        # Pion berada di sisi berlawanan
                        if (dx * other_dx == 0 and dy * other_dy == 0):
                            return True
                        # Pion membentuk sudut pengepungan
                        if (dx != other_dx or dy != other_dy):
                            return True
        
        # Cek posisi blocking jalur pelarian
        elif dx == 1 or dy == 1:
            # Hitung jumlah pion yang menghalangi jalur pelarian
            blocking_pieces = 0
            for piece in self.game_logic.manusia_pieces:
                if piece != manusia_pos:
                    if abs(piece[0] - macan_pos[0]) <= 2 and abs(piece[1] - macan_pos[1]) <= 2:
                        blocking_pieces += 1
            
            # Posisi strategis jika ada cukup pion pendukung
            if blocking_pieces >= 2:
                return True
        
        # Cek kontrol area penting
        center_x, center_y = 250, 250  # Pusat papan
        if self._manhattan_distance(manusia_pos, (center_x, center_y)) <= 100:
            nearby_pieces = 0
            for piece in self.game_logic.manusia_pieces:
                if piece != manusia_pos:
                    if self._manhattan_distance(piece, manusia_pos) <= 50:
                        nearby_pieces += 1
            
            # Posisi strategis jika mengontrol area penting dengan dukungan
            if nearby_pieces >= 2:
                return True
        
        return False 

    def get_movement_move(self, is_macan):
        """Mendapatkan gerakan untuk fase pergerakan saja."""
        possible_moves = []
        if is_macan:
            for piece in self.game_logic.macan_piece:
                valid_moves = self.game_logic.get_valid_moveable_positions(piece)
                possible_moves.extend([(piece, move[0]) for move in valid_moves])
        else:
            for piece in self.game_logic.manusia_pieces:
                valid_moves = self.game_logic.get_valid_moveable_positions(piece)
                possible_moves.extend([(piece, move[0]) for move in valid_moves])

        if not possible_moves:
            return None

        # Pilih gerakan terbaik menggunakan minimax
        best_score = float('-inf')
        best_move = None
        for move in possible_moves:
            old_state = self.save_game_state()
            self.make_move(move, is_macan)
            score = self.minimax(self.MAX_DEPTH - 1, False, is_macan, float('-inf'), float('inf'))
            self.restore_game_state(old_state)
            
            if score > best_score:
                best_score = score
                best_move = move

        return best_move 

    def get_valid_moveable_positions(self, node):
        """Mendapatkan semua posisi valid yang bisa dituju."""
        if not node or node not in self.positions:
            return []
        
        valid_moves = []
        connected_nodes = []
        node_index = self.positions.index(node)
        
        # Jika node berada di grid 5x5 (indeks 0-24)
        if node_index < 25:
            row = node_index // 5
            col = node_index % 5
            
            # Cek orthogonal di grid
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_row, new_col = row + dx, col + dy
                if 0 <= new_row < 5 and 0 <= new_col < 5:
                    new_index = new_row * 5 + new_col
                    connected_nodes.append(self.positions[new_index])
            
            # Cek diagonal jika ada
            if self._has_diagonal_lines(row, col):
                for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_row, new_col = row + dx, col + dy
                    if 0 <= new_row < 5 and 0 <= new_col < 5:
                        new_index = new_row * 5 + new_col
                        connected_nodes.append(self.positions[new_index])
            
            # Tambahkan koneksi ke segitiga hanya dari titik tengah
            if col == 0 and row == 2:  # Titik tengah kolom kiri (index 10)
                # Koneksi ke segitiga kiri
                for triangle_node in self.positions[25:31]:
                    dx = triangle_node[0] - node[0]
                    dy = triangle_node[1] - node[1]
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance <= 100:  # Threshold jarak koneksi
                        connected_nodes.append(triangle_node)
            
            elif col == 4 and row == 2:  # Titik tengah kolom kanan (index 14)
                # Koneksi ke segitiga kanan
                for triangle_node in self.positions[31:]:
                    dx = triangle_node[0] - node[0]
                    dy = triangle_node[1] - node[1]
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance <= 100:  # Threshold jarak koneksi
                        connected_nodes.append(triangle_node)
        
        # Jika node berada di area segitiga (indeks 25+)
        else:
            # Koneksi dalam segitiga yang sama
            if node_index < 31:  # Segitiga kiri
                # Koneksi ke node segitiga lain di kiri
                for triangle_node in self.positions[25:31]:
                    if triangle_node != node:
                        dx = triangle_node[0] - node[0]
                        dy = triangle_node[1] - node[1]
                        distance = (dx ** 2 + dy ** 2) ** 0.5
                        if distance <= 100:
                            connected_nodes.append(triangle_node)
                
                # Koneksi hanya ke titik tengah grid (index 10)
                grid_node = self.positions[10]  # Titik tengah kolom kiri
                dx = grid_node[0] - node[0]
                dy = grid_node[1] - node[1]
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance <= 100:
                    connected_nodes.append(grid_node)
            
            else:  # Segitiga kanan
                # Koneksi ke node segitiga lain di kanan
                for triangle_node in self.positions[31:]:
                    if triangle_node != node:
                        dx = triangle_node[0] - node[0]
                        dy = triangle_node[1] - node[1]
                        distance = (dx ** 2 + dy ** 2) ** 0.5
                        if distance <= 100:
                            connected_nodes.append(triangle_node)
                
                # Koneksi hanya ke titik tengah grid (index 14)
                grid_node = self.positions[14]  # Titik tengah kolom kanan
                dx = grid_node[0] - node[0]
                dy = grid_node[1] - node[1]
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance <= 100:
                    connected_nodes.append(grid_node)
        
        # Filter gerakan valid berdasarkan aturan permainan
        for target_node in connected_nodes:
            if target_node not in self.macan_piece:  # Tidak bisa ke posisi macan lain
                if node in self.macan_piece:  # Logika untuk Macan
                    if target_node not in self.manusia_pieces:
                        valid_moves.append((target_node, None))
                    else:  # Cek lompatan untuk makan
                        dx = target_node[0] - node[0]
                        dy = target_node[1] - node[1]
                        jump_x = target_node[0] + dx
                        jump_y = target_node[1] + dy
                        
                        # Cari node untuk lompatan
                        for jump_node in self.positions:
                            if (abs(jump_node[0] - jump_x) < 20 and 
                                abs(jump_node[1] - jump_y) < 20 and
                                jump_node not in self.manusia_pieces and
                                jump_node not in self.macan_piece):
                                valid_moves.append((jump_node, target_node))
                
                else:  # Logika untuk Manusia
                    if target_node not in self.manusia_pieces:
                        valid_moves.append((target_node, None))
        
        return valid_moves 