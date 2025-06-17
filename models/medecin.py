class Medecin:
    def _init_(self, id, username, email, specialite):
        self.id = id
        self.username = username
        self.email = email
        self.specialite = specialite

    def _repr_(self):
        return f"<Médecin {self.username} - {self.specialite}>"