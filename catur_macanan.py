import tkinter as tk
from tkinter import messagebox
from draw_board import draw_board
from game_logic import GameLogic

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

def start_game(root,choice):
    """Mulai permainan berdasarkan pilihan (Manusia atau Macan)."""
    # Buat jendela baru untuk permainan
    game_window = tk.Toplevel()
    game_window.title("Papan Macanan")
    canvas_width = 820
    canvas_height = 600

    # Buat canvas untuk papan permainan
    canvas = tk.Canvas(game_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    # Atur posisi jendela di tengah layar
    center_window(game_window, canvas_width, canvas_height)

    # Gambar papan
    positions = draw_board(canvas, 400, 200)  # Ukuran papan dan padding

    # Inisialisasi logika permainan
    game_logic = GameLogic(canvas, positions)

    # Menambahkan label untuk menunjukkan siapa yang sedang bermain
    current_player = choice
    turn_label = tk.Label(game_window, text=f"{current_player}'s Turn", font=("Helvetica", 16))
    turn_label.pack(pady=10)

    # Memperbarui giliran
    update_turn_label(turn_label, current_player)


    # Fungsi untuk memperbarui giliran setelah setiap langkah
    
    # Menambahkan fungsi untuk mengganti giliran
    game_logic.change_turn(current_player)
    print(current_player)


    # Mulai permainan
    game_window.transient(root)
    game_window.grab_set()
    root.wait_window(game_window)
    
    print(game_window)

def show_start_screen():
    """Menampilkan tampilan awal (pilihan antara Manusia atau Macan)."""
    root = tk.Tk()
    root.title("Papan Macanan - Start Game")

    # Ukuran jendela tampilan awal
    canvas_width = 400
    canvas_height = 300

    # Atur posisi jendela di tengah layar
    center_window(root, canvas_width, canvas_height)

    # Label untuk judul
    title_label = tk.Label(root, text="Pilih Karakter Anda", font=("Helvetica", 20))
    title_label.pack(pady=50)

    # Tombol untuk memilih manusia
    button_manusia = tk.Button(root, text="Menjadi Manusia", width=20, height=2,
                               command=lambda: start_game(root,"You"))
    button_manusia.pack(pady=10)

    # Tombol untuk memilih macan
    button_macan = tk.Button(root, text="Menjadi Macan", width=20, height=2,
                             command=lambda: start_game(root,"AI"))
    button_macan.pack(pady=10)

    # Jalankan tampilan awal
    
    root.mainloop()

# Menjalankan tampilan awal ketika file ini dijalankan
if __name__ == "__main__":
    show_start_screen()
