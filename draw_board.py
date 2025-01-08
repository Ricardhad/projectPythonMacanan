import tkinter as tk

def draw_board(canvas, size, padding):
    """Menggambar papan macanan dengan garis diagonal bergantian dan segitiga di kiri & kanan."""
    gap = size // 5  # Ukuran jarak antar titik
    node_radius = 8  # Radius untuk titik-titik

    nodes_pos = []
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

            nodes_pos.append((x, y))
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
        (left_center_x - triangle_width, left_center_y - gap),
        (left_center_x - triangle_width, left_center_y),
        (left_center_x - triangle_width, left_center_y + gap),
        (left_center_x - gap, left_center_y - gap/2),
        (left_center_x - gap, left_center_y),
        (left_center_x - gap, left_center_y + gap/2),
    ]

    for x, y in left_nodes:
        canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill="black"
        )

    nodes_pos.extend(left_nodes)

    # Segitiga kanan
    right_center_x = padding + 4 * gap
    right_center_y = padding + 2 * gap

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

    nodes_pos.extend(right_nodes)

    return nodes_pos  # Mengembalikan posisi semua titik

# # Contoh penggunaan
# root = tk.Tk()
# canvas_size = 400
# padding = 50
# canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
# canvas.pack()

# positions = draw_board(canvas, canvas_size - 2 * padding, padding)
# print("Posisi semua titik:", positions)

# root.mainloop()
