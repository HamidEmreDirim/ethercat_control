import customtkinter as ctk

# Ana pencere oluşturma
app = ctk.CTk()
app.geometry("400x300")
app.title("CustomTkinter UI")

# UI öğeleri ekleme
label = ctk.CTkLabel(app, text="Merhaba, CustomTkinter!")
label.pack(pady=20)

button = ctk.CTkButton(app, text="Tıkla", command=lambda: print("Tıklandı!"))
button.pack(pady=10)

# Pencereyi çalıştırma
app.mainloop()

