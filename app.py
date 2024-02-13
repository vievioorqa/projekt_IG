from flask import Flask, render_template, request, redirect, url_for, session
import random

from logic import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Zmienna przechowująca wybór pionka, imię gracza, aktualną pozycję pionków i ilość pól do przesunięcia
selected_pawn = "Czerwony pionek"
player_name = ""
current_position = {"red": 0, "purple": 0}
fields_to_move = 0


@app.route('/')
def preparation():
    return render_template('preparation.html')


# Endpoint obsługujący formularz wyboru pionka i imienia gracza
@app.route('/start_game', methods=['POST'])
def start_game():
    global selected_pawn, player_name

    # Pobierz dane z formularza
    selected_pawn = request.form.get('pawnColor')
    player_name = request.form.get('playerName')

    # Walidacja: Sprawdź, czy gracz wybrał pionek
    if not selected_pawn:
        error_message = "Wybierz pionek przed rozpoczęciem gry!"
        return render_template('preparation.html', error_message=error_message)

    # Walidacja: Sprawdź, czy gracz wprowadził imię
    if not player_name:
        error_message = "Wpisz imię przed rozpoczęciem gry!"
        return render_template('preparation.html', error_message=error_message)

    if player_name == 'komputer' or player_name == 'Komputer':
        error_message = "Nie możesz nazywać się 'komputer'"
        return render_template('preparation.html', error_message=error_message)

    player = Player(player_name)
    computer = Player('komputer')
    board = Board([player, computer])

    session['board'] = board.serialize()
    session['player'] = player.serialize()
    session['computer'] = computer.serialize()

    # Przekieruj na stronę gry
    return redirect(url_for('board_view'))


# Endpoint wyświetlający planszę
@app.route('/board')
def board_view():
    global current_position, fields_to_move

    board = Board.deserialize(session['board'])
    player = Player.deserialize(session['player'])
    computer = Player.deserialize(session['computer'])

    # Ustawienie początkowych pozycji pionków na polu "START"
    # current_position['red'] = 0
    # current_position['purple'] = 0


    # Tutaj umieść kod do obsługi rzutu kostką i przesunięcia pionków
    # Losowanie liczby pól do przesunięcia (np. rzut kostką)
    fields_to_move = random.randint(1, 6)



    # Przesunięcie pionków na planszy
    move_pawns()

    return render_template('board_view.html',
                           board=board, player=player, computer=computer)


def move_pawns():
    global current_position, fields_to_move

    # Przesuń pionki o określoną liczbę pól
    current_position['red'] += fields_to_move
    current_position['purple'] += fields_to_move

    # Sprawdź, czy pionki przekroczyły liczbę pól na planszy, a następnie ustal ich nową pozycję
    board_length = 18  # Ustal długość planszy (liczba pól)
    for color in current_position:
        if current_position[color] >= board_length:
            current_position[color] = board_length - 1


@app.route('/roll_dice', methods=['POST'])
def roll_dice():
    global fields_to_move
    fields_to_move = random.randint(1, 6)
    return redirect(url_for('board'))


if __name__ == '__main__':
    app.run(debug=True)
