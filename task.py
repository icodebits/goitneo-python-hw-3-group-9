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
        output = []
        # Prepare data
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        birthday_dict = defaultdict(list)

        # Cycle through users
        for user in self.data.values():
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
            output.append(f"{day}: {', '.join(names)}")
        
        return '\r\n'.join(output)

class Bot:
    def parse_input(self,user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args

    def input_error(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError:
                return "Give me name and phone please."
            except IndexError as e:
                return "Give me the name please."

        return inner
    
    def input_error_bday(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError:
                return "Give me the name and birthday please."

        return inner

    @input_error
    def add_contact(self, args, contacts):
        record_found = None
        name, phone = args
        # Check if contact exists
        record = contacts.find(name)
        if record:                      # Contact exists
            record_found = True
        else:                           # No contact found with this name, should create new one
            record_found = False
            record = Record(name)
            
        # To elaborate correct Phone length wrap it in try-except and return its error
        try:
            record.add_phone(phone)
        except ValueError as e:
            return e

        # If contact was not found, should add it to the contacts, otherwise its already updated
        if not record_found:
            contacts.add_record(record)
            return "Contact added."
        else:
            return "Contact added new phone."
        
    @input_error
    def change_contact(self, args, contacts):
        name, old_phone, new_phone = args
        record = contacts.find(name)
        # Check if contact exists
        if record:
            # To elaborate correct Phone length wrap it in try-except and return its error
            try:
                record.edit_phone(old_phone, new_phone)
                return "Contact updated."
            except ValueError as e:
                return e
        else:
            return f'{name} not found.'

    @input_error
    def show_phone(self, args, contacts):
        name = args[0]
        record = contacts.find(name)
        if record != None:
            return '; '.join(str(p) for p in record.phones)
        else:
            return f'{name} not found.'

    def show_all(self, contacts):
        all_contacts = []
        if contacts:
            for name, record in contacts.data.items():
                all_contacts.append(f'{record}')
            return '\r\n'.join(all_contacts)
        else:
            return 'The contact list is empty'

    @input_error_bday
    def add_birthday(self, args, contacts):
        name, birthday = args
        # Check if contact exists
        record = contacts.find(name)
        if record:
            # To elaborate correct Birthday format wrap it in try-except and return its error
            try:
                record.add_birthday(birthday)
            except ValueError as e:
                return e
            return "Birthday added."
        else:
            return f'{name} not found.'

    @input_error
    def show_birthday(self, args, contacts):
        name = args[0]
        # Check if contact exists
        record = contacts.find(name)
        if record != None:
            return record.birthday
        else:
            return f'{name} not found.'
    
    def get_birthdays(self, contacts):
        if contacts:
            return contacts.get_birthdays_per_week()
        else:
            return 'The contact list is empty'

    def main(self):
        book = AddressBook()
        print("Welcome to the assistant bot!")
        while True:
            user_input = input("Enter a command: ")
            command, *args = self.parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break
            elif command == "hello":
                print("How can I help you?")
            elif command == "add":
                print(self.add_contact(args, book))
            elif command == "change":
                print(self.change_contact(args, book))
            elif command == "phone":
                print(self.show_phone(args, book))
            elif command == "all":
                print(self.show_all(book))
            elif command == "add-birthday":
                print(self.add_birthday(args, book))
            elif command == "show-birthday":
                print(self.show_birthday(args, book))
            elif command == "birthdays":
                print(self.get_birthdays(book))
            else:
                print("Invalid command.")

if __name__ == "__main__":
    bot = Bot()
    bot.main()