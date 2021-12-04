import os
import datetime

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import IN, OUT


class ClientDatabase:

    class Contacts:
        def __init__(self, username):
            self.username = username
            self.id = None

    class Messages:
        def __init__(self, username, direction, message_text, date):
            self.username = username
            self.direction = direction
            self.message_text = message_text
            self.date = date
            self.id = None

    class KnownUsers:
        def __init__(self, username):
            self.id = None
            self.username = username

    def __init__(self, username):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.client_engine = create_engine(f'sqlite:///{dir_path}/client_{username}.db3', echo=False, pool_recycle=7200,
                                           connect_args={'check_same_thread': False})

        metadata = MetaData()

        contacts_table = Table('contacts', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('username', String),
                               )

        messages_table = Table('messages', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('username', String),
                               Column('direction', String),
                               Column('message_text', String),
                               Column('date', DateTime)
                               )

        known_users_table = Table('known_users', metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('username', String)
                                  )

        metadata.create_all(self.client_engine)

        mapper(self.Contacts, contacts_table)
        mapper(self.Messages, messages_table)
        mapper(self.KnownUsers, known_users_table)

        new_session = sessionmaker(bind=self.client_engine)

        self.session = new_session()

        self.session.query(self.KnownUsers).delete()
        self.session.commit()

    def add_contact(self, contact_name):
        if not self.session.query(self.Contacts).filter_by(username=contact_name).count():
            new_contact = self.Contacts(username=contact_name)
            self.session.add(new_contact)
            self.session.commit()

    def delete_contact(self, contact_name):
        self.session.query(self.Contacts).filter_by(username=contact_name).delete()
        self.session.commit()

    def add_message(self, username, direction, message_text, date):
        new_message = self.Messages(username=username, direction=direction, message_text=message_text, date=date)
        self.session.add(new_message)
        self.session.commit()

    def add_users(self, users: list):
        for user in users:
            new_user = self.KnownUsers(username=user)
            self.session.add(new_user)
        self.session.commit()

    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.Contacts.username).all()]

    def get_messages(self, contact_name):
        return self.session.query(self.Messages.username,
                                  self.Messages.direction,
                                  self.Messages.message_text,
                                  self.Messages.date
                                  ).filter_by(username=contact_name).all()

    def get_users(self):
        return [contact[0] for contact in self.session.query(self.KnownUsers.username).all()]


if __name__ == '__main__':
    new_db = ClientDatabase('Petrov')
    new_db.add_contact('test1')
    new_db.add_contact('test2')
    new_db.add_contact('test3')
    new_db.add_contact('test4')
    new_db.add_contact('Ivanov')
    new_db.add_contact('Sidorov')
    new_db.delete_contact('test2')
    new_db.delete_contact('test4')
    print(new_db.get_contacts())
    new_db.add_message('Ivanov', 'Привет!', OUT, datetime.datetime.now())
    new_db.add_message('Ivanov', 'Привет!', IN, datetime.datetime.now())
    new_db.add_message('Ivanov', 'Как дела?!', OUT, datetime.datetime.now())
    new_db.add_message('Ivanov', 'Ништяк', IN, datetime.datetime.now())
    new_db.add_message('Sidorov', 'Ты когда сотку вернешь?!', IN, datetime.datetime.now())
    new_db.add_message('Sidorov', 'Сорян! Пока на мели :((( Давай в следующем месяце', OUT, datetime.datetime.now())
    print(new_db.get_messages('Ivanov'))
    print(new_db.get_messages('Sidorov'))
