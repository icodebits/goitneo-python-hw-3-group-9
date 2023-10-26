from collections import UserDict, defaultdict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(value):
        return len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid_birthday(value):
            raise ValueError("Invalid birthday format. Please use 'DD.MM.YYYY'.")
        super().__init__(value)

    @staticmethod
    def is_valid_birthday(value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not isinstance(phone, Phone):
            phone = Phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p != phone]

    def edit_phone(self, old_phone, new_phone):
        new_phone = Phone(new_phone)
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
    
    def add_birthday(self, birthday):
        if not isinstance(birthday, Birthday):
            birthday = Birthday(birthday)
        self.birthday = birthday

    def __str__(self):
        phone_list = '; '.join(str(p) for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phone_list}, birthday: {self.birthday or 'N/A'}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_birthdays_per_week(self):
        output = ''
        # Prepare data
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        birthday_dict = defaultdict(list)

        # Cycle through users
        for user in self.data.values():
            print(user)
            name = user.name.value
            birthday = datetime.strptime(user.birthday.value, '%d.%m.%Y').date()
            birthday_this_year = birthday.replace(year=today.year)
            
            # Check Birth Day this year
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Find how many day to/from the Birth Day
            delta_days = (birthday_this_year - today).days

            # Find day of the week and keep the result
            if delta_days < 7:
                day_of_week = (today + timedelta(days=delta_days)).strftime('%A')
                if day_of_week in ["Sunday","Saturday"]:
                    birthday_dict["Monday"].append(name)
                else:
                    birthday_dict[day_of_week].append(name)


        # Result Output
        for day, names in birthday_dict.items():
            output = output + f"{day}: {', '.join(names)}" + '\r\n'
        
        return str.strip(output)

if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("27.10.1990")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday("29.10.1985")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    print(book.get_birthdays_per_week())

    # Знаходження та редагування телефону для John
    john = book.find("John")
    if john:    # Перевірка запису до редагування
        john.edit_phone("1234567890", "1112223333")

    print(john) # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    if found_phone: # Перевірка запису до виведення
        print(f"{john.name}: {found_phone}")  # Виведення: John: 5555555555
    
    # Видалення запису Jane
    book.delete("Jane")
