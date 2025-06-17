class Utilisateur:
    def _init_(self, id, username, email, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def _repr_(self):
        return f"<Utilisateur {self.username} ({self.role})>"