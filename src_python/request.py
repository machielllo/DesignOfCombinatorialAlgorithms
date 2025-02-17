class Request:
    def __init__(self, request_type, customer_id = None, locker_id = None, charger_id = None):
        self.request_type = request_type
        self.customer_id = customer_id
        self.locker_id = locker_id
        self.charger_id = charger_id
    