import tkinter as tk
from draw_board import draw_board

def center_window(root, canvas_width, canvas_height):
    """Posisikan jendela Tkinter di tengah layar."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (canvas_width // 2)
    y = (screen_height // 2) - (canvas_height // 2)
    root.geometry(f"{canvas_width}x{canvas_height}+{x}+{y}")

def main():
    # Inisialisasi Tkinter
    root = tk.Tk()
    root.title("Papan Macanan")

    # Ukuran canvas
    canvas_width = 800
    canvas_height = 600

    # Buat canvas
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    # Atur posisi jendela di tengah layar
    center_window(root, canvas_width, canvas_height)

    # Gambar papan macanan
    draw_board(canvas, 400, 200)  # Ukuran papan dan padding

    # Jalankan aplikasi
    root.mainloop()

if __name__ == "__main__":
    main()
