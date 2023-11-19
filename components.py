import tkinter as tk
import tkinter.ttk as ttk
from threading import Timer
from copy import deepcopy
from math import gcd
from functools import reduce
from database import PlayerDatabase


pd = PlayerDatabase('Player Database11162023.XLSX')
styleID = lambda x: f'{id(x)}.TButton'
WARMUP_TIME = 2 * 60 + 30

class group_select_btn(ttk.Button):
    _order = []
    _groups = {}
    def __init__(self, master, label, group=None, pre=False):
        self.group = group if not group is None else id(self)
        super().__init__(master, style=styleID(self), text=label, command=self.on_click)
        if self.group not in self._groups:
            self._groups[self.group] = []
            if not group is None:
                self._order.append(self.group)
        self._groups[self.group].append((self, False))
        if pre:
            self.on_click()

    def on_click(self):
        for i, [btn, state] in enumerate(self._groups[self.group]):
            state = not state if btn == self else False
            style = ttk.Style()
            style.configure(styleID(btn), background='red' if state else 'white')
            btn.style = style
            self._groups[self.group][i] = (btn, state)

    @classmethod
    def match_number(cls, pre):
        ret = ""
        for group in cls._order:
            for i, [btn, state] in enumerate(cls._groups[group]):
                if state:
                    ret += btn['text']
                    state = False
                    style = ttk.Style()
                    style.configure(styleID(btn), background='white')
                    btn.style = style
                    cls._groups[group][i] = (btn, state)

            if pre[group]:
                btn, state = cls._groups[group][0]
                state = True
                style = ttk.Style()
                style.configure(styleID(btn), background='red')
                btn.style = style
                cls._groups[group][0] = (btn, state)
        return ret


