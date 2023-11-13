import tkinter as tk
import tkinter.ttk as ttk
from components import timer_button, queue_timer, match_button, RepeatTimer
from time import time
import threading
import datetime
import logging

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/presentations"]
PRESENTATION_ID = "1kI6iC2XyPtJslBBTX8aCuThsxc9L0w5T0iDoXWyevxE"
deleteTextRequest = lambda r, c: {
    "deleteText": {
        "objectId": "g29998979928_0_10",
        "cellLocation": {
            "rowIndex": r,
            "columnIndex": c,
        },
        "textRange": {
            "type": "ALL",
        }
    }
}
insertTextRequest = lambda r, c, text: {
    "insertText": {
        "objectId": "g29998979928_0_10",
        "cellLocation": {
            "rowIndex": r,
            "columnIndex": c,
        },
        "text": text,
        "insertionIndex": 0
    }
}

creds = None
service = None
event = None
# ++++++++++++++++++++++++
# Variables
COURT_ROW = 3
COURT_COL = 4
MAX_CALL_QUE = 30
QUE_COL = 5
CALL_TIME = 2 # min
PPT_ROW = 6
PPT_COL = 6
EDIT_TIME_THRESHOLD = 10
SLIDE_DOC = 0
LAST_UPDATE = 0
UPDATE_THRESHOLD = 10
# ++++++++++++++++++++++++
lock = threading.Lock()

def log(*args):
    print(f'{datetime.datetime.now()} -',*args)

def auth():
    global creds, service
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "sjsutournamentcredentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    log('auth')
    try:
        service = build("slides", "v1", credentials=creds)
        log('build done')
    except HttpError as err:
        log(err)

with lock:
    auth()

root = tk.Tk()
root.title('SJSU Spring 2023 SmashOff')
root.geometry('1000x800')
# root.resizable(0,0)

def __callback():
    with lock:
        requestDeleteAll(PPT_ROW, PPT_COL, SLIDE_DOC)
        event.cancel()

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

def check_time(t, threshold):
    t2 = time()
    if t2 - t < threshold:
        return False
    return t2

def set_event():
    global event
    event = RepeatTimer(UPDATE_THRESHOLD, checkUpdate)
    event.start()

def callRequest(req, mtd):
    global SLIDE_DOC, LAST_UPDATE
    if not req:
        return
    try:
        service.presentations().batchUpdate(
            body={
                "requests": req
            },
            presentationId=PRESENTATION_ID,
        ).execute()
        if mtd == 'add':
            SLIDE_DOC += len(req)
        elif mtd == 'del':
            SLIDE_DOC -= len(req)
        event.cancel()
        LAST_UPDATE = time()
        set_event()
    except Exception as e:
        log(e)

def requestDeleteAll(max_r, max_c, count):
    auth()
    req = []
    index = 0
    for row in range(1,max_r):
        for col in range(max_c):
            if index < count:
                req.append(deleteTextRequest(row, col))
                index += 1
    thr = threading.Thread(target=lambda : callRequest(req, 'del'))
    thr.start()
    thr.join()

def requestAddQue(max_r,max_c,que):
    auth()
    req = []
    index = 0
    for row in range(1,max_r):
        for col in range(0,max_c,2):
            if index < len(que):
                req.append(insertTextRequest(row, col, que[index].var_match_no.get()))
                time_left = que[index].var_time.get()[2:3]
                if time_left == "6":
                    time_left = "5"
                if que[index].var_time.get() == "0":
                    time_left = "LAST CALL"
                else:
                    time_left += " min"
                req.append(insertTextRequest(row, col+1, time_left))
                index += 1
    thr = threading.Thread(target=lambda : callRequest(req, 'add'))
    thr.start()
    thr.join()

def checkUpdate():
    global LAST_UPDATE
    t = check_time(LAST_UPDATE, UPDATE_THRESHOLD)
    if t:
        LAST_UPDATE = t
        if not lock.locked():
            with lock:
                requestDeleteAll(PPT_ROW, PPT_COL, SLIDE_DOC)
                requestAddQue(PPT_ROW, PPT_COL, que)

# Court Timer part
row = 0
court_frame = ttk.Frame(root)
for row in range(COURT_ROW):
    for col in range(COURT_COL):
        tb = timer_button(court_frame, padx=5, pady=10, highlightthickness=2,
                          highlightbackground='black')
        tb.grid(column=col, row=row, columnspan=1, rowspan=1)
# court_frame.pack(side='top', anchor='nw')
court_frame.grid(column=0, row=0, columnspan=1, rowspan=1, sticky='w')

queue_frame = ttk.Frame(root)
que = []
def add_que(label):
    log('adding to queue')
    if len(que) == MAX_CALL_QUE:
        warning('You are calling too many matches at once!')
        return
    qt = queue_timer(queue_frame, delete_que, len(que), label, minutes=CALL_TIME,
                     padx=5, pady=10, highlightthickness=2, highlightbackground='yellow')
    que.append(qt)
    redo_que()

def redo_que():
    for i,qt in enumerate(que):
        qt.grid(row=2+i//QUE_COL, column=i%QUE_COL, rowspan=1, columnspan=1)
        qt.index = i
    if not lock.locked():
        with lock:
            requestDeleteAll(PPT_ROW, PPT_COL, SLIDE_DOC)
            requestAddQue(PPT_ROW, PPT_COL, que)

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


mb = match_button(master=root,
                  label_list=[list("ABCDE"), ['MS', 'WS', 'XD', 'MD', 'WD'], list('0123456789'), list('0123456789')],
                  pre=[False,False,True,True],
                  action=add_que)
# mb.pack(side='top', anchor='ne')
mb.grid(column=1, row=0, columnspan=1, rowspan=1, sticky='w')
# queue_frame.pack(side='top', anchor='nw')
queue_frame.grid(column=0, row=1, columnspan=2, rowspan=1, sticky='w')
set_event()
root.mainloop()