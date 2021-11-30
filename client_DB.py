from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import datetime

class ClientDatabase:

    class Contacts:
        def __init__(self, username):
            self.username = username
            self.id = None

    class Messages:
        def __init__(self, from_user, message_text, date):
            self.from_user = from_user
            self.message_text = message_text
            self.date = date
            self.id = None

    class KnownUsers:
        def __init__(self, username):
            self.id = None
            self.username = username

    def __init__(self, username):

        self.client_engine = create_engine(f'sqlite:///server-DB-{username}.db3', echo=False, pool_recycle=7200,
                                           connect_args={'check_same_thread': False})

        metadata = MetaData()

        contacts_table = Table('contacts', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('username', String),
                               )

        messages_table = Table('messages', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('from_user', String),
                               Column('message_text', String),
                               Column('date', DateTime)
                               )

        known_users_table = Table('known_users', self.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('username', String)
                                  )

        metadata.create_all(self.client_engine)

        mapper(self.Contacts, contacts_table)
        mapper(self.Messages, messages_table)
        mapper(self.KnownUsers, known_users_table)

        new_session = sessionmaker(bind=self.server_engine)

        self.session = new_session()

        self.session.query(self.KnownUsers).all().delete()
        self.session.commit()