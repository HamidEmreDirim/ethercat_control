# ui_main.py
import customtkinter as ctk
import config
import motor_controller
from menu_bar import create_menu_bar

def create_main_window():
    ctk.set_appearance_mode("Dark")  
    ctk.set_default_color_theme("./themes/red.json")

    # 1) Motor manager'ı başlat
    motor_controller.init_motor_manager()

    root = ctk.CTk()
    root.title("UI Design")

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    window_w = int(screen_w * 0.8)
    window_h = int(screen_h * 0.8)
    x_pos = (screen_w - window_w) // 2
    y_pos = (screen_h - window_h) // 2
    root.geometry(f"{window_w}x{window_h}+{x_pos}+{y_pos}")
    root.resizable(True, True)

    # Üst menü
    menu_bar = create_menu_bar(root, config.shared_data)
    menu_bar.pack(fill=ctk.X)

    main_frame = ctk.CTkFrame(root, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    main_frame.rowconfigure((0,1), weight=1)
    main_frame.columnconfigure((0,1), weight=1)

    systems = []
    for i in range(4):
        frame = ctk.CTkFrame(main_frame, corner_radius=10)
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
        systems.append(frame)

        title = ctk.CTkLabel(frame, text=f"SYSTEM-{i+1}", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        # controls_frame
        controls_frame = ctk.CTkFrame(frame)
        controls_frame.pack(fill="both", expand=True, padx=5, pady=5)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        # VELOCITY
        sub_frame_velocity = ctk.CTkFrame(controls_frame)
        sub_frame_velocity.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        position_frame_v = ctk.CTkFrame(sub_frame_velocity, fg_color="transparent")
        position_frame_v.pack(anchor="center", pady=3)

        velocity_label = ctk.CTkLabel(position_frame_v, text="VELOCITY", font=("Arial", 13))
        velocity_label.pack(side=ctk.LEFT, padx=5)

        switch_var_v = ctk.StringVar(value="on")
        toggle_switch_v = ctk.CTkSwitch(
            master=position_frame_v,
            text="",
            variable=switch_var_v,
            command=lambda sv=switch_var_v, st=f"velocity_motor_{i+1}": motor_controller.handle_switch(sv, st),
            onvalue="on",
            offvalue="off"
        )
        toggle_switch_v.pack(side=ctk.LEFT, padx=5)

        config.config_labels[f"velocity_config_label_{i+1}"] = ctk.CTkLabel(
            sub_frame_velocity, 
            text="UNCONFIGURED",
            font=("Arial", 12, "bold"),

            text_color="red"
        )
        config.config_labels[f"velocity_config_label_{i+1}"].pack(pady=2)

        config.motor_sliders[f"velocity_motor_{i+1}"] = ctk.CTkSlider(
            sub_frame_velocity,
            from_=-500, to=500,
            orientation="horizontal",
            command=lambda value, idx=config.motor_num[f"velocity_{i+1}"], i=i: (
                motor_controller.on_motor_slider_change(value, idx),
                config.info_labels[f"velocity_slider_value_{i+1}"].configure(text=f"{value:.1f}")
            )
        )
        config.motor_sliders[f"velocity_motor_{i+1}"].pack(fill=ctk.X, padx=5, pady=5)

        # Add value label for velocity slider
        velocity_value_frame = ctk.CTkFrame(sub_frame_velocity, fg_color="transparent")
        velocity_value_frame.pack(fill=ctk.X, padx=5)
        velocity_value_frame.columnconfigure(0, weight=1)

        config.info_labels[f"velocity_slider_value_{i+1}"] = ctk.CTkLabel(
            velocity_value_frame,
            
            text="0.0",
            font=("Arial", 12, "bold"),
            width=80
        )
        config.info_labels[f"velocity_slider_value_{i+1}"].pack(side=ctk.RIGHT, padx=5)

        v_id = config.motor_num[f"velocity_{i+1}"]
        config.slider_ids[f"velocity_motor_{i+1}"] = v_id

        labels_frame_v = ctk.CTkFrame(sub_frame_velocity)
        labels_frame_v.pack(pady=3, fill="x")
        labels_frame_v.columnconfigure((0,1), weight=1)

        config.info_labels[f"velocity_load_{i+1}"] = ctk.CTkLabel(labels_frame_v, text="Load:", font=("Arial", 13))
        config.info_labels[f"velocity_load_{i+1}"].grid(row=0, column=0, padx=5, pady=2, sticky="w")

        config.info_labels[f"velocity_position_{i+1}"] = ctk.CTkLabel(labels_frame_v, text="Position:", font=("Arial", 13))
        config.info_labels[f"velocity_position_{i+1}"].grid(row=0, column=1, padx=5, pady=2, sticky="w")

        config.info_labels[f"velocity_velocity_{i+1}"] = ctk.CTkLabel(labels_frame_v, text="Velocity:", font=("Arial", 13))
        config.info_labels[f"velocity_velocity_{i+1}"].grid(row=1, column=0, padx=5, pady=2, sticky="w")

        config.info_labels[f"velocity_torque_{i+1}"] = ctk.CTkLabel(labels_frame_v, text="Torque:", font=("Arial", 13))
        config.info_labels[f"velocity_torque_{i+1}"].grid(row=1, column=1, padx=5, pady=2, sticky="w")

        logs_frame_v = ctk.CTkFrame(sub_frame_velocity, corner_radius=10)
        logs_frame_v.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        logs_label_v = ctk.CTkLabel(logs_frame_v, text="Logs", font=("Arial", 12, "bold"), anchor="w")
        logs_label_v.pack(fill=ctk.X, padx=5, pady=(3,0))

        config.logs[f"{v_id}"] = ctk.CTkTextbox(
            logs_frame_v,
            height=50,
            width=200,
            corner_radius=8,
            fg_color="#F5F5F5",
            text_color="#000000",
            font=("Courier", 11)
        )
        config.logs[f"{v_id}"].pack(fill=ctk.BOTH, expand=True, padx=5, pady=(0,5))

        # POSITION
        sub_frame_position = ctk.CTkFrame(controls_frame)
        sub_frame_position.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        position_frame_p = ctk.CTkFrame(sub_frame_position, fg_color="transparent")
        position_frame_p.pack(anchor="center", pady=3)

        position_label = ctk.CTkLabel(position_frame_p, text="POSITION", font=("Arial", 13))
        position_label.pack(side=ctk.LEFT, padx=5)

        switch_var_p = ctk.StringVar(value="on")
        toggle_switch_p = ctk.CTkSwitch(
            master=position_frame_p,
            text="",
            variable=switch_var_p,
            command=lambda sv=switch_var_p, st=f"position_motor_{i+1}": motor_controller.handle_switch(sv, st),
            onvalue="on",
            offvalue="off"
        )
        toggle_switch_p.pack(side=ctk.LEFT, padx=5)

        config.config_labels[f"position_config_label_{i+1}"] = ctk.CTkLabel(
            sub_frame_position,
            text="UNCONFIGURED",
            font=("Arial", 12, "bold"),
            text_color="red"
        )
        config.config_labels[f"position_config_label_{i+1}"].pack(pady=2)

        config.motor_sliders[f"position_motor_{i+1}"] = ctk.CTkSlider(
            sub_frame_position,
            from_=-180, to=180,
            orientation="horizontal",
            command=lambda value, idx=config.motor_num[f"position_{i+1}"], i=i: (
                motor_controller.on_motor_slider_change(value, idx),
                config.info_labels[f"position_slider_value_{i+1}"].configure(text=f"{value:.1f}")
            )
        )
        config.motor_sliders[f"position_motor_{i+1}"].pack(fill=ctk.X, padx=5, pady=5)

        # Add value label for position slider
        position_value_frame = ctk.CTkFrame(sub_frame_position, fg_color="transparent")
        position_value_frame.pack(fill=ctk.X, padx=5)
        position_value_frame.columnconfigure(0, weight=1)

        config.info_labels[f"position_slider_value_{i+1}"] = ctk.CTkLabel(
            position_value_frame,
            text="0.0",
            font=("Arial", 12, "bold"),
            width=80
        )
        config.info_labels[f"position_slider_value_{i+1}"].pack(side=ctk.RIGHT, padx=5)

        p_id = config.motor_num[f"position_{i+1}"]
        config.slider_ids[f"position_motor_{i+1}"] = p_id

        labels_frame_p = ctk.CTkFrame(sub_frame_position)
        labels_frame_p.pack(pady=3, fill="x")
        labels_frame_p.columnconfigure((0,1), weight=1)

        config.info_labels[f"position_load_{i+1}"] = ctk.CTkLabel(labels_frame_p, text="Load:", font=("Arial", 13))
        config.info_labels[f"position_load_{i+1}"].grid(row=0, column=0, padx=5, pady=2, sticky="w")

        config.info_labels[f"position_position_{i+1}"] = ctk.CTkLabel(labels_frame_p, text="Position:", font=("Arial", 13))
        config.info_labels[f"position_position_{i+1}"].grid(row=0, column=1, padx=5, pady=2, sticky="w")

        config.info_labels[f"position_velocity_{i+1}"] = ctk.CTkLabel(labels_frame_p, text="Velocity:", font=("Arial", 13))
        config.info_labels[f"position_velocity_{i+1}"].grid(row=1, column=0, padx=5, pady=2, sticky="w")

        config.info_labels[f"position_torque_{i+1}"] = ctk.CTkLabel(labels_frame_p, text="Torque:", font=("Arial", 13))
        config.info_labels[f"position_torque_{i+1}"].grid(row=1, column=1, padx=5, pady=2, sticky="w")

        logs_frame_p = ctk.CTkFrame(sub_frame_position, corner_radius=10)
        logs_frame_p.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        logs_label_p = ctk.CTkLabel(logs_frame_p, text="Logs", font=("Arial", 12, "bold"), anchor="w")
        logs_label_p.pack(fill=ctk.X, padx=5, pady=(3,0))

        config.logs[f"{p_id}"] = ctk.CTkTextbox(
            logs_frame_p,
            height=50,
            width=200,
            corner_radius=8,
            fg_color="#F5F5F5",
            text_color="#000000",
            font=("Courier", 11)
        )
        config.logs[f"{p_id}"].pack(fill=ctk.BOTH, expand=True, padx=5, pady=(0,5))

    # Bottom frame configuration
    bottom_frame = ctk.CTkFrame(root, corner_radius=10)
    bottom_frame.pack(fill=ctk.X, padx=10, pady=10)
    
    # Configure columns with proper weights
    bottom_frame.columnconfigure(1, weight=3)  # Slider column gets more space
    bottom_frame.columnconfigure(2, weight=1)  # Value label column
    bottom_frame.columnconfigure(3, weight=1)  # Button column

    def on_all_velocity_slider_change(value):
        velocity_value_label.configure(text=f"{value:.1f}")
        for key, val in config.motor_sliders.items():
            if key.startswith("velocity"):
                val.set(value)
                motor_controller.on_motor_slider_change(value, config.slider_ids[key])
                if motor_controller.motor_manager:
                    # Burada doğrudan anında gönderim var;
                    # isterseniz yine tampon yapısına döndürebilirsiniz,
                    # ancak talep dışı olduğu için aynen koruyoruz.
                    motor_controller.motor_manager.set_velocity(config.slider_ids[key], value)

    def on_all_position_slider_change(value):
        position_value_label.configure(text=f"{value:.1f}")
        for key, val in config.motor_sliders.items():
            if key.startswith("position"):
                val.set(value)
                motor_controller.on_motor_slider_change(value, config.slider_ids[key])
                if motor_controller.motor_manager:
                    motor_controller.motor_manager.set_position(config.slider_ids[key], value)

    def on_stop():
        for key, val in config.motor_sliders.items():
            config.motor_sliders[key].set(0)
        slider_velocity.set(0)
        on_all_velocity_slider_change(0)
        slider_position.set(0)
        on_all_position_slider_change(0)

    slider_velocity_label = ctk.CTkLabel(bottom_frame, text="ALL VELOCITY", font=("Arial", 12, "bold"))
    slider_velocity_label.grid(row=0, column=0, padx=5, pady=2)

    slider_velocity = ctk.CTkSlider(
        bottom_frame, from_=-500, to=500,
        orientation="horizontal", command=on_all_velocity_slider_change
    )
    slider_velocity.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    # Make value label more visible
    velocity_value_label = ctk.CTkLabel(bottom_frame, text="0.0", font=("Arial", 12, "bold"), width=80)
    velocity_value_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")

    slider_position_label = ctk.CTkLabel(bottom_frame, text="ALL POSITION", font=("Arial", 12, "bold"))
    slider_position_label.grid(row=1, column=0, padx=5, pady=2)

    slider_position = ctk.CTkSlider(
        bottom_frame, from_=-180, to=180,
        orientation="horizontal", command=on_all_position_slider_change
    )
    slider_position.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

    # Make value label more visible
    position_value_label = ctk.CTkLabel(bottom_frame, text="0.0", font=("Arial", 12, "bold"), width=80)
    position_value_label.grid(row=1, column=2, padx=5, pady=2, sticky="w")

    start_btn = ctk.CTkButton(bottom_frame, text="Start", font=("Arial", 12, "bold"), command=motor_controller.start_config)
    start_btn.grid(row=0, column=3, padx=5, pady=2)

    stop_btn = ctk.CTkButton(bottom_frame, text="Stop", font=("Arial", 12, "bold"), command=on_stop)
    stop_btn.grid(row=1, column=3, padx=5, pady=2)

    # poll_data'yı başlat (eski haliyle)
    motor_controller.poll_data(root)

    # ---------------------------------------------------
    # [YENİ] update_motors fonksiyonunu da periyodik çağırıyoruz:
    # ---------------------------------------------------
    def schedule_update_motors():
        motor_controller.update_motors()
        root.after(100, schedule_update_motors)  # 100 ms'de bir tamponu gönder

    schedule_update_motors()

    return root  # Fonksiyon, root'u döndürüyor
