import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # pip install pillow

class AccueilPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clinique Médicale - Accueil")
        self.geometry("900x520")
        self.configure(bg="#f4f8fb")  # Couleur douce

        # Chargement du logo
        try:
            image = Image.open("logo_clinique.png")
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)
            tk.Label(self, image=photo, bg="#f4f8fb").pack(pady=(30, 10))
            self.logo = photo
        except Exception:
            tk.Label(self, text="🏥", font=("Arial", 50), bg="#f4f8fb").pack(pady=(30, 10))

        # Titre
        tk.Label(
            self,
            text="Bienvenue sur le Système de Gestion de la Clinique",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f8fb",
            fg="#2d9cdb"
        ).pack(pady=(0, 10))

        # Sous-titre
        tk.Label(
            self,
            text="Gérez vos rendez-vous, dossiers médicaux et prescriptions\nen toute sécurité et confidentialité.",
            font=("Segoe UI", 12),
            bg="#f4f8fb",
            fg="#636e72",
            justify="center"
        ).pack(pady=(0, 30))

        # Style moderne pour ttk
        style = ttk.Style(self)
        style.configure("Accent.TButton", font=("Segoe UI", 13, "bold"), foreground="#2d9cdb", background="#0984e3")
        style.map("Accent.TButton", background=[("active", "#74b9ff")])

        # Bouton Connexion stylé
        bouton_connexion = ttk.Button(self, text="🔐 Connexion", style="Accent.TButton", command=self.aller_connexion)
        bouton_connexion.pack(ipadx=20, ipady=10)

        # Footer stylé
        tk.Label(
            self,
            text="Université Gamal Abdel Nasser de Conakry\nProjet : Système de Gestion de Clinique Médicale",
            font=("Segoe UI", 9),
            bg="#f4f8fb",
            fg="#8395a7",
            justify="center"
        ).pack(side=tk.BOTTOM, pady=20)

    def aller_connexion(self):
        self.destroy()
        from ui.login import afficher_page_connexion
        afficher_page_connexion()