class match_button(tk.Frame):
    def __init__(self, master, label_list, pre, action, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.label_list = label_list
        self.max_row = reduce(lambda x,y: int((x*y) / gcd(x,y)), [len(i) for i in label_list])
        for i, labels in enumerate(label_list):
            row = 0
            rowm = int(self.max_row / len(labels))
            for j,label in enumerate(labels):
                btn = group_select_btn(self, label, group=i, pre=True if pre[i] and j==0 else False)
                btn.grid(column=i, row=j*rowm, columnspan=1, rowspan=rowm, ipady=10*(rowm-1))
                row += 1
        # Players
        self.var_p1 = tk.StringVar()
        self.var_p2 = tk.StringVar()
        label_p1 = tk.Label(self, text='Team 1')
        label_p1.grid(row=row, column=0, rowspan=1, columnspan=len(label_list)//2)
        label_p2 = tk.Label(self, text='Team 2')
        label_p2.grid(row=row, column=-(-len(label_list) // 2), rowspan=1, columnspan=len(label_list) // 2)
        row += 1
        entry_p1 = AutocompleteEntry(self, textvariable=self.var_p1)
        entry_p1.grid(row=row, column=0, rowspan=1, columnspan=len(label_list)//2)
        entry_p2 = AutocompleteEntry(self, textvariable=self.var_p2)
        entry_p2.grid(row=row, column=-(-len(label_list) // 2), rowspan=1, columnspan=len(label_list) // 2)
        call = ttk.Button(self, text='Call', command=lambda : [action(self._construct_match(pre)),self.reset()])
        call.grid(column=i+1, row=0, columnspan=1, rowspan=self.max_row, ipady=(self.max_row-1)*10)
        row += 1
        self.instruction = """
        If you want to add multiple player for doubles, separate players name with a ','.
        Then the name list will show up again, and you can add both players.
        The autocomplete label on edit button is wacky. Please bear with 
        that lol And try not to use it
        Please call Ryoki if the software bugs out / or call at 4088597149
        The link to ppt is https://tinyurl.com/SJSUFall2023
        """
        self.instruction_label = tk.Label(self, text=self.instruction, font=("Arial", 10))
        self.instruction_label.grid(column=i+2, row=0, columnspan=1,
                                    rowspan=self.max_row)

    def _construct_match(self, pre):
        return Match(self.var_p1, self.var_p2, tk.StringVar(value=group_select_btn.match_number(pre)))

    def reset(self):
        self.var_p1.set("")
        self.var_p2.set("")


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
        self.label_state = tk.Label(self, text='Not In Use', font=("Arial", 10, 'bold'))
        self.label_state.grid(column=3,row=row,columnspan=1,rowspan=1)
        row += 1
        # Match No
        self.var_match_no = tk.StringVar()
        self.label_match_no = tk.Label(self, textvariable=self.var_match_no, font=("Arial", 10))
        self.label_match_no.grid(column=2, row=row, columnspan=1, rowspan=1)
        row += 1
        # Player names
        self.var_p1 = tk.StringVar()
        self.var_p2 = tk.StringVar()
        self.match = Match(self.var_p1, self.var_p2, self.var_match_no)
        self.label_p1 = tk.Label(self, textvariable=self.var_p1, font=('Arial', 15))
        self.label_p1.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        self.label_vs = tk.Label(self, text='VS', font=('Arial', 7))
        self.label_vs.grid(row=row, column=2, rowspan=1, columnspan=1)
        row += 1
        self.label_p2 = tk.Label(self, textvariable=self.var_p2, font=('Arial', 15))
        self.label_p2.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        # Time label
        self.var_time = tk.StringVar(value='000:00')
        self.label_time = tk.Label(self, textvariable=self.var_time, font=("Arial", 20))
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
        entry_p1 = AutocompleteEntry(second, textvariable=self.match.p1, window=True)
        entry_p1.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        label_p2 = tk.Label(second, text='Player 2')
        label_p2.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_p2 = AutocompleteEntry(second, textvariable=self.match.p2, window=True)
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
            self.set_time(WARMUP_TIME)
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

    def update_info(self, match):
        self.match.p1.set(match.p1.get())
        self.match.p2.set(match.p2.get())
        self.match.match_num.set(match.match_num.get())


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
    def __init__(self, master, del_func, index, match, minutes, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.index = index
        row = 0
        # Player names
        self.var_p1 = tk.StringVar()
        self.var_p2 = tk.StringVar()
        self.var_match_no = tk.StringVar()
        self.match = Match(self.var_p1, self.var_p2, self.var_match_no)
        self.update_info(match)
        self.label_match = tk.Label(self, text='Match No:')
        self.label_match.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        self.label_match_no = tk.Label(self, textvariable=self.var_match_no, font=("Arial", 10))
        self.label_match_no.grid(column=2, row=row, columnspan=1, rowspan=1)
        row += 1
        self.label_p1 = tk.Label(self, textvariable=self.var_p1, font=('Arial', 15))
        self.label_p1.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        self.label_vs = tk.Label(self, text='VS', font=('Arial', 7))
        self.label_vs.grid(row=row, column=2, rowspan=1, columnspan=1)
        row += 1
        self.label_p2 = tk.Label(self, textvariable=self.var_p2, font=('Arial', 15))
        self.label_p2.grid(row=row, column=1, rowspan=1, columnspan=3)
        row += 1
        # Time label
        self.var_time = tk.StringVar(value='000:00')
        self.label_time = tk.Label(self, textvariable=self.var_time, font=("Arial", 20))
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
        self.default_time = minutes * 60
        # Set Up Time Interval
        self.clock = clock(txtVar=self.var_time)
        self.event = RepeatTimer(1, lambda: self.clock.update(0, self.change_color))
        self.set_time(self.default_time)
        self.event = RepeatTimer(1, lambda: self.clock.update(-1, self.change_color))
        self.labels = [self.label_vs, self.label_p1, self.label_p2, self.label_time, self.label_match_no,
                       self, self.label_match]
        self.start_button()

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
        entry_p1 = AutocompleteEntry(second, textvariable=self.match.p1, window=True)
        entry_p1.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        label_p2 = tk.Label(second, text='Player 2')
        label_p2.grid(row=row, column=1, rowspan=1, columnspan=1)
        row += 1
        entry_p2 = AutocompleteEntry(second, textvariable=self.match.p2, window=True)
        entry_p2.grid(row=row, column=1, rowspan=1, columnspan=5)
        row += 1
        # Close Button
        btn_reset = ttk.Button(second, text='Clear', command=self.clear)
        btn_reset.grid(row=row, column=2, rowspan=1, columnspan=1)
        btn_close = ttk.Button(second, text='Save', command=lambda : self.destroy_window(second))
        btn_close.grid(row=row, column=3, rowspan=1, columnspan=1)

    def clear(self):
        self.match.p1.set('')
        self.match.p2.set('')
        self.match.match_num.set('')

    def destroy_window(self, window):
        window.destroy()
        if not self.event.is_alive():
            self.start_button()

    def change_color(self, color):
        for label in self.labels:
            label.config(background=color)

    def __callback(self):
        pass

    def start_button(self):
        self.event.start()

    def set_time(self, time):
        self.var_time.set(f'{time // 60:03}:{time % 60:02}')

    def count_down_button(self):
        self.event.cancel()
        self.set_time(self.default_time)
        self.change_color('white')
        self.event = RepeatTimer(1, lambda : self.clock.update(-1, self.change_color))
        self.start_button()

    def update_info(self, match):
        self.match.p1.set(match.p1.get())
        self.match.p2.set(match.p2.get())
        self.match.match_num.set(match.match_num.get())


class AutocompleteEntry(tk.Entry):
    def __init__(self, master, window=False, *args, **kwargs):

        super().__init__(master, *args, **kwargs)
        self.master = master
        self.window = window
        self.var = kwargs["textvariable"]

        self.var.trace_variable('w', self.changed)

        self.lb_up = False

    def changed(self, name, index, mode):

        if self.var.get() == '':
            if self.lb:
                self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    lbx = self.winfo_x() + (self.master.winfo_x() if not self.window else self.master.winfo_rootx())
                    lby = self.winfo_y() + (self.master.winfo_y() if not self.window else self.master.winfo_rooty()) + self.winfo_height()
                    self.lb.place(x=lbx, y=lby)
                    self.lb_up = True

                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            name = self.var.get()
            if "," in name:
                name = name[:name.index(",")] + "," + self.lb.get(tk.ACTIVE)
            else:
                name = self.lb.get(tk.ACTIVE)
            self.var.set(name)
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)
            self.focus()


    def comparison(self):
        name = self.var.get()
        if "," in name:
            name = name[name.index(",")+1:]
        return pd.search_name(name)
