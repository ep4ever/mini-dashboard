#!/usr/bin/env python

import os
import sys
import json
import MySQLdb
import threading
from tkinter import Label, Tk, PhotoImage


class Dashboard:
    def __init__(self):
        self.config: dict = self._readconfig()
        self.cnx: dict = self._readsources()
        self.win: Tk = self._buildwin()

    def show(self):
        self._refresh()
        self.win.mainloop()

    def _refresh(self):
        self.refreshtm = threading.Timer(10.0, self._refresh)
        self.refreshtm.start()

        datas = self._getdatas()

        for field in self.config.get('fields', []):
            ident = field.get('field')
            fieldctl: dict = self._getfieldctl(ident)
            suffix = field.get('suffix')
            data = datas.get(ident, 0)
            lbl: Label = fieldctl.get('text', '')
            if field.get('format') == 'percentage':
                lbl.configure(text=f"{data:.0%}")
            elif field.get('format') == 'number':
                lbl.configure(text=f"{data:.2f} {suffix}")
            else:
                lbl.configure(text=f"{data} {suffix}")

    def _buildwin(self) -> Tk:
        fieldcount = len(self.config.get('fields', []))

        win = Tk()
        win.configure(bg='')
        win.attributes('-topmost', True)
        win.resizable(width=False, height=False)
        win.iconphoto(False, PhotoImage(file="icon.png"))
        win.title('Dashboard')
        win.rowconfigure(fieldcount, minsize=8)
        win.columnconfigure([0, 1], minsize=60)
        self.refreshtm: threading.Timer
        win.protocol("WM_DELETE_WINDOW", self._terminate)
        idx = 0
        self.fields = []
        for field in self.config.get('fields', []):
            fieldctl: dict = {}
            fieldctl['name'] = ''
            fieldctl = {
                "name": field.get('field'),
                "text": self._addentry(win, field.get('label'), idx)
            }
            self.fields.append(fieldctl)

            idx += 1
        return win

    def _terminate(self):
        self.win.destroy()
        self.refreshtm.cancel()
        self.refreshtm.join()
        sys.exit(0)

    def _getfieldctl(self, fieldname) -> dict:
        for field in self.fields:
            if field.get('name') == fieldname:
                return field

        return {}

    def _readconfig(self) -> dict:
        sd = os.path.dirname(os.path.abspath(sys.argv[0]))
        config_path = os.path.join(sd, 'settings.json')
        fjson = open(config_path, 'r')
        jsonstream = fjson.read()
        config = json.loads(jsonstream)
        fjson.close()
        return config

    def _readsources(self) -> dict:
        cnx = {}
        for source in self.config.get('sources', []):
            cnx[source.get('name')] = MySQLdb.connect(
                user=source.get('dbuser'),
                password=source.get('dbpwd'),
                host=source.get('dbhost'),
                database=source.get('dbname'),
            )
        return cnx

    def _getdatas(self) -> dict:
        retval = {}
        for query in self.config.get('queries', []):
            src = query.get('source')
            cursor = self.cnx[src].cursor()
            cursor.execute(query.get('query'))
            records = cursor.fetchall()

            for r in records:
                retval[r[0]] = r[1]

            self.cnx[src].commit()

        return retval

    def _addentry(self, win, name, rowpos):
        lbl = Label(win, text=name, anchor='w', justify='left', width=8)
        lbl.grid(row=rowpos, column=0, padx=2, pady=2)
        lbl.config(bg='black', fg='yellow')
        txt = Label(win, text='...', anchor='e', justify='right', width=8)
        txt.grid(row=rowpos, column=1, padx=2, pady=2)
        txt.config(bg='black', fg='yellow')

        return txt


if __name__ == '__main__':
    print('starting app')
    dashboard = Dashboard()
    dashboard.show()
