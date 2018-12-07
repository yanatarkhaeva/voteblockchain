import wallets as ws


class Vote:
    def __init__(self, name, text, vars):
        self.name = name
        self.text = text
        self.vars = {}
        for v in vars:
            w = ws.deserialize()
            wallet_address = w.create_wallet()
            self.vars[v] = wallet_address
        self.result = None
