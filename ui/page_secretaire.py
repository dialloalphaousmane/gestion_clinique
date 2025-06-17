import tkinter as tk
from tkinter import ttk, messagebox
from db.connexion import connect_db
from datetime import datetime
from ui.facturation import FacturationPage
from ui.listfacture import ListeFacturesPage
# si tu es dans le dossier ui/

class SecretairePage(tk.Tk):
    def __init__(self, user):  # Correction ici
        super().__init__() 
        from db.connexion import connect_db# Correction ici
        self.user = user
        self.title(f"Espace Secrétaire - {self.user['username']}")
        self.geometry("800x550")
        self.configure(bg="white")
        self.db_conn = connect_db()
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Label(self, text=f"Bienvenue {self.user['username']}", font=("Arial", 16), bg="white").pack(pady=10)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📅 Gérer les Rendez-vous", command=self.afficher_rendezvous, width=25).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="👤 Liste des Patients", command=self.afficher_patients, width=25).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="➕ Prendre un nouveau RDV", command=self.afficher_formulaire_rdv, bg="#00b894", fg="white", font=("Helvetica", 11), width=25).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="➕ Ajouter un patient", command=self.afficher_formulaire_patient, bg="#0984e3", fg="white", width=25).grid(row=0, column=3, padx=10)
                # Bouton Déconnexion
        logout_btn = ttk.Button(self, text="🚪 Déconnexion", command=self.deconnexion)
        logout_btn.place(x=680, y=20)  # position en haut à droite
        btn_facturation = ttk.Button(self, text="Facturation", command=self.ouvrir_facturation)
        btn_facturation.pack(pady=10)
        btn_facturation = ttk.Button(self, text="Factures", command=self.ouvrir_liste_factures)
        btn_facturation.pack(pady=10)
    def ouvrir_liste_factures(self):
        # self.db est la connexion à la base de données que tu passes à la fenêtre ListeFacturesPage
        ListeFacturesPage(self, self.db_conn)

    def ouvrir_facturation(self):
        FacturationPage(self, self.db_conn)
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def afficher_rendezvous(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("ID", "Patient", "Médecin", "Début du rendez-vous", "Durée (min)", "Statut")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT r.id, 
                       CONCAT(p.nom, ' ', p.prenom) AS patient, 
                       u.login AS medecin, 
                       r.date_rdv, 
                       r.duree, 
                       r.statut
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                JOIN medecins m ON r.medecin_id = m.id
                JOIN utilisateurs u ON m.user_id = u.id
                WHERE u.role = 'medecin'
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=(
                    row['id'],
                    row['patient'],
                    row['medecin'],
                    row['date_rdv'],
                    row['duree'],
                    row['statut']
                ))
            cursor.close()
            conn.close()

        # Supprimer les anciens boutons si déjà présents
        if hasattr(self, 'btn_rdv_frame') and self.btn_rdv_frame.winfo_exists():
            self.btn_rdv_frame.destroy()

        # >>> AJOUTE CETTE PARTIE POUR MASQUER LES BOUTONS PATIENT <<<
        if hasattr(self, 'btn_patient_frame') and self.btn_patient_frame.winfo_exists():
            self.btn_patient_frame.destroy()
        # <<< FIN AJOUT >>>

        # Ajouter les boutons sous le tableau
        self.btn_rdv_frame = tk.Frame(self, bg="white")
        self.btn_rdv_frame.pack(pady=10)
        tk.Button(self.btn_rdv_frame, text="Modifier le rendez-vous sélectionné", bg="#0984e3", fg="white",
                  command=lambda: self.modifier_rdv()).pack(side=tk.LEFT, padx=10)
        tk.Button(self.btn_rdv_frame, text="Supprimer le rendez-vous sélectionné", bg="#d63031", fg="white",
                  command=lambda: self.supprimer_rdv()).pack(side=tk.LEFT, padx=10)

    def modifier_rdv(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous à modifier.")
            return
        values = self.tree.item(item, "values")
        self.afficher_formulaire_rdv_modification(values)
    def deconnexion(self):
        self.destroy()  # ferme la fenêtre actuelle
        from ui.login import afficher_page_connexion  # importe ici pour éviter les import circulaires
        afficher_page_connexion()  # réaffiche la page de connexion

    def supprimer_rdv(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous à supprimer.")
            return
        rdv_id = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce rendez-vous ?"):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM rendezvous WHERE id = %s", (rdv_id,))
                    conn.commit()
                    messagebox.showinfo("Succès", "Rendez-vous supprimé.")
                    self.afficher_rendezvous()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")
                finally:
                    cursor.close()
                    conn.close()

    def afficher_patients(self):
        # Détruire la barre de recherche si elle existe déjà
        if hasattr(self, 'frame_recherche') and self.frame_recherche.winfo_exists():
            self.frame_recherche.destroy()

        # Créer la barre de recherche
        self.frame_recherche = tk.Frame(self)
        self.frame_recherche.pack(pady=5)

        tk.Label(self.frame_recherche, text="Nom:").grid(row=0, column=0)
        entry_nom = tk.Entry(self.frame_recherche)
        entry_nom.grid(row=0, column=1)

        tk.Label(self.frame_recherche, text="Prénom:").grid(row=0, column=2)
        entry_prenom = tk.Entry(self.frame_recherche)
        entry_prenom.grid(row=0, column=3)

        tk.Label(self.frame_recherche, text="Date de naissance:").grid(row=0, column=4)
        entry_date = tk.Entry(self.frame_recherche)
        entry_date.grid(row=0, column=5)

        def rechercher():
            nom = entry_nom.get()
            prenom = entry_prenom.get()
            date_naissance = entry_date.get()
            requete = "SELECT * FROM patients WHERE 1=1"
            params = []
            if nom:
                requete += " AND nom LIKE %s"
                params.append(f"%{nom}%")
            if prenom:
                requete += " AND prenom LIKE %s"
                params.append(f"%{prenom}%")
            if date_naissance:
                requete += " AND date_naissance = %s"
                params.append(date_naissance)

            self.tree.delete(*self.tree.get_children())
            conn = connect_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(requete, tuple(params))
                rows = cursor.fetchall()
                for row in rows:
                    self.tree.insert("", tk.END, values=(row['id'], row['nom'], row['prenom'], row['date_naissance'], row['groupe_sanguin'], row['assurance']))
                cursor.close()
                conn.close()

        tk.Button(self.frame_recherche, text="Rechercher", command=rechercher, bg="#00b894", fg="white").grid(row=0, column=6, padx=10)

        # Tableau des patients
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("ID", "Nom", "Prénom", "Date de naissance", "Groupe sanguin", "Assurance")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=(row['id'], row['nom'], row['prenom'], row['date_naissance'], row['groupe_sanguin'], row['assurance']))
            cursor.close()
            conn.close()

        # Supprimer les anciens boutons si déjà présents
        if hasattr(self, 'btn_patient_frame') and self.btn_patient_frame.winfo_exists():
            self.btn_patient_frame.destroy()

        # >>> AJOUTE CETTE PARTIE POUR MASQUER LES BOUTONS RDV <<<
        if hasattr(self, 'btn_rdv_frame') and self.btn_rdv_frame.winfo_exists():
            self.btn_rdv_frame.destroy()
        # <<< FIN AJOUT >>>

        # Ajouter les boutons sous le tableau
        self.btn_patient_frame = tk.Frame(self, bg="white")
        self.btn_patient_frame.pack(pady=10)
        tk.Button(self.btn_patient_frame, text="Modifier le patient sélectionné", bg="#0984e3", fg="white",
                  command=self.modifier_patient).pack(side=tk.LEFT, padx=10)
        tk.Button(self.btn_patient_frame, text="Supprimer le patient sélectionné", bg="#d63031", fg="white",
                  command=self.supprimer_patient).pack(side=tk.LEFT, padx=10)

    def modifier_rdv(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous à modifier.")
            return
        values = self.tree.item(item, "values")
        self.afficher_formulaire_rdv_modification(values)

    def supprimer_rdv(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous à supprimer.")
            return
        rdv_id = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce rendez-vous ?"):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM rendezvous WHERE id = %s", (rdv_id,))
                    conn.commit()
                    messagebox.showinfo("Succès", "Rendez-vous supprimé.")
                    self.afficher_rendezvous()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")
                finally:
                    cursor.close()
                    conn.close()

    def afficher_patients(self):
        # Détruire la barre de recherche si elle existe déjà
        if hasattr(self, 'frame_recherche') and self.frame_recherche.winfo_exists():
            self.frame_recherche.destroy()

        # Créer la barre de recherche
        self.frame_recherche = tk.Frame(self)
        self.frame_recherche.pack(pady=5)

        tk.Label(self.frame_recherche, text="Nom:").grid(row=0, column=0)
        entry_nom = tk.Entry(self.frame_recherche)
        entry_nom.grid(row=0, column=1)

        tk.Label(self.frame_recherche, text="Prénom:").grid(row=0, column=2)
        entry_prenom = tk.Entry(self.frame_recherche)
        entry_prenom.grid(row=0, column=3)

        tk.Label(self.frame_recherche, text="Date de naissance:").grid(row=0, column=4)
        entry_date = tk.Entry(self.frame_recherche)
        entry_date.grid(row=0, column=5)

        def rechercher():
            nom = entry_nom.get()
            prenom = entry_prenom.get()
            date_naissance = entry_date.get()
            requete = "SELECT * FROM patients WHERE 1=1"
            params = []
            if nom:
                requete += " AND nom LIKE %s"
                params.append(f"%{nom}%")
            if prenom:
                requete += " AND prenom LIKE %s"
                params.append(f"%{prenom}%")
            if date_naissance:
                requete += " AND date_naissance = %s"
                params.append(date_naissance)

            self.tree.delete(*self.tree.get_children())
            conn = connect_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(requete, tuple(params))
                rows = cursor.fetchall()
                for row in rows:
                    self.tree.insert("", tk.END, values=(row['id'], row['nom'], row['prenom'], row['date_naissance'], row['groupe_sanguin'], row['assurance']))
                cursor.close()
                conn.close()

        tk.Button(self.frame_recherche, text="Rechercher", command=rechercher, bg="#00b894", fg="white").grid(row=0, column=6, padx=10)

        # Tableau des patients
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("ID", "Nom", "Prénom", "Date de naissance", "Groupe sanguin", "Assurance")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=(row['id'], row['nom'], row['prenom'], row['date_naissance'], row['groupe_sanguin'], row['assurance']))
            cursor.close()
            conn.close()

        # Supprimer les anciens boutons si déjà présents
        if hasattr(self, 'btn_patient_frame') and self.btn_patient_frame.winfo_exists():
            self.btn_patient_frame.destroy()

        # >>> AJOUTE CETTE PARTIE POUR MASQUER LES BOUTONS RDV <<<
        if hasattr(self, 'btn_rdv_frame') and self.btn_rdv_frame.winfo_exists():
            self.btn_rdv_frame.destroy()
        # <<< FIN AJOUT >>>

        # Ajouter les boutons sous le tableau
        self.btn_patient_frame = tk.Frame(self, bg="white")
        self.btn_patient_frame.pack(pady=10)
        tk.Button(self.btn_patient_frame, text="Modifier le patient sélectionné", bg="#0984e3", fg="white",
                  command=self.modifier_patient).pack(side=tk.LEFT, padx=10)
        tk.Button(self.btn_patient_frame, text="Supprimer le patient sélectionné", bg="#d63031", fg="white",
                  command=self.supprimer_patient).pack(side=tk.LEFT, padx=10)

    def afficher_formulaire_rdv(self):
        fenetre_rdv = tk.Toplevel(self)
        fenetre_rdv.title("Prendre un nouveau Rendez-vous")
        fenetre_rdv.geometry("400x450")
        fenetre_rdv.configure(bg="white")

        try:
            conn = connect_db()
            patients = []
            medecins = []
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT p.id, p.nom, p.prenom FROM patients p")
                patients = cursor.fetchall()
                cursor.execute("""
                    SELECT m.id, u.login
                    FROM medecins m
                    JOIN utilisateurs u ON m.user_id = u.id
                    WHERE u.role = 'medecin'
                """)
                medecins = cursor.fetchall()
                cursor.close()
                conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données : {e}")
            fenetre_rdv.destroy()
            return

        tk.Label(fenetre_rdv, text="Patient :", bg="white").pack(pady=5)
        combo_patient = ttk.Combobox(
            fenetre_rdv,
            values=[f"{p['nom']} {p['prenom']} (ID:{p['id']})" for p in patients],
            state="readonly"
        )
        combo_patient.pack(pady=5)

        tk.Label(fenetre_rdv, text="Médecin :", bg="white").pack(pady=5)
        combo_medecin = ttk.Combobox(
            fenetre_rdv,
            values=[f"{m['login']} (ID:{m['id']})" for m in medecins],
            state="readonly"
        )
        combo_medecin.pack(pady=5)

        tk.Label(fenetre_rdv, text="Date (YYYY-MM-DD HH:MM):", bg="white").pack(pady=5)
        entry_date = tk.Entry(fenetre_rdv)
        entry_date.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M'))
        entry_date.pack(pady=5)

        tk.Label(fenetre_rdv, text="Durée (en minutes) :", bg="white").pack(pady=5)
        entry_duree = tk.Entry(fenetre_rdv)
        entry_duree.pack(pady=5)

        tk.Label(fenetre_rdv, text="Statut :", bg="white").pack(pady=5)
        combo_statut = ttk.Combobox(fenetre_rdv, values=["prévu", "terminé", "annulé"], state="readonly")
        combo_statut.current(0)
        combo_statut.pack(pady=5)

        def enregistrer_rdv():
            nom_patient = combo_patient.get()
            nom_medecin = combo_medecin.get()
            date_rdv = entry_date.get()
            duree = entry_duree.get()
            statut = combo_statut.get()

            patient_idx = combo_patient.current()
            medecin_idx = combo_medecin.current()

            if not (nom_patient and nom_medecin and date_rdv and duree and statut):
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
                return

            if patient_idx == -1 or medecin_idx == -1:
                messagebox.showerror("Erreur", "Sélectionnez un patient et un médecin dans la liste.")
                return

            patient_id = patients[patient_idx]['id']
            medecin_id = medecins[medecin_idx]['id']

            try:
                datetime.strptime(date_rdv, '%Y-%m-%d %H:%M')
            except ValueError:
                messagebox.showerror("Erreur", "Le format de la date est invalide (attendu YYYY-MM-DD HH:MM).")
                return

            if not duree.isdigit() or int(duree) <= 0:
                messagebox.showerror("Erreur", "La durée doit être un nombre entier positif.")
                return

            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                query = "INSERT INTO rendezvous (patient_id, medecin_id, date_rdv, duree, statut) VALUES (%s, %s, %s, %s, %s)"
                try:
                    cursor.execute(query, (patient_id, medecin_id, date_rdv, int(duree), statut))
                    conn.commit()
                    messagebox.showinfo("Succès", "Rendez-vous enregistré avec succès.")
                    fenetre_rdv.destroy()
                    self.afficher_rendezvous()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(fenetre_rdv, text="Enregistrer", bg="#0984e3", fg="white", command=enregistrer_rdv).pack(pady=20)

    def afficher_formulaire_patient(self, patient=None):
        fenetre = tk.Toplevel(self)
        fenetre.title("Ajouter un patient" if patient is None else "Modifier le patient")
        fenetre.geometry("400x400")
        fenetre.configure(bg="white")

        # Liste déroulante des utilisateurs patients
        conn = connect_db()
        utilisateurs = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, login FROM utilisateurs WHERE role = 'patient'")
            utilisateurs = cursor.fetchall()
            cursor.close()
            conn.close()
        user_choices = [f"{u['login']} (ID:{u['id']})" for u in utilisateurs]

        tk.Label(fenetre, text="Utilisateur Patient", bg="white").pack(pady=5)
        combo_user = ttk.Combobox(fenetre, values=user_choices, state="readonly")
        combo_user.pack(pady=5)

        labels = ["Nom", "Prénom", "Date de naissance (YYYY-MM-DD)", "Groupe sanguin", "Assurance"]
        entries = {}
        for label in labels:
            tk.Label(fenetre, text=label, bg="white").pack(pady=5)
            entry = tk.Entry(fenetre)
            entry.pack(pady=5)
            entries[label] = entry

        # Pré-remplir si modification
        if patient:
            for idx, u in enumerate(utilisateurs):
                if u['id'] == patient['user_id']:
                    combo_user.current(idx)
                    break
            entries["Nom"].insert(0, patient['nom'])
            entries["Prénom"].insert(0, patient['prenom'])
            entries["Date de naissance (YYYY-MM-DD)"].insert(0, patient['date_naissance'])
            entries["Groupe sanguin"].insert(0, patient['groupe_sanguin'])
            entries["Assurance"].insert(0, patient['assurance'])

        def enregistrer():
            idx = combo_user.current()
            if idx == -1:
                messagebox.showerror("Erreur", "Sélectionnez un utilisateur patient.")
                return
            user_id = utilisateurs[idx]['id']
            nom = entries["Nom"].get()
            prenom = entries["Prénom"].get()
            date_naissance = entries["Date de naissance (YYYY-MM-DD)"].get()
            groupe_sanguin = entries["Groupe sanguin"].get()
            assurance = entries["Assurance"].get()

            if not (nom and prenom and date_naissance):
                messagebox.showerror("Erreur", "Nom, prénom et date de naissance sont obligatoires.")
                return

            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    if patient:
                        cursor.execute(
                            "UPDATE patients SET nom=%s, prenom=%s, date_naissance=%s, groupe_sanguin=%s, assurance=%s, user_id=%s WHERE id=%s",
                            (nom, prenom, date_naissance, groupe_sanguin, assurance, user_id, patient['id'])
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO patients (user_id, nom, prenom, date_naissance, groupe_sanguin, assurance) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user_id, nom, prenom, date_naissance, groupe_sanguin, assurance)
                        )
                    conn.commit()
                    messagebox.showinfo("Succès", "Patient enregistré avec succès.")
                    fenetre.destroy()
                    self.afficher_patients()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(fenetre, text="Enregistrer", bg="#00b894", fg="white", command=enregistrer).pack(pady=20)
        tk.Button(fenetre, text="Voir les antécédents", bg="#636e72", fg="white",
                  command=lambda: self.afficher_antecedents_patient(patient['id'] if patient else None, fenetre)
        ).pack(pady=10)

    def afficher_antecedents_patient(self, patient_id, parent_fenetre):
        if not patient_id:
            messagebox.showerror("Erreur", "Veuillez d'abord enregistrer le patient avant d'ajouter des antécédents.")
            return

        fenetre_ant = tk.Toplevel(parent_fenetre)
        fenetre_ant.title("Antécédents médicaux")
        fenetre_ant.geometry("500x400")
        fenetre_ant.configure(bg="white")

        # Liste des antécédents
        tree = ttk.Treeview(fenetre_ant, columns=("Date", "Description"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Description", text="Description")
        tree.pack(expand=True, fill=tk.BOTH, pady=10)

        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT date_ajout, description FROM antecedents WHERE patient_id=%s ORDER BY date_ajout DESC", (patient_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(row['date_ajout'], row['description']))
            cursor.close()
            conn.close()

        # Formulaire d'ajout
        tk.Label(fenetre_ant, text="Nouvel antécédent :", bg="white").pack(pady=5)
        entry_desc = tk.Entry(fenetre_ant, width=50)
        entry_desc.pack(pady=5)

        def ajouter_ant():
            desc = entry_desc.get()
            if not desc:
                messagebox.showerror("Erreur", "Description obligatoire.")
                return
            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO antecedents (patient_id, description, date_ajout) VALUES (%s, %s, CURDATE())",
                        (patient_id, desc)
                    )
                    conn.commit()
                    tree.insert("", tk.END, values=(datetime.now().strftime('%Y-%m-%d'), desc))
                    entry_desc.delete(0, tk.END)
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de l'ajout : {e}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(fenetre_ant, text="Ajouter", bg="#00b894", fg="white", command=ajouter_ant).pack(pady=10)

    def afficher_formulaire_rdv_modification(self, rdv_values):
        fenetre_rdv = tk.Toplevel(self)
        fenetre_rdv.title("Modifier le Rendez-vous")
        fenetre_rdv.geometry("400x450")
        fenetre_rdv.configure(bg="white")

        rdv_id, patient_nom, medecin_login, date_rdv, duree, statut = rdv_values

        conn = connect_db()
        patients = []
        medecins = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT p.id, p.nom, p.prenom FROM patients p")
            patients = cursor.fetchall()
            cursor.execute("""
                SELECT m.id, u.login
                FROM medecins m
                JOIN utilisateurs u ON m.user_id = u.id
                WHERE u.role = 'medecin'
            """)
            medecins = cursor.fetchall()
            cursor.close()
            conn.close()

        tk.Label(fenetre_rdv, text="Patient :", bg="white").pack(pady=5)
        combo_patient = ttk.Combobox(
            fenetre_rdv,
            values=[f"{p['nom']} {p['prenom']} (ID:{p['id']})" for p in patients],
            state="readonly"
        )
        combo_patient.pack(pady=5)
        combo_patient.set(patient_nom)  # Pré-remplir le champ patient

        tk.Label(fenetre_rdv, text="Médecin :", bg="white").pack(pady=5)
        combo_medecin = ttk.Combobox(fenetre_rdv, values=[f"{m['login']} (ID:{m['id']})" for m in medecins], state="readonly")
        combo_medecin.pack(pady=5)
        combo_medecin.set(medecin_login)  # Pré-remplir le champ médecin

        tk.Label(fenetre_rdv, text="Date (YYYY-MM-DD HH:MM):", bg="white").pack(pady=5)
        entry_date = tk.Entry(fenetre_rdv)
        entry_date.insert(0, date_rdv)
        entry_date.pack(pady=5)

        tk.Label(fenetre_rdv, text="Durée (en minutes) :", bg="white").pack(pady=5)
        entry_duree = tk.Entry(fenetre_rdv)
        entry_duree.insert(0, duree)
        entry_duree.pack(pady=5)

        tk.Label(fenetre_rdv, text="Statut :", bg="white").pack(pady=5)
        combo_statut = ttk.Combobox(fenetre_rdv, values=["prévu", "terminé", "annulé"], state="readonly")
        combo_statut.current(0 if statut == "prévu" else 1 if statut == "terminé" else 2)
        combo_statut.pack(pady=5)

        def enregistrer_modif():
            nouvelle_date = entry_date.get()
            nouvelle_duree = entry_duree.get()
            nouveau_statut = combo_statut.get()

            if not (nouvelle_date and nouvelle_duree and nouveau_statut):
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
                return

            try:
                datetime.strptime(nouvelle_date, '%Y-%m-%d %H:%M')
            except ValueError:
                try:
                    datetime.strptime(nouvelle_date, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    messagebox.showerror("Erreur", "Le format de la date est invalide (attendu YYYY-MM-DD HH:MM ou YYYY-MM-DD HH:MM:SS).")
                    return

            if not nouvelle_duree.isdigit() or int(nouvelle_duree) <= 0:
                messagebox.showerror("Erreur", "La durée doit être un nombre entier positif.")
                return

            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "UPDATE rendezvous SET date_rdv=%s, duree=%s, statut=%s WHERE id=%s",
                        (nouvelle_date, int(nouvelle_duree), nouveau_statut, rdv_id)
                    )
                    conn.commit()
                    messagebox.showinfo("Succès", "Rendez-vous modifié avec succès.")
                    fenetre_rdv.destroy()
                    self.afficher_rendezvous()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la modification : {e}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(fenetre_rdv, text="Enregistrer", bg="#0984e3", fg="white", command=enregistrer_modif).pack(pady=20)

    def modifier_patient(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un patient à modifier.")
            return
        values = self.tree.item(item, "values")
        # Récupère l'id du patient sélectionné
        patient_id = values[0]
        # Récupère les infos du patient depuis la base
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            patient = cursor.fetchone()
            cursor.close()
            conn.close()
            if patient:
                self.afficher_formulaire_patient(patient)

    def supprimer_patient(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un patient à supprimer.")
            return
        patient_id = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce patient ?"):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
                    conn.commit()
                    messagebox.showinfo("Succès", "Patient supprimé.")
                    self.afficher_patients()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")
                finally:
                    cursor.close()
                    conn.close()
