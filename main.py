"""                                  Технічне завдання до домашнього завдання HW08


В цьому домашньому завданні ви повинні додати функціонал збереження адресної книги на диск та відновлення з диска.

Для минулого домашнього завдання ви маєте вибрати pickle протокол серіалізації/десеріалізації даних та реалізувати 
методи, які дозволять зберегти всі дані у файл і завантажити їх із файлу. Ось код з попереднього домашнього завдання:

from datetime import datetime, date, timedelta
from collections import UserDict

# Спочатку опишемо класи
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        # Виправлена валідація дати
        if not isinstance(value, str):
            raise ValueError("Birthday must be a string in format DD.MM.YYYY")
        try:
            string_to_date(value)
            
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        # настаток викликаємо ініціалізатор батьківського класу з рядком
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if phone:
            new_phone = Phone(new_number)
            index = self.phones.index(phone)
            self.phones[index] = new_phone
        else:
            raise ValueError("Old phone number not found.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found.")

    def get_upcoming_birthdays(self, days=7):
        users = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = string_to_date(record.birthday.value)                
                users.append({"name": record.name.value, "birthday": birthday_date})
        return get_upcoming_birthdays(users, days)

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())


def string_to_date(date_string):
    return datetime.strptime(date_string, "%d.%m.%Y").date()


def date_to_string(date):
    return date.strftime("%d.%m.%Y")


def find_next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)


def adjust_for_weekend(birthday):
    if birthday.weekday() >= 5:
        return find_next_weekday(birthday, 0)
    return birthday


def get_upcoming_birthdays(users, days=7):
    upcoming_birthdays = []
    today = date.today()

    for user in users:
        birthday_this_year = user["birthday"].replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(year=today.year + 1)
        
        if 0 <= (birthday_this_year - today).days <= days:
            birthday_this_year = adjust_for_weekend(birthday_this_year)
            congratulation_date_str = date_to_string(birthday_this_year)
            upcoming_birthdays.append({"name": user["name"], "congratulation_date": congratulation_date_str})
    return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except KeyError:
            return "Contact not found. Please check the name."
        except IndexError:
            return "Invalid command. Please provide the correct number of arguments."
        except AttributeError:
            # Якщо record є None, при звертанні до його атрибутів виникне AttributeError
            return "Contact not found. Please check the name."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    # Якщо запис не знайдено, створюємо новий контакт. Обробка помилки відсутня,
    # оскільки це нормальна ситуація при додаванні нового контакту.
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return f"Contact {name} phone updated from {old_phone} to {new_phone}."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    phones = ', '.join(phone.value for phone in record.phones) if record.phones else "No phones"
    return f"{name}'s phone numbers: {phones}."


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    record.add_birthday(birthday_str)
    return f"Birthday {birthday_str} added to contact {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record.birthday is None:
        return f"No birthday set for contact {name}."
    return f"{name}'s birthday is {record.birthday.value}."


@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7
    upcoming = book.get_upcoming_birthdays(days)
    if not upcoming:
        return "No upcoming birthdays."
    result = []
    for entry in upcoming:
        result.append(f"{entry['name']} - {entry['congratulation_date']}")
    return "\n".join(result)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")



if __name__ == "__main__":
    main()


Головна мета, щоб застосунок не втрачав дані після виходу із застосунку та при запуску відновлював їх з файлу. 
Повинна зберігатися адресна книга з якою ми працювали на попередньому сеансі.

Реалізуйте функціонал для збереження стану AddressBook у файл при закритті програми і відновлення стану при її запуску.

Приклади коду які стануть в нагоді.

Серіалізація з pickle


import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


Інтеграція збереження та завантаження в основний цикл

def main():
    book = load_data()

    # Основний цикл програми

    save_data(book)  # Викликати перед виходом з програми

Ці приклади допоможуть вам у реалізації домашнього завдання.


                        Критерії оцінювання:

1. Реалізовано протокол серіалізації/десеріалізації даних за допомогою pickle
2. Всі дані повинні зберігатися при виході з програми
3. При новому сеансі Адресна книга повинна бути у застосунку, яка була при попередньому запуску."""