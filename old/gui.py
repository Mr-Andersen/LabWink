#!/usr/bin/python3
# PyQTGraph
import tkinter as tk


class ExecField(tk.Frame):
    def __init__(self, master=None, log_file=None, frame_kw=dict(),
                 entry_kw=dict(), button_kw=dict(), **kwargs):
        self.log_file = log_file
        for k in kwargs.keys():
            if k.startswith('f__'):
                frame_kw[k[3:]] = kwargs[k]
            elif k.startswith('e__'):
                entry_kw[k[3:]] = kwargs[k]
            elif k.startswith('b__'):
                button_kw[k[3:]] = kwargs[k]
        frame_kw_default = dict()
        frame_kw_default.update(frame_kw)
        entry_kw_default = dict(width=32, font='Courier 16')
        entry_kw_default.update(entry_kw)
        button_kw_default = dict(font='Courier 16', text='Go')
        button_kw_default.update(button_kw)
        tk.Frame.__init__(self, master, **frame_kw_default)
        self.entry = tk.Entry(self, **entry_kw_default)
        self.entry.bind('<Return>', self.exec)
        self.button = tk.Button(self, **button_kw_default)
        self.button.bind('<Button-1>', self.exec)
        self.entry.grid(row=0, column=0)
        self.button.grid(row=0, column=1)

    def exec(self, event=None):
        s = self.entry.get()
        try:
            exec(s)
            if self.log_file is not None:
                self.log_file.write('%s\n' % s)
            self.entry.delete(0, len(s))
        except Exception as e:
            if self.log_file is not None:
                self.log_file.write('# %s (failed with error: %s)\n' %
                                    (s, str(e)))
            raise e

    def destroy(self):
        if self.log_file is not None:
            self.log_file.close()
        tk.Frame.destroy(self)


root = tk.Tk()

exec_field = ExecField(root, open('gui_log.txt', 'at'))
exec_field.grid(row=0, column=0)

tk.mainloop()
