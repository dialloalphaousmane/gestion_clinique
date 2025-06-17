from datetime import datetime

class RendezVous:
    def _init_(self, id, patient_id, medecin_id, date_rdv, heure):
        self.id = id
        self.patient_id = patient_id
        self.medecin_id = medecin_id
        self.date_rdv = date_rdv  # format: YYYY-MM-DD
        self.heure = heure        # format: HH:MM

    def _repr_(self):
        return f"<RDV Patient {self.patient_id} avec Médecin {self.medecin_id} le {self.date_rdv} à {self.heure}>"