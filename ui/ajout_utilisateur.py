import tkinter as tk
from tkinter import ttk, messagebox

def AjouterUtilisateur(parent):
    # Palette clinique moderne et rassurante
    PRIMARY = "#2d9cdb"      # Bleu clinique
    SECONDARY = "#27c9a9"    # Vert clinique
    BG = "#f7fafc"           # Fond général
    BTN_TEXT = "#2d3436"
    ENTRY_BG = "#eaf6fb"
    LABEL_FG = "#0984e3"

    fen = tk.Toplevel(parent)
    fen.title("Ajouter un nouvel utilisateur")
    fen.geometry("600x650")
    fen.configure(bg=BG)
    fen.resizable(False, False)

    # Frame principal
    main_frame = tk.Frame(fen, bg=BG)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header = tk.Frame(main_frame, bg=BG)
    header.pack(pady=(40, 0))
    tk.Label(header, text="👤", font=("Arial", 38, "bold"), bg=BG).pack(side=tk.LEFT, padx=(0, 14))
    tk.Label(header, text="Créer un nouvel utilisateur", font=("Segoe UI", 22, "bold"), bg=BG, fg=PRIMARY).pack(side=tk.LEFT)

    # Champs
    form_frame = tk.Frame(main_frame, bg=BG)
    form_frame.pack(pady=(30, 0), fill=tk.BOTH, expand=True)

    fields = [
        {"label": "Nom d'utilisateur", "var": tk.StringVar()},
        {"label": "Mot de passe", "var": tk.StringVar(), "show": "*"},
        {"label": "Email", "var": tk.StringVar()},
        {"label": "Rôle", "var": tk.StringVar()},
    ]

    entries = []
    for idx, field in enumerate(fields):
        tk.Label(form_frame, text=field["label"], font=("Segoe UI", 14, "bold"), bg=BG, fg=LABEL_FG).pack(anchor="w", padx=80, pady=(18 if idx == 0 else 12, 2))
        if field["label"] == "Rôle":
            combo = ttk.Combobox(form_frame, textvariable=field["var"], state="readonly", font=("Segoe UI", 13))
            combo["values"] = ("admin", "medecin", "secretaire", "patient")
            combo.pack(fill=tk.X, padx=80, pady=4, ipady=5)
            entries.append(combo)
        else:
            entry = tk.Entry(form_frame, textvariable=field["var"], font=("Segoe UI", 13), bg=ENTRY_BG, fg=BTN_TEXT, relief=tk.FLAT, show=field.get("show", ""))
            entry.pack(fill=tk.X, padx=80, pady=4, ipady=8)
            entries.append(entry)

    # ✅ Fonction corrigée
    def enregistrer():
        username = fields[0]["var"].get().strip()
        password = fields[1]["var"].get().strip()
        email = fields[2]["var"].get().strip()
        role = fields[3]["var"].get().strip()  # ✅ Correction ici

        if not (username and password and email and role):
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.", parent=fen)
            return
        try:
            from services.gestion_utilisateurs import ajouter_utilisateur
            if ajouter_utilisateur(username, password, email, role):
                messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.", parent=fen)
                fen.destroy()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout de l'utilisateur.", parent=fen)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}", parent=fen)

    # Boutons bas
    btn_frame = tk.Frame(main_frame, bg=BG)
    btn_frame.pack(pady=(30, 20))

    tk.Button(
        btn_frame,
        text="Créer l'utilisateur",
        bg=SECONDARY,
        fg="white",
        font=("Segoe UI", 15, "bold"),
        relief=tk.FLAT,
        bd=0,
        activebackground=PRIMARY,
        activeforeground="white",
        width=20,
        height=2,
        command=enregistrer,
        cursor="hand2"
    ).pack(side=tk.LEFT, padx=20)

    tk.Button(
        btn_frame,
        text="Annuler",
        bg="#b2bec3",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        relief=tk.FLAT,
        bd=0,
        activebackground="#636e72",
        activeforeground="white",
        width=12,
        height=2,
        command=fen.destroy,
        cursor="hand2"
    ).pack(side=tk.LEFT, padx=20)

    # Citation
    tk.Label(
        main_frame,
        text="« Prendre soin, c'est aussi bien accueillir. »",
        font=("Segoe UI", 13, "italic"),
        bg=BG,
        fg=SECONDARY
    ).pack(side=tk.BOTTOM, pady=10)
