from db.connexion import connect_db

def enregistrer_consultation(patient_id, medecin_id, diagnostic, prescription, date_consultation):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consultation (patient_id, medecin_id, diagnostic, prescription, date_consultation)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, medecin_id, diagnostic, prescription, date_consultation))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur enregistrement consultation :", e)
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def lister_consultations():
    conn = connect_db()
    consultations = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.id, p.username AS patient, m.username AS medecin,
                       c.diagnostic, c.prescription, c.date_consultation
                FROM consultation c
                JOIN patient p ON c.patient_id = p.id
                JOIN medecin m ON c.medecin_id = m.id
                ORDER BY c.date_consultation DESC
            """)
            consultations = cursor.fetchall()
        except Exception as e:
            print("Erreur récupération consultations :", e)
        finally:
            cursor.close()
            conn.close()
    return consultations