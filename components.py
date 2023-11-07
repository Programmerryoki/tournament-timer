import tkinter as tk
import tkinter.ttk as ttk
from threading import Timer


class timer_button(tk.Frame):
    court = 1
    STATE = ['Not In Use','WarmUp','InGame']
    COLOR_STATE = ['gray90','light goldenrod','brown1']
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        row = 0
        # Court Number
        self.court_no = timer_button.court
        timer_button.court += 1
        self.label_court_no = tk.Label(self, text=f'Court {self.court_no:02}', font=("Arial", 15, 'underline'))
        self.label_court_no.grid(column=1,row=row,columnspan=1,rowspan=1)
        self.var_match_no = tk.StringVar()
        self.label_match_no = tk.Label(self, textvariable=self.var_match_no)
        self.label_match_no.grid(column=2, row=row, columnspan=1, rowspan=1)
        self.label_state = tk.Label(self, text='Not In Use', font=("Arial", 10, 'bold'))
        self.label_state.grid(column=3,row=row,columnspan=1,rowspan=1)
        row += 1
        # Player names
        self.var_p1 = tk.StringVar()
        self.var_p2 = tk.StringVar()
        self.match = Match(self.var_p1, self.var_p2, self.var_match_no)
        self.label_p1 = tk.Label(self, textvariable=self.var_p1)
        self.label_p1.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        self.label_vs = tk.Label(self, text='VS', font=('Arial', 7))
        self.label_vs.grid(row=row, column=2, rowspan=1, columnspan=1)
        row += 1
        self.label_p2 = tk.Label(self, textvariable=self.var_p2)
        self.label_p2.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        # Time label
        self.var_time = tk.StringVar(value='000:00')
        self.label_time = tk.Label(self, textvariable=self.var_time, font=("Arial", 25))
        self.label_time.grid(column=1,row=row,columnspan=3,rowspan=1)
        row += 1
        # Buttons
        self.btn_start = ttk.Button(master=self, text='Start', command=self.start_button)
        self.btn_start.grid(column=1,row=row,columnspan=1,rowspan=1)
        self.btn_edit = ttk.Button(master=self, text='Edit', command=self.edit_button)
        self.btn_edit.grid(column=2, row=row, columnspan=1, rowspan=1)
        self.btn_reset = ttk.Button(master=self, text='Reset', command=self.reset_button)
        self.btn_reset.grid(column=3, row=row, columnspan=1, rowspan=1)
        row += 1
        # Labels to change BG
        self.labels = [self.label_vs, self.label_p1, self.label_p2, self.label_time,
                       self.label_state, self.label_court_no, self.label_match_no, self]
        # Set Up Time Interval
        self.clock = clock(txtVar=self.var_time)
        self.event = RepeatTimer(1, lambda : self.clock.update(0, self.change_color))
        self.change_state(0)

    def edit_button(self):
        second = tk.Toplevel()
        second.title(f'Court Detail')
        second.protocol("WM_DELETE_WINDOW", self.__callback)
        second.geometry(f'300x300+{self.master.winfo_x()+300}+{self.master.winfo_y()+300}')
        row = 0
        # Match No
        label_match_no = tk.Label(second, text='Match No:')
        label_match_no.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_match_no = tk.Entry(second, textvariable=self.match.match_num)
        entry_match_no.grid(row=row, column=2, rowspan=1, columnspan=1)
        row += 1
        # Players
        label_p1 = tk.Label(second, text='Player 1')
        label_p1.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_p1 = tk.Entry(second, textvariable=self.match.p1)
        entry_p1.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        label_p2 = tk.Label(second, text='Player 2')
        label_p2.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_p2 = tk.Entry(second, textvariable=self.match.p2)
        entry_p2.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        # Close Button
        btn_reset = ttk.Button(second, text='Reset', command=self.clear)
        btn_reset.grid(row=row, column=2, rowspan=1, columnspan=1)
        btn_close = ttk.Button(second, text='Save', command=second.destroy)
        btn_close.grid(row=row, column=3, rowspan=1, columnspan=1)

    def clear(self):
        self.match.p1.set('')
        self.match.p2.set('')
        self.match.match_num.set('')

    def __callback(self):
        pass

    def change_color(self, color):
        for label in self.labels:
            label.config(background=color)

    def change_state(self, state):
        self.config(bg=timer_button.COLOR_STATE[state])
        self.label_state.config(text=timer_button.STATE[state])
        self.change_color(timer_button.COLOR_STATE[state])
        if state == 0:
            self.set_time(0)
            self.btn_start.config(text='Warm Up', command=self.warm_up, state='normal')
            self.btn_reset.config(text='Game', command=self.game)
        elif state == 1:
            self.set_time(2 * 60)
            self.count_down_button()
            self.btn_start.config(text='Warm Up', state='disabled')
            self.btn_reset.config(text='Game', command=self.game)
            self.start_button()
        elif state == 2:
            self.set_time(0)
            self.stop_button()
            self.btn_start.config(text='Game', state='disabled')
            self.btn_reset.config(text='Reset', command=self.reset_button)
            self.start_button()

    def start_button(self):
        self.event.start()

    def stop_button(self):
        self.event.cancel()
        self.event = RepeatTimer(1, lambda : self.clock.update(1, self.change_color))

    def set_time(self, time):
        self.var_time.set(f'{time // 60:03}:{time % 60:02}')

    def reset_button(self):
        self.event.cancel()
        self.change_state(0)

    def count_down_button(self):
        self.event.cancel()
        self.event = RepeatTimer(1, lambda : self.clock.update(-1, self.change_color))

    def game(self):
        self.change_state(2)

    def warm_up(self):
        self.change_state(1)


