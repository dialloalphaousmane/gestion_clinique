import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

class FacturationPage(tk.Toplevel):
    def __init__(self, master, db_conn):
        super().__init__(master)
        self.db = db_conn
        self.title("Facturation")
        self.geometry("400x250")

        # --- Widgets ---
        ttk.Label(self, text="Rendez-vous :").pack(pady=5)
        self.rdv_combobox = ttk.Combobox(self, width=40, state="readonly")
        self.rdv_combobox.pack(pady=5)
        self.remplir_rendez_vous()

        ttk.Label(self, text="Prix (consultation) :").pack(pady=5)
        self.prix_entry = ttk.Entry(self)
        self.prix_entry.pack(pady=5)

        ttk.Button(self, text="Enregistrer la facture", command=self.enregistrer_facture).pack(pady=15)

    def remplir_rendez_vous(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                SELECT r.id, p.nom, p.prenom, r.date_rdv 
                FROM rendezvous r 
                JOIN patients p ON r.patient_id = p.id 
                WHERE r.statut = 'Prévu'
            """)
            self.rendez_vous_liste = cursor.fetchall()
            self.rdv_combobox['values'] = [f"{r[1]} {r[2]} - {r[3]}" for r in self.rendez_vous_liste]
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement : {e}")

    def enregistrer_facture(self):
        index = self.rdv_combobox.current()
        if index == -1:
            messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous.")
            return

        rdv_id = self.rendez_vous_liste[index][0]
        prix = self.prix_entry.get()

        if not prix.strip():
            messagebox.showwarning("Attention", "Veuillez saisir un prix.")
            return

        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO factures (rendez_vous_id, prix, date_facture)
                VALUES (%s, %s, %s)
            """, (rdv_id, float(prix), str(date.today())))
            self.db.commit()
            messagebox.showinfo("Succès", "Facture enregistrée avec succès.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
