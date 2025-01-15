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
        macan_pos = str(self.game_logic.macan_piece)
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
        """Mendapatkan gerakan terbaik dengan variasi strategi."""
        self.update_game_phase()
        
        # Occasionally make random moves for unpredictability (10% chance)
        if random.random() < 0.1:
            possible_moves = self.get_all_possible_moves(is_macan)
            if possible_moves:
                return random.choice(possible_moves)

        position_hash = self.get_position_hash()
        cached = self.transposition_table.lookup(position_hash)
        
        if cached and cached[0] >= self.MAX_DEPTH:
            return cached[2]  # Return cached move

        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        possible_moves = self.get_sorted_moves(is_macan)
        
        for move in possible_moves:
            old_state = self.save_game_state()
            self.make_move(move, is_macan)
            
            score = self.minimax(self.MAX_DEPTH - 1, False, is_macan, alpha, beta)
            
            self.restore_game_state(old_state)
            
            if score > best_score:
                best_score = score
                best_move = move
                alpha = max(alpha, score)

        # Cache the result
        self.transposition_table.store(position_hash, self.MAX_DEPTH, best_score, best_move)
        self.move_history.append((best_move, self.game_phase))
        
        return best_move

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
            if self.game_logic.macan_piece:
                center_control = self._evaluate_center_control(self.game_logic.macan_piece)
                mobility = len(self.game_logic.get_valid_moveable_positions(self.game_logic.macan_piece))
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
            # Fokus pada formasi yang kuat dan posisi defensif
            formation_score = self._evaluate_manusia_formation()
            mobility_score = self._evaluate_manusia_mobility()
            score += formation_score * 40 + mobility_score * 20

        elif self.game_phase == "mid":
            # Fokus pada mengepung macan dan melindungi pion penting
            surrounding_score = self._evaluate_surrounding_macan()
            defense_score = self._evaluate_defensive_positions()
            score += surrounding_score * 50 + defense_score * 30

        else:  # late game
            # Fokus pada bertahan dan mencegah macan memakan pion
            if len(self.game_logic.manusia_pieces) >= 6:
                score += 300
            escape_routes = self._evaluate_escape_routes()
            score += escape_routes * 20

        # Tambahan evaluasi umum untuk pion yang tersisa
        score += len(self.game_logic.manusia_pieces) * 10

        return score
    
    def _evaluate_manusia_mobility(self):
        """Evaluasi mobilitas pion manusia untuk memastikan mereka memiliki opsi gerakan."""
        mobility = 0
        for piece in self.game_logic.manusia_pieces:
            mobility += len(self.game_logic.get_valid_moveable_positions(piece))
        return mobility

    def _evaluate_defensive_positions(self):
        """Evaluasi seberapa baik pion manusia berada dalam posisi defensif terhadap macan."""
        score = 0
        macan_pos = self.game_logic.macan_piece
        for piece in self.game_logic.manusia_pieces:
            if self.game_logic.is_piece_protected(piece):
                score += 1
            if self.game_logic.is_near_macan(piece, macan_pos):
                score -= 2
        return score

    def _evaluate_escape_routes(self):
        """Evaluasi opsi jalur melarikan diri untuk pion manusia."""
        escape_score = 0
        for piece in self.game_logic.manusia_pieces:
            if self.game_logic.has_escape_route(piece):
                escape_score += 1
        return escape_score


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
        if not self.game_logic.macan_piece:
            return 0
        
        surrounding_score = 0
        macan_pos = self.game_logic.macan_piece
        
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
        if self.game_logic.macan_piece:
            for piece in self.game_logic.manusia_pieces:
                if self._can_eat_piece(self.game_logic.macan_piece, piece):
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
            # Untuk manusia, prioritaskan gerakan yang menjauh dari macan
            if self.game_logic.macan_piece:
                dist = self._manhattan_distance(to_pos, self.game_logic.macan_piece)
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
        if is_macan:
            piece = self.game_logic.macan_piece
            if piece:
                valid_moves = self.game_logic.get_valid_moveable_positions(piece)
                moves.extend([(piece, move[0]) for move in valid_moves])
        else:
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
            'macan_piece': self.game_logic.macan_piece,
            'game_over': self.game_logic.game_over,
            'winner': self.game_logic.winner
        }

    def restore_game_state(self, state):
        """Kembalikan state game ke kondisi sebelumnya."""
        self.game_logic.manusia_pieces = state['manusia_pieces'].copy()
        self.game_logic.macan_piece = state['macan_piece']
        self.game_logic.game_over = state['game_over']
        self.game_logic.winner = state['winner']

    def make_move(self, move, is_macan):
        """Buat gerakan untuk simulasi."""
        from_pos, to_pos = move
        if is_macan:
            self.game_logic.macan_piece = to_pos
        else:
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