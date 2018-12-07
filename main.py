import os
from PyQt5 import QtWidgets, QtCore, uic
from blockchain import Blockchain
import wallets
from vote import Vote


class MainForm(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/mainwindow.ui", self)
        ws = wallets.Wallets()
        w = ws.create_wallet()
        self.bc = Blockchain(w)
        self.create_vote_button.clicked.connect(self.create_vote)
        self.wallet_create_button.clicked.connect(self.create_wallet)
        if len(self.bc.votes) > 1:
            for vot in self.bc.votes.keys():
                self.add_vote_on_table(vot)

    @QtCore.pyqtSlot()
    def create_vote(self):
        nvf = NewVoteForm(master=self)
        self.close()
        nvf.exec()
        pass

    @QtCore.pyqtSlot()
    def create_wallet(self):
        wf = WalletForm(self)
        self.close()
        wf.exec()

    def add_vote_on_table(self, name):
        vote_name = name
        vote_button = QtWidgets.QPushButton("Проголосовать")
        vote_button.clicked.connect(lambda: self.do_vote(name))
        end_vote_button = QtWidgets.QPushButton("Завершить")
        end_vote_button.clicked.connect(lambda: self.end_vote(name))
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row + 1)
        self.tableWidget.setCellWidget(row, 0, QtWidgets.QLabel(vote_name))
        self.tableWidget.setCellWidget(row, 1, vote_button)
        self.tableWidget.setCellWidget(row, 2, end_vote_button)
        pass

    @QtCore.pyqtSlot()
    def do_vote(self, name):
        vote = None
        for nm in self.bc.votes.keys():
            if name == nm:
                vote = self.bc.votes[name]
                break
        if vote is not None:
            vf = VoteForm(vote, self)
            self.close()
            vf.exec()
        pass

    @QtCore.pyqtSlot()
    def end_vote(self, name):
        vote = None
        for nm in self.bc.votes.keys():
            if name == nm:
                vote = self.bc.votes[name]
                break
        if vote is not None:
            vr = VoteResults(self, vote)
            self.close()
            vr.exec()
        pass
    pass


class NewVoteForm(QtWidgets.QDialog):
    def __init__(self, master=None):
        super().__init__()
        self.master = master
        uic.loadUi("gui/new_vote_form.ui", self)

        self.cancel_button.clicked.connect(self.on_exit)
        self.create_vote_button.clicked.connect(self.create_vote)
        pass

    @QtCore.pyqtSlot()
    def on_exit(self):
        self.close()
        self.master.show()
        pass

    @QtCore.pyqtSlot()
    def create_vote(self):
        name = self.vote_name_lineEdit.text()
        text = self.vote_text_plainTextEdit.toPlainText()
        vars_text = self.vars_plainTextEdit.toPlainText()
        vars = vars_text.split(sep="\n")
        self.master.bc.add_vote(name, text, vars)
        self.vote_name_lineEdit.setText("")
        self.vote_text_plainTextEdit.setPlainText("")
        self.vars_plainTextEdit.setPlainText("")
        self.master.add_vote_on_table(name)
        pass
    pass


class VoteForm(QtWidgets.QDialog):
    def __init__(self, vote, master=None):
        super().__init__()
        self.master = master
        uic.loadUi("gui/vote_form.ui", self)
        self.vote = vote
        self.vote_name_label.setText(self.vote.name)
        self.vote_text_label.setText(self.vote.text)
        self.cancel_button.clicked.connect(self.on_exit)
        self.vote_button.clicked.connect(self.do_vote)
        self.create_wallet_button.clicked.connect(self.create_wallet)
        self.r_buttons = []
        for name, wal in self.vote.vars.items():
            # print(wal)
            radio_button = QtWidgets.QRadioButton(name)
            radio_button.setCheckable(True)
            self.r_buttons.append(radio_button)
            self.vars.addWidget(radio_button)

    @QtCore.pyqtSlot()
    def create_wallet(self):
        wf = WalletForm(self.master)
        self.close()
        wf.exec()
        pass

    @QtCore.pyqtSlot()
    def on_exit(self):
        self.close()
        self.master.show()
        pass

    @QtCore.pyqtSlot()
    def do_vote(self):
        for rb in self.r_buttons:
            if rb.isChecked():
                pk = self.pubkey_lineEdit.text()
                ws = wallets.deserialize()
                address_from = ws.get_wallet_by_pub_key(pk)
                print("On Form: " + str(address_from))
                try:
                    self.master.bc.do_vote(address_from, self.vote.vars[rb.text()])  # wallet address
                except Exception as e:
                    print(e)
                    raise Exception
        self.pubkey_lineEdit.setText("")


class WalletForm(QtWidgets.QDialog):
    def __init__(self, master):
        super().__init__()
        self.master = master
        uic.loadUi("gui/new_wallet_form.ui", self)
        self.create_wallet_button.clicked.connect(self.create_wallet)
        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.on_exit)

    @QtCore.pyqtSlot()
    def on_exit(self):
        self.close()
        self.master.show()
        pass

    @QtCore.pyqtSlot()
    def create_wallet(self):
        ws = wallets.deserialize()
        address = ws.create_wallet()
        wallet = ws.get_wallet(address)
        self.private_key_plainTextEdit.setPlainText(str(wallet.private))
        self.public_key_plainTextEdit.setPlainText(str(wallet.public))
        self.master.bc.add_block(address)

    @QtCore.pyqtSlot()
    def on_exit(self):
        self.close()
        self.master.show()
        pass

    @QtCore.pyqtSlot()
    def save(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home/myScripts')
        name = fname.split(sep="/")
        self.cname = name[-1]
        with open(fname, mode="w") as f:
            try:
                f.write(self.private_key_plainTextEdit.toPlainText() + "\n" +
                        self.public_key_plainTextEdit.toPlainText())
            except Exception as e:
                print(e)
                pass
            pass
        pass
    pass


class VoteResults(QtWidgets.QDialog):
    def __init__(self, master, vote):
        super().__init__()
        self.master = master
        uic.loadUi("gui/vote_results_form.ui", self)
        self.vote_name_label.setText(vote.name)
        self.vote_text_label.setText(vote.text)
        for name, wal in vote.vars.items():
            address = wal
            result = self.master.bc.get_balance(address)
            self.vars.addWidget(QtWidgets.QLabel(name + " ======= " + str(result)))
        winner = self.master.bc.end_vote(vote.name)
        self.winner_lineEdit.setText(str(winner[1]))
        self.cancel_button.clicked.connect(self.on_exit)

    @QtCore.pyqtSlot()
    def on_exit(self):
        self.close()
        self.master.show()
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainForm()
    window.show()
    sys.exit(app.exec_())