class Patient:
    def _init_(self, id, username, email, adresse=None, telephone=None):
        self.id = id
        self.username = username
        self.email = email
        self.adresse = adresse
        self.telephone = telephone

    def _repr_(self):
        return f"<Patient {self.username}>"