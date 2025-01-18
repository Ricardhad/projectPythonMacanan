import tkinter as tk
from tkinter import messagebox
from draw_board import draw_board
from game_logic import GameLogic
import random

def center_window(root, canvas_width, canvas_height):
    """Posisikan jendela Tkinter di tengah layar."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (canvas_width // 2)
    y = (screen_height // 2) - (canvas_height // 2)
    root.geometry(f"{canvas_width}x{canvas_height}+{x}+{y}")

def update_turn_label(turn_label, current_player):
    """Memperbarui label giliran yang menunjukkan pemain mana yang sedang bermain."""
    if current_player == "You":
        turn_label.config(text="Your Turn", fg="blue")
    else:
        turn_label.config(text="AI's Turn", fg="red")

def start_game(root, player_choice, mode, pvp_roles=None):
    """Mulai permainan berdasarkan pilihan."""
    game_window = tk.Toplevel()
    game_window.title("Papan Macanan")
    canvas_width = 820
    canvas_height = 600

    canvas = tk.Canvas(game_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    center_window(game_window, canvas_width, canvas_height)
    positions = draw_board(canvas, 400, 200)
    
    # Inisialisasi logika permainan
    game_logic = GameLogic(canvas, positions, player_choice, mode, pvp_roles)

    game_window.transient(root)
    game_window.grab_set()
    root.wait_window(game_window)

def roll_dice():
    """Return angka random 1-6."""
    return random.randint(1, 6)

def show_role_selection(root, mode):
    """Tampilkan window untuk pemilihan role dengan roll dice."""
    role_window = tk.Toplevel()
    role_window.title("Role Selection")
    
    # Set ukuran window
    window_width = 400
    window_height = 300
    center_window(role_window, window_width, window_height)
    
    # Label judul
    title_label = tk.Label(role_window, text="Roll Dice untuk Menentukan Role", 
                          font=("Helvetica", 16, "bold"))
    title_label.pack(pady=20)
    
    # Frame untuk hasil roll
    result_frame = tk.Frame(role_window)
    result_frame.pack(pady=10)
    
    # Labels untuk player
    player1_label = tk.Label(result_frame, text="Player 1: -", font=("Helvetica", 12))
    player1_label.grid(row=0, column=0, padx=20)
    
    player2_label = tk.Label(result_frame, text="Player 2: -", font=("Helvetica", 12))
    player2_label.grid(row=0, column=1, padx=20)
    
    # Variable untuk menyimpan hasil roll
    player1_roll = [0]
    player2_roll = [0]
    current_player = [1]
    
    def handle_roll():
        result = roll_dice()
        if current_player[0] == 1:
            player1_roll[0] = result
            player1_label.config(text=f"Player 1: {result}")
            current_player[0] = 2
            roll_button.config(text="Player 2 Roll")
        else:
            player2_roll[0] = result
            player2_label.config(text=f"Player 2: {result}")
            roll_button.config(state="disabled")
            
            # Tentukan winner setelah kedua player roll
            if player1_roll[0] > player2_roll[0]:
                result_label.config(text="Player 1 menjadi Macan!")
                start_button.config(state="normal")
                roles[0] = ("Player 1: Macan", "Player 2: Manusia")
            elif player2_roll[0] > player1_roll[0]:
                result_label.config(text="Player 2 menjadi Macan!")
                start_button.config(state="normal")
                roles[0] = ("Player 2: Macan", "Player 1: Manusia")
            else:
                result_label.config(text="Seri! Roll lagi!")
                current_player[0] = 1
                roll_button.config(state="normal", text="Player 1 Roll")
                player1_label.config(text="Player 1: -")
                player2_label.config(text="Player 2: -")
    
    # Button untuk roll
    roll_button = tk.Button(role_window, text="Player 1 Roll", 
                           command=handle_roll, width=20)
    roll_button.pack(pady=10)
    
    # Label untuk hasil
    result_label = tk.Label(role_window, text="", font=("Helvetica", 14))
    result_label.pack(pady=10)
    
    # Menyimpan role yang terpilih
    roles = [("", "")]
    
    def start_pvp_game():
        role_window.destroy()
        start_game(root, "PVP", "PVP", roles[0])
    
    # Button untuk memulai game (awalnya disabled)
    start_button = tk.Button(role_window, text="Mulai Game", 
                            command=start_pvp_game, state="disabled", width=20)
    start_button.pack(pady=20)
    
    role_window.transient(root)
    role_window.grab_set()
    root.wait_window(role_window)

def show_start_screen():
    """Menampilkan tampilan awal."""
    root = tk.Tk()
    root.title("Papan Macanan - Start Game")

    canvas_width = 400
    canvas_height = 400  # Perbesar sedikit untuk tombol tambahan

    center_window(root, canvas_width, canvas_height)

    title_label = tk.Label(root, text="Pilih Mode Permainan", font=("Helvetica", 20))
    title_label.pack(pady=30)

    # Mode melawan AI
    ai_label = tk.Label(root, text="Mode vs AI:", font=("Helvetica", 14))
    ai_label.pack(pady=10)

    button_manusia = tk.Button(root, text="Menjadi Manusia", width=20, height=2,
                              command=lambda: start_game(root, "Manusia", "AI"))
    button_manusia.pack(pady=5)

    button_macan = tk.Button(root, text="Menjadi Macan", width=20, height=2,
                             command=lambda: start_game(root, "Macan", "AI"))
    button_macan.pack(pady=5)

    # Mode Player vs Player
    pvp_label = tk.Label(root, text="Mode vs Player:", font=("Helvetica", 14))
    pvp_label.pack(pady=10)

    button_pvp = tk.Button(root, text="Player vs Player", width=20, height=2,
                          command=lambda: show_role_selection(root, "PVP"))
    button_pvp.pack(pady=5)

    root.mainloop()

# Menjalankan tampilan awal ketika file ini dijalankan
if __name__ == "__main__":
    show_start_screen()
