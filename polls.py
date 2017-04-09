import tkinter as tk
from functools import partial

questions = [
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],
    ['Często', 'Czasem', 'Rzadko', 'Nigdy'],
    ['Tak', 'Nie'],
    ['Rodzice', 'Koledzy', 'Rodzeństwo', 'Nauczyciele', 'Przypadkowe osoby', 'Inne osoby'],  # 5
    ['Codziennie', 'Kilka razy w tyg', 'Raz na miesiąc', 'Kilka razy w m', 'Raz na miesiąc', 'Wcale'],
    ['Wcale/kilka', '0,5h - 1h', '1,5h - 2h', '2,5h - 3h', '3,5h - 4h', '4h+'],
    ['6-10', '11-15', '16-20', '21-24', '+24'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],  # 10
    ['Tak', 'Nie', 'Nie wiem'],
    ['Cżesto', 'Czasami', 'Nigdy'],
    ['Tak', 'Nie', 'Nie wiem'],
    ['Tak', 'Nie'],
    ['Nic', 'Dorosłemu', 'Kolegom', 'Z piszącym', 'Zrobiłem to samo', 'Inaczej'],  # 15
    ['YouTube', 'e-mail', 'Czaty', 'Gry', 'Edukacja', 'Blogi', 'Społecz', 'Encyklopedie', 'Komunikatory'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie', 'Zdarzyło'],
    ['Tak', 'Nie'],  # 20
    ['Tak', 'Nie'],
    ['Tak', 'Nie', 'Nie dotyczy'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie', 'Czasami'],
    ['Tak', 'Nie'],  # 25
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie']  # 30
]
answers = []
for q in questions:
    answers.append([])
    for var in q:
        answers[len(answers) - 1].append(0)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.structure = []
        self.pack()
        self.create_widgets()
        self.iterator = 0

    def create_widgets(self):

        q_in_row = 10
        for q_id in range(len(questions)):
            self.structure.append([])
            for var_id in range(len(questions[q_id])):
                b = tk.Button(self, text= '(' + str(q_id+1) + ') ' + questions[q_id][var_id])
                l = tk.Label(self, text=0)
                if q_id % 3 == 0:
                    b['fg'] = 'blue'
                elif q_id % 3 == 1:
                    b['fg'] = 'red'
                elif q_id % 3 == 2:
                    b['fg'] = 'green'
                b['command'] = partial(self.increment, q_id=q_id, var_id=var_id)
                b.grid(column=2 * ((q_id % q_in_row) + 1) - 1, row=(q_id//q_in_row * q_in_row + 1) + (var_id % q_in_row + 1), sticky='w')
                l.grid(column=2 * ((q_id % q_in_row) + 1), row=(q_id//q_in_row * q_in_row + 1) + (var_id % q_in_row + 1))
                self.structure[q_id].append([b, l])

                # self.hi_there = tk.Button(self)
                # self.labl = tk.Label(self)
                # self.hi_there.grid(row=1, column=1)
                # self.labl.grid(row=1, column=2)
                # self.labl['text'] = "ELOAL"
                #
                # self.labls = [tk.Label(self, text="raz"), tk.Label(self, text="dwa"), tk.Label(self, text="trzy")]
                # self.labls[0].grid(row=2, column=1)
                # self.labls[1].grid(row=2, column=2)
                # self.labls[2].grid(row=2, column=3)
                # # self.hi_there['padx'] = 100
                # # self.hi_there['pady'] = 100
                # self.hi_there["text"] = "Hello World\n(click me)"
                # self.hi_there["command"] = partial(self.say_hi, cos='eloszka')
                # self.hi_there.pack()
                # self.labl.pack(after=s)
                #
                # self.quit = tk.Button(self, text="QUIT", fg="red",
                #                       command=root.destroy)
                # self.quit.pack(side="bottom")

    def increment(self, q_id, var_id):
        print("pytanie %d wariant %d!" % (q_id, var_id))
        answers[q_id][var_id] += 1
        self.structure[q_id][var_id][1]['text'] = answers[q_id][var_id]
        context_file = open('data_' + str(self.iterator) + '.txt', 'w')
        context_file.write(str(answers))
        self.iterator += 1
        if self.iterator > 5:
            self.iterator = 0
        context_file.close()

root = tk.Tk()
app = Application(master=root)
app.mainloop()
