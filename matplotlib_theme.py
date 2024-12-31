import customtkinter as ctk
import matplotlib as mpl

def apply_matplotlib_theme():


    appearance_mode = ctk.get_appearance_mode()  #

    if appearance_mode == "dark":
        bg_color = "#343638"      # arka plan
        axes_color = "#1D1E1E"    # eksen arka planı
        text_color = "#DCE4EE"    # yazı rengi
        grid_color = "#5A5A5A"    # çizgilerin rengi
    else:
        
        bg_color = "#F9F9FA"
        axes_color = "#F1F1F1"
        text_color = "black"
        grid_color = "#b3b3b3"

    # rcParams ile Matplotlib’i güncelliyoruz
    mpl.rcParams.update({
        "figure.figsize": (4.5, 3.5),
        "figure.facecolor": bg_color,
        "axes.facecolor": axes_color,
        "savefig.facecolor": bg_color,

        "axes.edgecolor": text_color,
        "axes.labelcolor": text_color,
        "axes.titlecolor": text_color,
        "xtick.color": text_color,
        "ytick.color": text_color,
        "text.color": text_color,
        "grid.color": grid_color,

        "axes.linewidth": 0.8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,

        # Font boyutu vb.
        "font.size": 9,
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
    })
