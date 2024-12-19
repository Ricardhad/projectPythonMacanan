import tkinter as tk

def center_window(root, canvas_width, canvas_height):
    """Posisikan jendela Tkinter di tengah layar."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (canvas_width // 2)
    y = (screen_height // 2) - (canvas_height // 2)
    root.geometry(f"{canvas_width}x{canvas_height}+{x}+{y}")

def draw_board(canvas, size, padding):
    """Menggambar papan macanan dengan garis diagonal bergantian dan segitiga di kiri & kanan."""
    gap = size // 5  # Ukuran jarak antar titik
    node_radius = 5  # Radius untuk titik-titik

    # Menggambar kotak tengah (5x5 grid) dengan garis diagonal bergantian
    for row in range(5):
        for col in range(5):
            x = col * gap + padding
            y = row * gap + padding

            # Titik
            canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill="black"
            )

            # Garis horizontal dan vertikal
            if col < 4:  # Horizontal
                canvas.create_line(x, y, x + gap, y, fill="black")
            if row < 4:  # Vertikal
                canvas.create_line(x, y, x, y + gap, fill="black")

            # Garis diagonal bergantian
            if col < 4 and row < 4:
                if (row + col) % 2 == 0:
                    canvas.create_line(x, y, x + gap, y + gap, fill="black")  # Diagonal \
                else:
                    canvas.create_line(x + gap, y, x, y + gap, fill="black")  # Diagonal /

    # Segitiga kiri
    left_center_x = padding
    left_center_y = padding + 2 * gap
    triangle_width = 2 * gap

    # Garis segitiga
    canvas.create_line(left_center_x, left_center_y, left_center_x - triangle_width, left_center_y - gap, fill="black")
    canvas.create_line(left_center_x, left_center_y, left_center_x - triangle_width, left_center_y + gap, fill="black")
    canvas.create_line(left_center_x - triangle_width, left_center_y - gap, left_center_x - triangle_width, left_center_y + gap, fill="black")

    # Garis silang di segitiga kiri
    canvas.create_line(left_center_x - gap, left_center_y - gap/2, left_center_x - gap, left_center_y + gap/2, fill="black")
    canvas.create_line(left_center_x - triangle_width, left_center_y, left_center_x, left_center_y, fill="black")

    # Titik segitiga kiri
    left_nodes = [
        (left_center_x - triangle_width, left_center_y - gap), #node 1 kiri atas
        (left_center_x - triangle_width, left_center_y), #node 2 tengah belakang
        (left_center_x - triangle_width, left_center_y + gap),  #node 3 kiri bawah
        (left_center_x - gap, left_center_y - gap/2),  #node 4  kanan atas
        (left_center_x - gap, left_center_y),  #node 5 kanan tengah
        (left_center_x - gap, left_center_y + gap/2),  #node 6 kanan bawah
    ]

    print(left_nodes)
    for x, y in left_nodes:
        canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill="black"
        )

    # Segitiga kanan
    right_center_x = padding + 4 * gap
    right_center_y = padding + 2 * gap

    print(gap)

    # Garis segitiga
    canvas.create_line(right_center_x, right_center_y, right_center_x + triangle_width, right_center_y - gap, fill="black")
    canvas.create_line(right_center_x, right_center_y, right_center_x + triangle_width, right_center_y + gap, fill="black")
    canvas.create_line(right_center_x + triangle_width, right_center_y - gap, right_center_x + triangle_width, right_center_y + gap, fill="black")

    # Garis silang di segitiga kanan
    canvas.create_line(right_center_x + gap, right_center_y - gap/2, right_center_x + gap, right_center_y + gap/2, fill="black")
    canvas.create_line(right_center_x, right_center_y, right_center_x + triangle_width, right_center_y, fill="black")

    # Titik segitiga kanan
   
    right_nodes = [
        (right_center_x + triangle_width, right_center_y - gap),
        (right_center_x + triangle_width, right_center_y),
        (right_center_x + triangle_width, right_center_y + gap),
        (right_center_x + gap, right_center_y - gap/2),
        (right_center_x + gap, right_center_y),
        (right_center_x + gap, right_center_y + gap/2),
    ]

    for x, y in right_nodes:
        canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill="black"
        )

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
