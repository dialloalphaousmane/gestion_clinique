import tkinter as tk
from tkinter import ttk, messagebox
from db.connexion import connect_db
from datetime import datetime, timedelta

# Palette de couleurs clinique
COLOR_BG = "#f0f8ff"  # Fond bleu très clair
COLOR_HEADER = "#0078d7"  # Bleu vif
COLOR_CARD = "#ffffff"  # Blanc pour cartes
COLOR_BTN = "#00b0f0"  # Bleu turquoise
COLOR_BTN_HOVER = "#0091d1"  # Bleu turquoise foncé
COLOR_TEXT = "#2c3e50"  # Texte foncé
COLOR_ACCENT = "#00b894"  # Vert
COLOR_WARNING = "#f39c12"  # Orange pour les alertes

class PatientPage(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(f"Espace Patient - {self.user['username']}")
        self.geometry("800x600")
        self.configure(bg=COLOR_BG)
        
        # Header
        header_frame = tk.Frame(self, bg=COLOR_HEADER, height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(
            header_frame, 
            text=f"Bienvenue {self.user['username']}", 
            font=("Segoe UI", 18, "bold"), 
            bg=COLOR_HEADER, 
            fg="white"
        ).pack(pady=20, side=tk.LEFT, padx=30)
        
        # Badge patient
        tk.Label(
            header_frame, 
            text="PATIENT", 
            font=("Segoe UI", 10, "bold"), 
            bg="#00b894", 
            fg="white",
            padx=8,
            pady=2
        ).pack(pady=20, side=tk.RIGHT, padx=30)
        
        # Contenu principal
        main_frame = tk.Frame(self, bg=COLOR_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Boutons d'action
        btn_frame = tk.Frame(main_frame, bg=COLOR_BG)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Style des boutons
        btn_style = {
            "bg": COLOR_BTN,
            "fg": "white",
            "activebackground": COLOR_BTN_HOVER,
            "font": ("Segoe UI", 11, "bold"),
            "bd": 0,
            "relief": tk.FLAT,
            "width": 15,
            "height": 2,
            "cursor": "hand2"
        }
        
        tk.Button(btn_frame, text="📅 Mes Rendez-vous", command=self.afficher_mes_rendezvous, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="🩺 Mes Consultations", command=self.afficher_mes_consultations, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="🔔 Mes Rappels", command=self.verifier_rappels_rendezvous, **btn_style).pack(side=tk.LEFT, padx=10)
                # Bouton Déconnexion
        logout_btn = ttk.Button(self, text="🚪 Déconnexion", command=self.deconnexion)
        logout_btn.place(x=680, y=20)  # position en haut à droite

        # Cadre pour le tableau
        table_frame = tk.Frame(main_frame, bg=COLOR_BG)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style du tableau
        style = ttk.Style()
        style.configure("Treeview.Heading", 
                       font=('Segoe UI', 10, 'bold'), 
                       background=COLOR_HEADER, 
                       foreground="white")
        style.configure("Treeview", 
                       font=('Segoe UI', 10), 
                       rowheight=30,
                       fieldbackground=COLOR_CARD)
        
        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Footer
        footer_frame = tk.Frame(self, bg=COLOR_HEADER, height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(
            footer_frame, 
            text="Clinique Médicale - Système Patient © 2025", 
            font=("Segoe UI", 9), 
            bg=COLOR_HEADER, 
            fg="white"
        ).pack(pady=10)

        # Appel automatique du rappel à l'ouverture
        self.verifier_rappels_rendezvous()

    def afficher_mes_rendezvous(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("ID", "Médecin", "Date", "Durée", "Statut")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120)
        
        # Ajuster les largeurs des colonnes
        self.tree.column("ID", width=50)
        self.tree.column("Médecin", width=150)
        self.tree.column("Date", width=150)
        self.tree.column("Durée", width=80)
        self.tree.column("Statut", width=100)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (self.user['id'],))
            patient = cursor.fetchone()
            if not patient:
                messagebox.showerror("Erreur", "Aucun profil patient trouvé pour cet utilisateur.")
                cursor.close()
                conn.close()
                return
            patient_id = patient['id']

            query = """
                SELECT r.id, u.login AS medecin, r.date_rdv, r.duree, r.statut
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                JOIN utilisateurs u ON m.user_id = u.id
                WHERE r.patient_id = %s
                ORDER BY r.date_rdv DESC
            """
            cursor.execute(query, (patient_id,))
            
            # Alternance de couleurs pour les lignes
            for i, row in enumerate(cursor.fetchall()):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=(
                    row['id'], 
                    row['medecin'], 
                    row['date_rdv'], 
                    row['duree'], 
                    row['statut']
                ), tags=(tag,))
            
            # Configuration des couleurs des lignes
            self.tree.tag_configure('evenrow', background=COLOR_CARD)
            self.tree.tag_configure('oddrow', background='#f5f9ff')
            
            cursor.close()
            conn.close()
    def deconnexion(self):
        self.destroy()  # ferme la fenêtre actuelle
        from ui.login import afficher_page_connexion  # importe ici pour éviter les import circulaires
        afficher_page_connexion()  # réaffiche la page de connexion

    def afficher_mes_consultations(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("Médecin", "Diagnostic", "Prescription")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", width=150)
        
        # Ajuster les largeurs des colonnes
        self.tree.column("Médecin", width=120)
        self.tree.column("Diagnostic", width=250)
        self.tree.column("Prescription", width=250)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (self.user['id'],))
            patient = cursor.fetchone()
            if not patient:
                messagebox.showerror("Erreur", "Aucun profil patient trouvé pour cet utilisateur.")
                cursor.close()
                conn.close()
                return
            patient_id = patient['id']

            query = """
                SELECT u.login AS medecin, c.diagnostic, c.prescription
                FROM consultations c
                JOIN rendezvous r ON c.rdv_id = r.id
                JOIN medecins m ON r.medecin_id = m.id
                JOIN utilisateurs u ON m.user_id = u.id
                WHERE r.patient_id = %s
            """
            cursor.execute(query, (patient_id,))
            
            # Alternance de couleurs pour les lignes
            for i, row in enumerate(cursor.fetchall()):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=(
                    row['medecin'], 
                    row['diagnostic'], 
                    row['prescription']
                ), tags=(tag,))
            
            # Configuration des couleurs des lignes
            self.tree.tag_configure('evenrow', background=COLOR_CARD)
            self.tree.tag_configure('oddrow', background='#f5f9ff')
            
            cursor.close()
            conn.close()

    def verifier_rappels_rendezvous(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (self.user['id'],))
            patient = cursor.fetchone()
            if not patient:
                cursor.close()
                conn.close()
                return
            patient_id = patient['id']

            now = datetime.now()
            dans_24h = now + timedelta(hours=24)
            query = """
                SELECT r.date_rdv, u.login AS medecin
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                JOIN utilisateurs u ON m.user_id = u.id
                WHERE r.patient_id = %s AND r.date_rdv BETWEEN %s AND %s AND r.statut = 'prévu'
                ORDER BY r.date_rdv ASC
            """
            cursor.execute(query, (patient_id, now.strftime('%Y-%m-%d %H:%M:%S'), dans_24h.strftime('%Y-%m-%d %H:%M:%S')))
            rdvs = cursor.fetchall()
            cursor.close()
            conn.close()

            if rdvs:
                msg = "Vous avez les rendez-vous suivants dans les prochaines 24h :\n\n"
                for rdv in rdvs:
                    msg += f"• {rdv['date_rdv']} avec le Dr {rdv['medecin']}\n"
                
                # Créer une fenêtre de rappel personnalisée
                reminder_win = tk.Toplevel(self)
                reminder_win.title("Rappel Rendez-vous")
                reminder_win.geometry("500x300")
                reminder_win.configure(bg=COLOR_BG)
                reminder_win.resizable(False, False)
                
                # Icône d'alerte
                tk.Label(
                    reminder_win, 
                    text="⏰", 
                    font=("Arial", 48), 
                    bg=COLOR_BG, 
                    fg=COLOR_WARNING
                ).pack(pady=(20, 10))
                
                # Message
                tk.Label(
                    reminder_win, 
                    text=msg, 
                    font=("Segoe UI", 11), 
                    bg=COLOR_BG, 
                    fg=COLOR_TEXT,
                    justify=tk.LEFT
                ).pack(padx=20, pady=10)
                
                # Bouton de fermeture
                tk.Button(
                    reminder_win, 
                    text="J'ai compris", 
                    bg=COLOR_ACCENT, 
                    fg="white",
                    activebackground="#00a885",
                    font=("Segoe UI", 11, "bold"),
                    bd=0,
                    relief=tk.FLAT,
                    padx=20,
                    pady=8,
                    command=reminder_win.destroy
                ).pack(pady=10)