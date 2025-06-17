class Consultation:
    def _init_(self, id, rendezvous_id, diagnostic, prescription):
        self.id = id
        self.rendezvous_id = rendezvous_id
        self.diagnostic = diagnostic
        self.prescription = prescription

    def _repr_(self):
        return f"<Consultation RDV {self.rendezvous_id}>"