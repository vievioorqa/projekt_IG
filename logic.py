from enum import Enum
from typing import List
import json
import random


QUESTIONS_FILE = 'questions.json'
LETTERS_FILE = 'letters.json'


class Player:
    def __init__(self, name: str, jug: int = 0, star: int = 0) -> None:
        self.name = name
        self.jug = jug
        self.star = star

    def serialize(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def deserialize(json_dict: str) -> 'Player':
        return Player(**json.loads(json_dict))


class Letter:
    def __init__(self, movement: int) -> None:
        self.movement = movement

    def serialize(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def deserialize(json_dict: str) -> 'Letter':
        return Letter(**json.loads(json_dict))


class Question:
    class Difficulty(Enum):   #słownik
        EASY = "easy"
        MEDIUM = "medium"
        HARD = "hard"

    def __init__(self, difficulty: Difficulty, question: str, answers: List[str]) -> None:
        self.difficulty = difficulty.value   #difficulty.value: Pobiera wartość enumeracji Difficulty
        self.question = question
        self.answers = answers

    def serialize(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod   #@staticmethod: Jest to dekorator, który oznacza, że poniżej znajduje się metoda statyczna, a nie metoda instancji. Oznacza to, że metoda może być wywołana bez utworzenia instancji obiektu klasy Question.
    def deserialize(json_dict: str) -> 'Question':
        json_dict = json.loads(json_dict)   # W efekcie uzyskujemy słownik Pythona reprezentujący dane pytania.
        difficulty = json_dict['difficulty']    # Pobiera wartość klucza 'difficulty' ze słownika, która reprezentuje poziom trudności pytania.

        for member in Question.Difficulty:
            if member.value == difficulty:  #Sprawdza, czy wartość aktualnego elementu enumeracji (member.value) jest równa wartości poziomu trudności pobranej z danych JSON. Jeśli tak, to przypisuje ten element do zmiennej difficulty.
                difficulty = member

        return Question(difficulty=difficulty, question=json_dict['question'], answers=json_dict['answers'])


class Field:
    def __init__(self, content: Question | Letter = None, players: List[Player] = None) -> None:
        self.content = content
        if not players:   #jeśli players nie zostało przekazane
            players = []
        self.players = players
        if isinstance(content, Question):
            self.content_type = 'question'
        elif isinstance(content, Letter):
            self.content_type = 'letter'
        else:
            self.content_type = 'normal'

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def serialize(self) -> str:
        if not self.content:
            content = {}
        else:
            content = self.content.serialize()

        field = {'content': content, 'players': [player.serialize() for player in self.players]}  #Tworzy słownik (field), który reprezentuje dane pola gry. Klucz 'content' w tym słowniku odpowiada zawartości pola. Klucz 'players' wskazuje na listę graczy, którzy są na tym polu. Jeśli zawartość pola istnieje (content nie jest None), to klucz 'content' zawiera zserializowane dane dotyczące zawartości pola (content.serialize()).
        return json.dumps(field)

    @staticmethod
    def deserialize(json_dict: str) -> 'Field':
        json_dict = json.loads(json_dict)
        content = json_dict['content']

        if 'movement' in content:
            content = Letter.deserialize(json.dumps(content))
        elif 'answers' in content:
            content = Question.deserialize(json.dumps(content))
        else:
            content = None

        players = [Player.deserialize(player) for player in json_dict['players']]

        return Field(content=content, players=players)


class Board:
    LENGTH = 18
    NORMAL_FIELD_CHANCE = 0.5
    QUESTION_FIELD_CHANCE = 0.7

    def __init__(self, players: List[Player] = None) -> None:
        self.fields: List[Field] = []  #: List[Field]: Wskazuje, że fields powinno być listą obiektów klasy Field.

        if players is not None:
            self.new_game(players)  #Jeśli przekazano listę graczy, wywołuje metodę new_game do rozpoczęcia nowej gry

    def serialize(self) -> str:
        board = {'fields': [field.serialize() for field in self.fields]}
        return json.dumps(board)

    @staticmethod
    def deserialize(json_dict: str) -> 'Board':
        json_dict = json.loads(json_dict)
        board = Board()
        board.fields = [Field.deserialize(field) for field in json_dict['fields']]
        return board

    def new_game(self, players: List[Player]) -> None:
        with open(QUESTIONS_FILE, 'r') as file:
            questions_list = json.load(file)

        with open(LETTERS_FILE, 'r') as file:
            letters_list = json.load(file)

        for i in range(Board.LENGTH - 2):
            if random.random() < Board.NORMAL_FIELD_CHANCE or (len(letters_list) == 0 and len(questions_list) == 0):
                self.fields.append(Field())   #utworzone normalne pole
            else:
                if random.random() < Board.QUESTION_FIELD_CHANCE or len(letters_list) == 0:
                    field_content = questions_list.pop(questions_list.index(random.choice(questions_list)))   #pole z pytaniem. losowy wybór pytania z questions_list, usunięcie tego pytania z listy. Zawartość pola (field_content) jest ustawiana na to pytanie.
                else:
                    field_content = letters_list.pop(letters_list.index(random.choice(letters_list)))   #pole z listem. Wybranie losowej litery z listy liter (letters_list) i usunięcie jej z listy. Zawartość pola (field_content) jest ustawiana na tę literę.
                self.fields.append(Field(field_content))   #dodanie pola do planszy

        start_field = Field()
        end_field = Field()

        for player in players:
            start_field.add_player(player)

        self.fields.insert(0, start_field)  # dodaje zwykłe pole na początek
        self.fields.insert(Board.LENGTH - 1, end_field)  # dodaje zwykłe pole na koniec
