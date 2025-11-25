import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x240")
app.title("Test Window")

button = ctk.CTkButton(app, text="Click Me", command=lambda: print("Clicked"))
button.pack(pady=20)

app.mainloop()