class clock:
    def __init__(self, txtVar):
        self.txtVar = txtVar
        self.ind = 0

    def update(self, d, color_func=None):
        min, sec = [int(i) for i in self.txtVar.get().split(':')]
        sec += d
        if sec > 59 or sec < 0:
            min += d
            sec = 0 if sec > 59 else 59
        if color_func and (sec < 0 or min < 0):
            color_func(['deep sky blue', 'gray90'][self.ind])
            self.ind = 1 - self.ind
        else:
            string = f'{min:03}:{sec:02}'
            self.txtVar.set(string)


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Match:
    def __init__(self, p1, p2, match_num):
        self.p1 = p1
        self.p2 = p2
        self.match_num = match_num


class queue_timer(tk.Frame):
    def __init__(self, master, del_func, index, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.index = index
        row = 0
        # Player names
        self.var_p1 = tk.StringVar()
        self.var_p2 = tk.StringVar()
        self.var_match_no = tk.StringVar()
        self.match = Match(self.var_p1, self.var_p2, self.var_match_no)
        self.label_match = tk.Label(self, text='Match No:')
        self.label_match.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        self.label_match_no = tk.Label(self, textvariable=self.var_match_no)
        self.label_match_no.grid(column=2, row=row, columnspan=1, rowspan=1)
        row += 1
        self.edit_button()
        self.label_p1 = tk.Label(self, textvariable=self.var_p1)
        self.label_p1.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        self.label_vs = tk.Label(self, text='VS', font=('Arial', 7))
        self.label_vs.grid(row=row, column=2, rowspan=1, columnspan=1)
        row += 1
        self.label_p2 = tk.Label(self, textvariable=self.var_p2)
        self.label_p2.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        # Time label
        self.var_time = tk.StringVar(value='000:00')
        self.label_time = tk.Label(self, textvariable=self.var_time, font=("Arial", 25))
        self.label_time.grid(column=1,row=row,columnspan=3,rowspan=1)
        row += 1
        # Buttons
        self.btn_start = ttk.Button(master=self, text='Reset', command=self.count_down_button)
        self.btn_start.grid(column=1, row=row, columnspan=1, rowspan=1)
        self.btn_edit = ttk.Button(master=self, text='Edit', command=self.edit_button)
        self.btn_edit.grid(column=2, row=row, columnspan=1, rowspan=1)
        self.btn_reset = ttk.Button(master=self, text='Delete', command=lambda : del_func(self.index))
        self.btn_reset.grid(column=3, row=row, columnspan=1, rowspan=1)
        row += 1
        # Labels to change BG
        self.labels = [self.label_vs, self.label_p1, self.label_p2, self.label_time]
        # Set Up Time Interval
        self.clock = clock(txtVar=self.var_time)
        self.event = RepeatTimer(1, lambda : self.clock.update(0, self.change_color))
        self.set_time(5 * 60)
        self.event = RepeatTimer(1, lambda: self.clock.update(-1, self.change_color))
        self.labels = [self.label_vs, self.label_p1, self.label_p2, self.label_time, self.label_match_no,
                       self, self.label_match]

    def edit_button(self):
        second = tk.Toplevel()
        second.title(f'Queue Detail')
        second.protocol("WM_DELETE_WINDOW", self.__callback)
        second.geometry(f'300x300+{self.master.winfo_x()+300}+{self.master.winfo_y()+300}')
        row = 0
        # Match No
        label_match_no = tk.Label(second, text='Match No:')
        label_match_no.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_match_no = tk.Entry(second, textvariable=self.match.match_num)
        entry_match_no.grid(row=row, column=2, rowspan=1, columnspan=1)
        row += 1
        # Players
        label_p1 = tk.Label(second, text='Player 1')
        label_p1.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_p1 = tk.Entry(second, textvariable=self.match.p1)
        entry_p1.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        label_p2 = tk.Label(second, text='Player 2')
        label_p2.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_p2 = tk.Entry(second, textvariable=self.match.p2)
        entry_p2.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        # Close Button
        btn_reset = ttk.Button(second, text='Reset', command=self.clear)
        btn_reset.grid(row=row, column=2, rowspan=1, columnspan=1)
        btn_close = ttk.Button(second, text='Save', command=lambda : self.destroy_window(second))
        btn_close.grid(row=row, column=3, rowspan=1, columnspan=1)

    def destroy_window(self, window):
        window.destroy()
        if not self.event.is_alive():
            self.start_button()

    def change_color(self, color):
        for label in self.labels:
            label.config(background=color)

    def clear(self):
        self.match.p1.set('')
        self.match.p2.set('')

    def __callback(self):
        pass

    def start_button(self):
        self.event.start()

    def set_time(self, time):
        self.var_time.set(f'{time // 60:03}:{time % 60:02}')

    def count_down_button(self):
        self.event.cancel()
        self.set_time(5 * 60)
        self.change_color('white')
        self.event = RepeatTimer(1, lambda : self.clock.update(-1, self.change_color))
        self.start_button()
