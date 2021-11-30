from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import datetime

from random import randint


class ServerDatabase:

    class AllUsers:

        def __init__(self, username):
            self.username = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:

        def __init__(self, user_id, ip, port):
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.login_time = datetime.datetime.now()
            self.user = user_id
            self.id = None

    class LoginHistory:

        def __init__(self, user_id, ip, port):
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.login_time = datetime.datetime.now()
            self.id = None

    class Contacts:

        def __init__(self, user_id, contact_id):
            self.user_id = user_id
            self.contact_id = contact_id
            self.id = None

    class History:

        def __init__(self, user_id):
            self.user_id = user_id
            self.messages_sent = 0
            self.messages_received = 0
            self.id = None

    def __init__(self):

        self.server_engine = create_engine('sqlite:///server-DB.db3', echo=False, pool_recycle=7200,
                                           connect_args={'check_same_thread': False})

        metadata = MetaData()

        all_users_table = Table('all_users', metadata,
                                Column('id', Integer, primary_key=True),
                                Column('username', String),
                                Column('last_login', DateTime)
                                )

        active_users_table = Table('active_users', metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', Integer, ForeignKey('all_users.id'), unique=True),
                                   Column('ip', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        login_history_table = Table('login_history', metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_id', Integer, ForeignKey('all_users.id')),
                                    Column('ip', String),
                                    Column('port', Integer),
                                    Column('login_time', DateTime)
                                    )

        contacts_table = Table('contacts', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('user_id', Integer, ForeignKey('all_users.id')),
                               Column('contact_id', Integer, ForeignKey('all_users.id')),
                               )

        history_table = Table('history', metadata,
                              Column('id', Integer, primary_key=True),
                              Column('user_id', Integer, ForeignKey('all_users.id'), unique=True),
                              Column('messages_sent', Integer),
                              Column('messages_received', Integer),
                              )

        metadata.create_all(self.server_engine)

        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)
        mapper(self.Contacts, contacts_table)
        mapper(self.History, history_table)

        new_session = sessionmaker(bind=self.server_engine)

        self.session = new_session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def login(self, username, ip, port):
        print('1')
        print(self.session.query(self.AllUsers).all())
        username_in_base = self.session.query(self.AllUsers).filter_by(username=username).first()
        print(username_in_base)
        if username_in_base:
            user = username_in_base
            user.last_login = datetime.datetime.now()

        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            users_history = self.History(user.id)
            self.session.add(users_history)
            self.session.commit()

        active_user = self.ActiveUsers(user.id, ip, port)
        self.session.add(active_user)

        login = self.LoginHistory(user.id, ip, port)
        self.session.add(login)

        self.session.commit()

    def logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def users_list(self):
        users_list = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login
        ).all()
        return users_list

    def active_users_list(self):
        active_users_list = self.session.query(
            self.AllUsers.username,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers).all()
        return active_users_list

    def message_history(self):
        message_history = self.session.query(
            self.AllUsers.username,
            self.History.messages_sent,
            self.History.messages_received
        ).join(self.AllUsers).all()
        return message_history

    def message(self, sender, recipient):
        sender_id = self.session.query(self.AllUsers).filter_by(username=sender).first().id
        recipient_id = self.session.query(self.AllUsers).filter_by(username=recipient).first().id
        self.session.query(self.History).filter_by(user_id=sender_id).first().messages_sent += 1
        self.session.query(self.History).filter_by(user_id=recipient_id).first().messages_received += 1

    def login_history(self, username=None):
        login_history = self.session.query(self.AllUsers.username,
                                           self.LoginHistory.ip,
                                           self.LoginHistory.port,
                                           self.LoginHistory.login_time).join(self.AllUsers)

        if username:
            login_history = login_history.filter(self.AllUsers.username == username)

        return login_history.all()

    def add_contact(self, username, contact_name):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        contact = self.session.query(self.AllUsers).filter_by(username=contact_name).first()

        if not user or\
           not contact or\
           self.session.query(self.Contacts).filter_by(user_id=user.id, contact_id=contact.id).all():
            return

        new_contact = self.Contacts(user_id=user.id, contact_id=contact.id)
        self.session.add(new_contact)
        self.session.commit()

    def remove_contact(self, username, contact_name):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        contact = self.session.query(self.AllUsers).filter_by(username=contact_name).first()

        if not user or not contact:
            return

        self.session.query(self.Contacts).filter_by(user_id=user.id, contact_id=contact.id).delete()
        self.session.commit()

    def contacts(self, username):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()

        contacts = self.session.query(self.Contacts, self.AllUsers.username).\
            filter_by(user_id=user.id).\
            join(self.AllUsers, self.Contacts.contact_id == self.AllUsers.id).all()

        contacts_list = [contact[1] for contact in contacts]
        
        return contacts_list


if __name__ == '__main__':

    server_DB = ServerDatabase()

    server_DB.login('test1', '127.0.0.1', 1)
    # for i in range(0, 20):
    #     server_DB.login(f'test{i}', '127.0.0.1', 1)
    #
    # for sender in server_DB.active_users_list():
    #     for recipient in server_DB.users_list():
    #         for _ in range(randint(1, 9)):
    #             server_DB.message(sender.username, recipient.username)
    #
    # for i in range(0, 20, 2):
    #     server_DB.logout(f'test{i}')
    #
    # print(server_DB.login_history('test2'))

    # contacts = server_DB.contacts('test1')
    #
    # for contact in contacts:
    #     print(contact)
    #
    # for i in range(2, 18, 2):
    #     server_DB.add_contact('test1', f'test{i}')

