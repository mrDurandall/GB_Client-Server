from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import datetime


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
            self.user = user_id
            self.id = None

    def __init__(self):

        self.server_engine = create_engine('sqlite:///server-DB.db3', echo=False, pool_recycle=7200)

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

        # TODO
        # message_history_table = Table('message_history', metadata,
        #                               )

        metadata.create_all(self.server_engine)

        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)

        new_session = sessionmaker(bind=self.server_engine)

        self.session = new_session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def login(self, username, ip, port):

        username_in_base = self.session.query(self.AllUsers).filter_by(username=username).first()

        if username_in_base:
            user = username_in_base
            user.last_login = datetime.datetime.now()

        else:
            user = self.AllUsers(username)
            self.session.add(user)
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


if __name__ == '__main__':

    server_DB = ServerDatabase()

    print(server_DB.active_users_list())

    for i in range(0, 20):
        server_DB.login(f'test{i}', '127.0.0.1', 1)

    print(server_DB.users_list())
    print(server_DB.active_users_list())

    for i in range(0, 20, 2):
        server_DB.logout(f'test{i}')

    print(server_DB.users_list())
    print(server_DB.active_users_list())

