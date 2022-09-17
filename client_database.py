import sys, os
try:
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Scripts\python.exe")
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Lib\site-packages")
except Exception:
    pass
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import *
from datetime import datetime


class ClientDB:
    class KnownUsers:
        def __init__(self, user_name):
            self.id = None
            self.user_name = user_name

    class MsgHist:
        def __init__(self, sender, receiver, message):
            self.id = None
            self.from_user = sender
            self.to_user = receiver
            self.message = message
            self.dt = datetime.now()

    class Contacts:
        def __init__(self, contact):
            self.id = None
            self.contact_name = contact

    def __init__(self, client_name):
        # each client has its' base
        self.db_engine = create_engine(f'sqlite:///client_{client_name}.db3',
                                        echo=False,
                                        pool_recycle=7200,
                                        connect_args={'check_same_thread': False})
        self.meta = MetaData()

        users_table = Table('known_users', self.meta,
            Column('id', Integer, primary_key=True),
            Column('user_name', String))

        hist_table = Table('history_table', self.meta,
            Column('id', Integer, primary_key=True),
            Column('from_user', String),
            Column('to_user', String),
            Column('message', Text),
            Column('date', DateTime))

        cont_table = Table('contacts', self.meta,
            Column('id', Integer, primary_key=True),
            Column('contact_name', String, unique=True))
        
        self.meta.create_all(self.db_engine)
        mapper(self.KnownUsers, users_table)
        mapper(self.MsgHist, hist_table)
        mapper(self.Contacts, cont_table)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        # очистить контакты, чтобы при запуске получит их с сервера чтобы 
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact_name):
        # add contact
        # import pdb; pdb.set_trace()
        if not self.session.query(self.Contacts).filter_by(contact_name=contact_name).count():
            contact_row = self.Contacts(contact_name)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact_name):
        # delte contact
        self.session.query(self.Contacts).filter_by(contact_name=contact_name).delete()
        self.session.commit()

    
    def add_users(self, user_list):
        # adds known user
        self.session.query(self.KnownUsers).delete()
        for user_name in user_list:
            user_row = self.KnownUsers(user_name)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        # save message to the communication history table
        message_row = self.MsgHist(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        # 'returns contacts'
        return [contact[0] for contact in self.session.query(self.Contacts.contact_name).all()]

    def get_users(self):
        # get users
        return [user[0] for user in self.session.query(self.KnownUsers.user_name).all()]

    def is_known(self, receiver):
        # check receiver is known; is in the KnownUsers table
        if self.session.query(self.KnownUsers).filter_by(user_name=receiver).count():
            return True
        else:
            return False

    def is_contact(self, contact_name):
        # check conctact name in the Contacts table
        if self.session.query(self.Contacts).filter_by(contact_name=contact_name).count():
            return True
        else:
            return False

    def get_messages_list(self, from_whom=None, to_whom=None):
        # returns communication history
        query = self.session.query(self.MsgHist)
        if from_whom:
            query = query.filter_by(from_user=from_whom)
        if to_whom:
            query = query.filter_by(to_user=to_whom)
        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    test_db = ClientDB(f'tester_{datetime.now().strftime("%S")}')
    for u in ['u1', 'u3', 'u7']:
        test_db.add_contact(u)
    test_db.add_contact('u3')
    test_db.add_users(['t1', 't2', 't3'])
    test_db.save_message('t1', 't3', f'hello t3 from t2 {datetime.now().strftime("%H:%M:%S")}')
    test_db.save_message('t3', 't2', f'hello this is the other test message to t2')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.is_known('t1'))
    print(test_db.is_known('t10'))
    print(test_db.get_messages_list(to_whom='t1'))
    print(test_db.get_messages_list(from_whom='t1'))
    print(test_db.del_contact('t5'))
    print(test_db.get_contacts())
