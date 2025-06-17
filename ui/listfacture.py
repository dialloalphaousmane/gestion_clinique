import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

class ListeFacturesPage(tk.Toplevel):
    def __init__(self, master, db_conn):
        super().__init__(master)
        self.db = db_conn
        self.title("Liste des factures")
        self.geometry("600x400")

        # Colonnes sans 'statut' et avec 'prix' au lieu de montant_total
        columns = ("id", "patient", "date_facture", "prix")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)

        for col, width, anchor in zip(columns, [40, 150, 120, 80], [tk.CENTER, tk.W, tk.CENTER, tk.E]):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor=anchor)

        self.charger_factures()

        ttk.Button(self, text="Générer reçu PDF", command=self.generer_recu).pack(pady=10)

    def charger_factures(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                SELECT f.id, p.nom, p.prenom, f.date_facture, f.prix
                FROM factures f
                JOIN rendezvous r ON f.rendez_vous_id = r.id
                JOIN patients p ON r.patient_id = p.id
                ORDER BY f.date_facture DESC
            """)
            factures = cursor.fetchall()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for f in factures:
                patient = f"{f[1]} {f[2]}"
                date_fact = f[3].strftime("%Y-%m-%d") if isinstance(f[3], datetime) else str(f[3])
                prix = f"{f[4]:.2f}"
                self.tree.insert("", tk.END, values=(f[0], patient, date_fact, prix))

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des factures : {e}")

    def generer_recu(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture.")
            return
        facture_id = self.tree.item(selected[0])['values'][0]
        self.creer_pdf_recu(facture_id)

    def creer_pdf_recu(self, facture_id):
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT f.id, p.nom, p.prenom, f.date_facture, f.prix
            FROM factures f
            JOIN rendezvous r ON f.rendez_vous_id = r.id
            JOIN patients p ON r.patient_id = p.id
            WHERE f.id = %s
        """, (facture_id,))
        facture = cursor.fetchone()

        if not facture:
            messagebox.showerror("Erreur", "Facture non trouvée.")
            return

        filename = f"recu_facture_{facture_id}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Reçu de Facturation")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Facture ID: {facture[0]}")
        c.drawString(50, height - 120, f"Patient: {facture[1]} {facture[2]}")
        date_str = facture[3].strftime("%d/%m/%Y") if isinstance(facture[3], datetime) else str(facture[3])
        c.drawString(50, height - 140, f"Date facture: {date_str}")
        c.drawString(50, height - 160, f"Prix: {facture[4]:.2f} GNF")

        c.drawString(50, height - 200, "Merci pour votre confiance.")
        c.showPage()
        c.save()

        messagebox.showinfo("Succès", f"Reçu PDF généré : {os.path.abspath(filename)}")
