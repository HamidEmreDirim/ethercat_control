import customtkinter as ctk
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt  # opsiyonel, eğer ihtiyaç varsa
from tkinter import ttk

# <-- (DEĞİŞİKLİK) yeni fonksiyon import
from matplotlib_theme import apply_matplotlib_theme

def open_parameter_visualisation(shared_data):
    # (DEĞİŞİKLİK) Önce matplotlib temayı uygula
    apply_matplotlib_theme()

    visualisation_window = ctk.CTkToplevel()
    visualisation_window.title("Parameter Visualisation")

    # Ekran boyutuna göre otomatik açmak (istenirse):
    screen_w = visualisation_window.winfo_screenwidth()
    screen_h = visualisation_window.winfo_screenheight()
    win_w = int(screen_w * 0.8)
    win_h = int(screen_h * 0.8)
    x_pos = (screen_w - win_w) // 2
    y_pos = (screen_h - win_h) // 2
    visualisation_window.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")

    container_frame = ctk.CTkFrame(master=visualisation_window)
    container_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

    graph_elements = {}
    slave_ids = list(shared_data.keys())
    slave_count = len(slave_ids)

    # 2 sütun, satır sayısı:
    rows = slave_count // 2 + (slave_count % 2)

    # Subplot boyutu, 2x2 layout (ama siz tek satırda 4 subplot isterseniz yine 1x4 ayarlayabilirsiniz).
    # (DEĞİŞİKLİK) Boyutları çok büyükse üst üste binme oluyor, hafifçe arttırıyoruz:
    fig_width = 5.4  
    fig_height = 3.8

    for idx, slave_id in enumerate(slave_ids):
        row, col = divmod(idx, 2)

        slave_frame = ctk.CTkFrame(master=container_frame, corner_radius=5)
        slave_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        slave_label = ctk.CTkLabel(master=slave_frame, 
                                   text=f"Slave: {slave_id.upper()}", 
                                   font=("Arial", 11, "bold"))
        slave_label.pack(anchor="w", padx=5, pady=5)

        content_frame = ctk.CTkFrame(master=slave_frame)
        content_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # content_frame'i grid'le: 2 sütun -> [0: grafik, 1: tablo]
        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        graph_frame = ctk.CTkFrame(master=content_frame, corner_radius=5)
        graph_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # (DEĞİŞİKLİK) Figure/axes oluşturma
        fig = Figure(figsize=(fig_width, fig_height), dpi=100)
        fig.patch.set_facecolor("#EFEFEF")  # Ana panelin arka planı.
 

        # Biraz spacing eklemek için subplots_adjust:
        fig.subplots_adjust(left=0.1, right=0.95, top=0.80, bottom=0.15, wspace=0.3, hspace=0.5)

        ax_velocity = fig.add_subplot(2, 2, 1)
        ax_position = fig.add_subplot(2, 2, 2)
        ax_load = fig.add_subplot(2, 2, 3)
        ax_torque = fig.add_subplot(2, 2, 4)

        ax_velocity.set_title("Velocity", fontsize=5)
        ax_position.set_title("Position", fontsize=5)
        ax_load.set_title("Motor Load", fontsize=5)
        ax_torque.set_title("Torque", fontsize=5)

        ax_velocity.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax_position.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax_load.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax_torque.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

        ax_velocity.tick_params(axis='y', labelsize=4)
        ax_position.tick_params(axis='y', labelsize=4)
        ax_load.tick_params(axis='y', labelsize=4)
        ax_torque.tick_params(axis='y', labelsize=4)



        # Başlangıç verileri
        x_data = list(range(10))
        y_velocity = [0]*10
        y_position = [0]*10
        y_load = [0]*10
        y_torque = [0]*10

        velocity_line, = ax_velocity.plot(x_data, y_velocity, color="#377eb8", linewidth=1.2)
        position_line, = ax_position.plot(x_data, y_position, color="#4daf4a", linewidth=1.2)
        load_line,     = ax_load.plot(x_data, y_load, color="#e41a1c", linewidth=1.2)
        torque_line,   = ax_torque.plot(x_data, y_torque, color="#ff7f0e", linewidth=1.2)

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Tablo
        table_frame = ctk.CTkFrame(master=content_frame, corner_radius=5)
        table_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        table = ttk.Treeview(master=table_frame, columns=("Parameter", "Value"), show="headings", height=5)
        table.heading("Parameter", text="Parameter")
        table.heading("Value", text="Value")
        table.column("Parameter", width=130, anchor="center")
        table.column("Value", width=60, anchor="center")

        table.insert("", "end", values=("Voltage of Control Power", "0"))
        table.insert("", "end", values=("Output Voltage", "0"))
        table.insert("", "end", values=("Output Current", "0"))
        table.insert("", "end", values=("Drive Temperature", "0"))
        table.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        graph_elements[slave_id] = {
            "velocity_line": velocity_line,
            "position_line": position_line,
            "load_line": load_line,
            "torque_line": torque_line,
            "y_velocity": y_velocity,
            "y_position": y_position,
            "y_load": y_load,
            "y_torque": y_torque,
            "canvas": canvas,
            "axes": [ax_velocity, ax_position, ax_load, ax_torque],
            "table": table,
        }

    # container_frame'i grid_row/columnconfigure
    for c in range(2):
        container_frame.columnconfigure(c, weight=1)
    for r in range(rows):
        container_frame.rowconfigure(r, weight=1)

    def update_graphs():
        for slave_id, data in shared_data.items():
            if slave_id not in graph_elements:
                continue

            elems = graph_elements[slave_id]

            new_vel = data.get("velocity", 0)
            new_pos = data.get("position", 0)
            new_load = data.get("load", 0)
            new_torque = data.get("torque", 0)

            elems["y_velocity"].append(new_vel)
            elems["y_position"].append(new_pos)
            elems["y_load"].append(new_load)
            elems["y_torque"].append(new_torque)

            x_idx = list(range(len(elems["y_velocity"])))

            elems["velocity_line"].set_xdata(x_idx)
            elems["velocity_line"].set_ydata(elems["y_velocity"])

            elems["position_line"].set_xdata(x_idx)
            elems["position_line"].set_ydata(elems["y_position"])

            elems["load_line"].set_xdata(x_idx)
            elems["load_line"].set_ydata(elems["y_load"])

            elems["torque_line"].set_xdata(x_idx)
            elems["torque_line"].set_ydata(elems["y_torque"])

            for ax_ in elems["axes"]:
                ax_.relim()
                ax_.autoscale_view()

            # Tablo güncelle
            table = elems["table"]
            table.delete(*table.get_children())
            table.insert("", "end", values=("Voltage of Control Power", data.get("Voltage_of_Control_Power", 0)))
            table.insert("", "end", values=("Output Voltage", data.get("Output_Voltage", 0)))
            table.insert("", "end", values=("Output Current", data.get("Output_Current", 0)))
            table.insert("", "end", values=("Drive Temperature", data.get("Drive_Temperature", 0)))

            elems["canvas"].draw()

        visualisation_window.after(100, update_graphs)

    update_graphs()

def create_menu_bar(root, shared_data):
    menu_bar = CTkMenuBar(master=root)

    param_button = menu_bar.add_cascade("Parameter View")
    param_dropdown = CustomDropdownMenu(widget=param_button)
    param_dropdown.add_option(
        option="Parameter Visualisation",
        command=lambda: open_parameter_visualisation(shared_data)
    )
    return menu_bar
