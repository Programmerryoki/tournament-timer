import tkinter as tk
import tkinter.ttk as ttk
from components import timer_button, queue_timer


root = tk.Tk()
root.title('SJSU Spring 2023 SmashOff')
root.geometry('1000x800')
# root.resizable(0,0)

def __callback():
    pass

def close(window):
    second = tk.Toplevel()
    second.title('Confirm')
    second.protocol("WM_DELETE_WINDOW", __callback)
    label = tk.Label(second, text='Do you want to close the app?\nNothing will be saved.')
    label.grid(row=1,column=1,rowspan=1,columnspan=2)
    btn_resume = ttk.Button(second, text='No', command=second.destroy)
    btn_resume.grid(row=2, column=1, rowspan=1, columnspan=1)
    btn_close = ttk.Button(second, text='Yes', command=window.destroy)
    btn_close.grid(row=2, column=2, rowspan=1, columnspan=1)

root.protocol("WM_DELETE_WINDOW", lambda : close(root))

"""
TODO:
 - add option to change name in timer_button
 - allow moving match
 - Called name list (queue) at the bottom
"""


# Add menu
# mb = Menubutton(root, text='Option')
# mb.grid()
# mb.menu = Menu(mb, tearoff=0)
# mb['menu'] = mb.menu
# cVar = IntVar()
# aVar = IntVar()
# mb.menu.add_checkbutton ( label ='Contact', variable = cVar )
# mb.menu.add_checkbutton ( label = 'About', variable = aVar )
# mb.pack()

# menu = Menu(root)
# item = Menu(menu)
# item.add_command(label='Setting')
# menu.add_cascade(label='Option', menu=item)
# root.config(menu=menu)

# Court Timer part
frame = ttk.Frame(root)
for row in range(3):
    for col in range(4):
        tb = timer_button(frame, padx=5, pady=10, highlightthickness=2,
                          highlightbackground='black')
        tb.grid(column=col, row=row, columnspan=1, rowspan=1)
frame.grid(row=1, column=1, rowspan=1, columnspan=1, sticky='W')

#
frame = ttk.Frame(root)
que = []
def add_que():
    if len(que) == 16:
        warning('You are calling too many matches at once!')
        return
    qt = queue_timer(frame, delete_que, len(que),
                     padx=5, pady=10, highlightthickness=2, highlightbackground='yellow')
    que.append(qt)
    redo_que()

def redo_que():
    for i,qt in enumerate(que):
        qt.grid(row=2+i//6, column=i%6, rowspan=1, columnspan=1)
        qt.index = i

def delete_que(n):
    que[n].event.cancel()
    que.pop(n).destroy()
    redo_que()

def warning(txt):
    second = tk.Toplevel()
    second.title('Warning')
    second.protocol("WM_DELETE_WINDOW", __callback)
    label = tk.Label(second, text=txt)
    label.grid(row=1, column=1, rowspan=1, columnspan=1)
    btn_resume = ttk.Button(second, text='ok', command=second.destroy)
    btn_resume.grid(row=2, column=1, rowspan=1, columnspan=1)



btn_add_que = ttk.Button(root, text='Call', command=add_que)
btn_add_que.grid(row=2, column=1, rowspan=1, columnspan=1, sticky='W')
frame.grid(row=3, column=1, rowspan=1, columnspan=1, sticky='W')
root.mainloop()