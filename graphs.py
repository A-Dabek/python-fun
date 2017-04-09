import matplotlib
from matplotlib import pyplot as plt
import numpy as np

matplotlib.rc('font', family='Arial')

names = [
    'Czy hasła, których używasz do logowania są bezpieczne\n - zawierają duże i małe litery oraz cyfry?',
    'Czy twój komputer ma zainstalowany aktywny program antywirusowy?',
    'Czy rozmawiasz z rodzicami o tym, co robisz w Internecie?',
    'Czy ustaliłeś z rodzicami zasady,\n na których możesz korzystać z Internetu?',
    'Z kim najczęście rozmawiasz o Internecie?',
    'Jak często korzystasz z Internetu?',
    'Jak dużo czasu spędzasz w Internecie?',
    'W jakich godzinach najczęściej korzystasz z komputera?',
    'Czy zdarza Ci się korzystać z komputera (lub innych urządzeń)\n poźną porą (wieczorem/w nocy)?',
    'Czy umieszczasz w sieci informacje o sobie, znajomych lub rodzinie?',
    'Czy uważasz, że umieszczanie treści na twój temat\n lub twoich znajomych może być niebezpieczne?',
    'Czy komentujesz zamieszczone w Internecie treści?',
    'Czy zdarzyło ci się napisać w Internecie coś, co mogło sprawić komuś przykrość?',
    'Czy zdarzyło ci się przeczytać w Internecie coś na swój temat,\n co sprawiło ci przykrość?',
    'Jeśli tak, to jak zareagowałeś na treści?',
    'Z jakich serwisów internetowych najczęściej korzystasz?',
    'Czy w Internecie podałeś obcym osobom swoje dane osobowe?',
    'Czy w Internecie otrzymałeś propozycję\n spotkania się z obcą osobą?',
    'Czy spotkałbyś się z obcą osobą poznaną w Internecie?',
    'Czy kiedykolwiek byłeś ofiarą gróźb\n lub obraźliwych treści w Internecie?',
    'Czy otrzymałeś nieprzyzwoite propozycje przez Internet?',
    'Czy bałeś się w związku z otrzymywaniem\n ewentualnych gróźb bądź nieprzyzwoitych propozycji?',
    'Czy wypełniałeś w Internecie kwestionariusze osobowe\n na prośbę obcych osób?',
    'Czy łatwiej rozmawia się tobie z ludźmi przez Internet?',
    'Czy ktoś mówi ci, że spędzasz za dużo czasu w Internecie?',
    'Czy chcesz spędzać więcej czasu w Internecie?',
    'Czy zdarzało ci się nie jeść lub jeść przy komputerze,\n aby spędzać więcej czasu w Internecie?',
    'Czy z powodu komputera/telefonu/tabletu\n zdarzyło ci się nie odrobić zadań domowych?',
    'Czy masz problemy ze snem lub śpisz w nietypowych porach\n w związku z używaniem komputera/telefona/tabletu?',
    'Czy zdarzyło ci się \"wchodzić\" na strony\n nieprzeznaczone dla dzieci? (nawet przypadkiem)'
]

questions = [
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],
    ['Często', 'Czasem', 'Rzadko', 'Nigdy'],
    ['Tak', 'Nie'],
    ['Rodzice', 'Koledzy', 'Rodzeństwo', 'Nauczyciele', 'Przypadkowe\nosoby', 'Inne osoby'],  # 5
    ['Codziennie', 'Kilka razy\n w tygodniu', 'Raz na miesiąc', 'Kilka razy\n w miesiącu', 'Raz na miesiąc', 'Wcale'],
    ['Wcale/kilka minut', '0,5h - 1h', '1,5h - 2h', '2,5h - 3h', '3,5h - 4h', '4h+'],
    ['6-10', '11-15', '16-20', '21-24', '24+'],
    ['Tak', 'Nie'],
    ['Tak', 'Nie'],  # 10
    ['Tak', 'Nie', 'Nie wiem'],
    ['Często', 'Czasami', 'Nigdy'],
    ['Tak', 'Nie', 'Nie wiem'],
    ['Tak', 'Nie'],
    ['Nic', 'Powiedziałem\n dorosłemu', 'Powiedziałem\n kolegom', 'Rozmawiałem z\n piszącym te treści', 'Zrobiłem\n to samo', 'Inaczej\n zareagowałem'],  # 15
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

ans_data = open('data_X.txt', 'r')
for elem in ans_data.readline().split(','):
    if elem[0] == '[' or elem.startswith(' ['):
        answers.append([])
    answers[len(answers) - 1].append(int(elem.strip(' []')))

print(answers)

csv_file = open('data.csv', 'w')

for i, ar, q in zip(names, answers, questions):
    row = '"' + i + '"' + ';'
    for qq in q:
        row += '"' + qq + '";'
    row = row[:-1] + '\n'
    print(row)
    csv_file.write(row)
    row = ';'
    for ac in ar:
        row += '"' + str(ac) + '"'
        row += ';'
    row = row[:-1] + '\n'
    csv_file.write(row)
    print(row)


csv_file.close()

exit()
exit()
exit()
fig_number = 1
for q, a, n in zip(questions, answers, names):
    n_groups = len(q)
    means_men = a
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 1. / n_groups
    rects1 = plt.bar(index, a, bar_width,
                     color='', edgecolor='black')
    plt.xlabel('')
    plt.ylabel('liczba głosów')
    plt.title(n)
    if n_groups > 6:
        plt.xticks(index + bar_width / 2, q, rotation=45)
    else:
        plt.xticks(index + bar_width / 2, q)

    plt.tight_layout()
    plt.savefig('wykresy/wykres_' + str(fig_number) + '.png')
    fig_number += 1
    plt.close()
