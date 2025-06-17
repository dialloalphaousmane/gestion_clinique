import tkinter as tk
from tkinter import ttk, messagebox
from db.connexion import connect_db
from datetime import datetime, timedelta

class MedecinPage(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(f"Espace Médecin - {self.user['username']}")
        self.geometry("800x600")
        self.configure(bg="#f7f7f7")

        self.style = ttk.Style()
        self._configure_styles()

        # Titre
        tk.Label(
            self, 
            text=f"Bienvenue Dr {self.user['username']}", 
            font=("Helvetica", 18, "bold"), 
            bg="#f7f7f7", 
            fg="#2d3436"
        ).pack(pady=15)

        # Boutons
        btn_frame = tk.Frame(self, bg="#f7f7f7")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="📅 Mes Rendez-vous", command=self.afficher_rendezvous).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="👤 Mes Patients", command=self.afficher_patients).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="🔔 Voir mes rappels", command=self.verifier_rappels_rendezvous).pack(side=tk.LEFT, padx=15)
                # Bouton Déconnexion
        logout_btn = ttk.Button(self, text="🚪 Déconnexion", command=self.deconnexion)
        logout_btn.place(x=680, y=20)  # position en haut à droite

        # Treeview principal
        self.tree = ttk.Treeview(self, columns=("1", "2", "3"), show="headings", style="Custom.Treeview")
        self.tree.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        self.verifier_rappels_rendezvous()

    def _configure_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#0984e3", foreground="white", padding=6)
        self.style.map("TButton", background=[("active", "#74b9ff")])
        self.style.configure("Custom.Treeview", background="white", foreground="#2d3436",
                             rowheight=28, fieldbackground="white", font=("Segoe UI", 10))
        self.style.configure("Custom.Treeview.Heading", background="#dfe6e9", foreground="black", font=("Segoe UI", 10, "bold"))
        self.style.map("Custom.Treeview", background=[("selected", "#dfe6e9")])
    def deconnexion(self):
        self.destroy()  # ferme la fenêtre actuelle
        from ui.login import afficher_page_connexion  # importe ici pour éviter les import circulaires
        afficher_page_connexion()  # réaffiche la page de connexion

    def afficher_rendezvous(self):
        self._clear_context()
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("ID", "Patient", "Date et heure")

        for idx, name in enumerate(self.tree["columns"]):
            self.tree.heading(f"#{idx+1}", text=name)
            self.tree.column(f"#{idx+1}", anchor=tk.CENTER)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM medecins WHERE user_id = %s", (self.user['id'],))
            medecin = cursor.fetchone()
            if not medecin:
                messagebox.showerror("Erreur", "Aucun profil médecin trouvé.")
                cursor.close()
                conn.close()
                return

            cursor.execute("""
                SELECT r.id, CONCAT(p.nom, ' ', p.prenom) AS patient, r.date_rdv
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.medecin_id = %s
                ORDER BY r.date_rdv DESC
            """, (medecin['id'],))
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=(row['id'], row['patient'], row['date_rdv']))
            cursor.close()
            conn.close()

        self._add_context_button("📝 Saisir une consultation", "#00b894", self.saisir_consultation)

    def afficher_patients(self):
        self._clear_context()
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("ID", "Nom", "Prénom")

        for idx, name in enumerate(self.tree["columns"]):
            self.tree.heading(f"#{idx+1}", text=name)
            self.tree.column(f"#{idx+1}", anchor=tk.CENTER)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM medecins WHERE user_id = %s", (self.user['id'],))
            medecin = cursor.fetchone()
            if not medecin:
                messagebox.showerror("Erreur", "Aucun profil médecin trouvé.")
                cursor.close()
                conn.close()
                return

            cursor.execute("""
                SELECT DISTINCT p.id, p.nom, p.prenom
                FROM patients p
                JOIN rendezvous r ON p.id = r.patient_id
                WHERE r.medecin_id = %s
            """, (medecin['id'],))
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=(row['id'], row['nom'], row['prenom']))
            cursor.close()
            conn.close()

        self._add_context_button("📋 Voir l'historique du patient sélectionné", "#6c5ce7", self.bouton_historique_patient)

    def saisir_consultation(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous à traiter.")
            return

        rdv_id = self.tree.item(item, "values")[0]
        patient_id = None

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT patient_id FROM rendezvous WHERE id = %s", (rdv_id,))
            row = cursor.fetchone()
            if row:
                patient_id = row['patient_id']
            cursor.close()
            conn.close()

        fen = tk.Toplevel(self)
        fen.title("Saisir une consultation")
        fen.geometry("600x600")
        fen.configure(bg="#f7f7f7")

        tk.Label(fen, text="Diagnostic :", bg="#f7f7f7", font=("Arial", 12)).pack(pady=5)
        entry_diag = tk.Text(fen, height=4)
        entry_diag.pack(pady=5)

        tk.Label(fen, text="Prescription :", bg="#f7f7f7", font=("Arial", 12)).pack(pady=5)
        entry_presc = tk.Text(fen, height=4)
        entry_presc.pack(pady=5)

        tree_hist = ttk.Treeview(fen, columns=("Date", "Diagnostic", "Prescription"), show="headings", height=5)
        for col in tree_hist["columns"]:
            tree_hist.heading(col, text=col)
            tree_hist.column(col, anchor=tk.CENTER)
        tree_hist.pack(expand=True, fill=tk.BOTH, pady=10)

        def enregistrer():
            diagnostic = entry_diag.get("1.0", tk.END).strip()
            prescription = entry_presc.get("1.0", tk.END).strip()
            if not diagnostic:
                messagebox.showerror("Erreur", "Le diagnostic est obligatoire.")
                return

            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO consultations (rdv_id, diagnostic, prescription) VALUES (%s, %s, %s)",
                    (rdv_id, diagnostic, prescription)
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Succès", "Consultation enregistrée.")
                entry_diag.delete("1.0", tk.END)
                entry_presc.delete("1.0", tk.END)

                # Refresh historique
                tree_hist.delete(*tree_hist.get_children())
                conn = connect_db()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT c.date_consultation, c.diagnostic, c.prescription
                        FROM consultations c
                        JOIN rendezvous r ON c.rdv_id = r.id
                        WHERE r.patient_id = %s
                        ORDER BY c.date_consultation DESC
                    """, (patient_id,))
                    for row in cursor.fetchall():
                        tree_hist.insert("", tk.END, values=(row['date_consultation'], row['diagnostic'], row['prescription']))
                    cursor.close()
                    conn.close()

        ttk.Button(fen, text="✅ Enregistrer la consultation", command=enregistrer).pack(pady=15)

        if patient_id:
            conn = connect_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT c.date_consultation, c.diagnostic, c.prescription
                    FROM consultations c
                    JOIN rendezvous r ON c.rdv_id = r.id
                    WHERE r.patient_id = %s
                    ORDER BY c.date_consultation DESC
                """, (patient_id,))
                for row in cursor.fetchall():
                    tree_hist.insert("", tk.END, values=(row['date_consultation'], row['diagnostic'], row['prescription']))
                cursor.close()
                conn.close()

    def afficher_historique(self, patient_id):
        fen = tk.Toplevel(self)
        fen.title("Historique des consultations")
        fen.geometry("600x400")

        tree = ttk.Treeview(fen, columns=("Date", "Diagnostic", "Prescription"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        tree.pack(expand=True, fill=tk.BOTH, pady=10)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.date_consultation, c.diagnostic, c.prescription
                FROM consultations c
                JOIN rendezvous r ON c.rdv_id = r.id
                WHERE r.patient_id = %s
                ORDER BY c.date_consultation DESC
            """, (patient_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(row['date_consultation'], row['diagnostic'], row['prescription']))
            cursor.close()
            conn.close()

    def bouton_historique_patient(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un patient.")
            return
        patient_id = self.tree.item(item, "values")[0]
        self.afficher_historique(patient_id)

    def verifier_rappels_rendezvous(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM medecins WHERE user_id = %s", (self.user['id'],))
            medecin = cursor.fetchone()
            if not medecin:
                cursor.close()
                conn.close()
                return

            medecin_id = medecin['id']
            now = datetime.now()
            dans_24h = now + timedelta(hours=24)

            cursor.execute("""
                SELECT r.date_rdv, p.nom, p.prenom
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.medecin_id = %s AND r.date_rdv BETWEEN %s AND %s AND r.statut = 'prévu'
                ORDER BY r.date_rdv ASC
            """, (medecin_id, now.strftime('%Y-%m-%d %H:%M:%S'), dans_24h.strftime('%Y-%m-%d %H:%M:%S')))
            rdvs = cursor.fetchall()
            cursor.close()
            conn.close()

            if rdvs:
                msg = "📅 Rendez-vous à venir dans les 24h :\n"
                for rdv in rdvs:
                    msg += f"  • {rdv['date_rdv']} avec {rdv['nom']} {rdv['prenom']}\n"
                messagebox.showinfo("Rappels de rendez-vous", msg)

    def _clear_context(self):
        if hasattr(self, 'btn_context_frame') and self.btn_context_frame and self.btn_context_frame.winfo_exists():
            self.btn_context_frame.destroy()

    def _add_context_button(self, text, bg_color, command):
        self.btn_context_frame = tk.Frame(self, bg="#f7f7f7")
        self.btn_context_frame.pack(pady=10)
        ttk.Button(self.btn_context_frame, text=text, command=command).pack(side=tk.LEFT, padx=10)
