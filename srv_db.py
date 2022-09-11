# import pdb;pdb.set_trace()
import sys
try:
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Scripts\python.exe")
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Lib\site-packages")
except Exception:
    pass
from sqlalchemy import *  # create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import DB_URL
from datetime import datetime

class ServerStorage:
    '''класс представляет сервеную базу данных'''
    class UsersAll:
        '''класс таблица пользователей'''
        def __init__(self, user_name):
            self.user_name = user_name
            self.last_login = datetime.now()
            self.id = None

    class UsersActive:
        '''класс таблица активных ползовтелей'''
        def __init__(self, user_id, ip, port, login_time):
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.logged_at = login_time
            self.id = None

    class LoginHistory:
        '''класс история посещений чата пользователями'''
        def __init__(self, user_id, user_name, logged_at, ip, port):
            self.user_id = user_id
            self.user_name = user_name
            self.logged_at = logged_at
            self.ip = ip
            self.port = port
            self.id = None

    def __init__(self):
        '''процедура создания базы данных'''
        # DB_URL = 'sqlite:///srv_db.db3'
        # echo-аргумент движка позволяет не выводить текст sql-запросов
        # pool_recycle восстанавливает автомаически соединение с базой по истечении указанного срока
        # connect_args управляет отслеживанием потоков, подключающихся к базе; по умолчанию база доступна лишь для одного какого-то потока
        self.engine = create_engine(
            DB_URL,
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread':False})
        self.meta = MetaData()  #MetaData object
        users_table = Table('Users_All', self.meta,
            Column('id', Integer, primary_key=True),
            Column('user_name', String, unique=True),
            Column('last_login', DateTime),)                                            

        users_active_table = Table('Users_Active', self.meta,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('Users_All.id'), unique=True),
            Column('ip', String),
            Column('port', Integer),
            Column('logged_at', DateTime))

        users_login_history_table = Table('Users_LogHist', self.meta,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('Users_All.id')),
            Column('user_name', String),
            Column('ip', String),
            Column('port', Integer),
            Column('logged_at', DateTime))
        # import pdb; pdb.set_trace()
        self.meta.create_all(self.engine)   # creation
        mapper(self.UsersAll, users_table)  # mapping
        mapper(self.UsersActive, users_active_table)
        mapper(self.LoginHistory, users_login_history_table)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()            # session's creation

        self.session.query(self.UsersActive).delete()
        self.session.commit()               # clear active users' table by the new launch

    def user_login(self, user_name, ip_addr, port):
        # фнукция обработки входа пользователя (записи в базу)
        # print(user_name, ip_addr, port)
        query_name = self.session.query(self.UsersAll).filter_by(user_name=user_name)
        if query_name.count():
            # если пользователь уже в базе, обновить время его входа
            user = query_name.first()
            user.last_login = datetime.now()
        else:
            # внесение нового с получением id
            user = self.UsersAll(user_name)
            self.session.add(user)
            self.session.commit()

        # внесение подключившегося в базу активных
        active_user = self.UsersActive(user.id, ip_addr, port, datetime.now())
        self.session.add(active_user)

        # фиксация подключения в истории подключений
        hist_fact = self.LoginHistory(user.id, user_name, datetime.now(), ip_addr, port)
        self.session.add(hist_fact)

        self.session.commit()

    def user_logout(self, user_name):
        # функция обработки отключения пользователя
        user = self.session.query(self.UsersAll).filter_by(user_name=user_name).first()  # get leaving user record
        self.session.query(self.UsersActive).filter_by(user_id=user.id).delete()       # delete from active

        self.session.commit()

    def users_list(self):
        # выборка пользователей и их последних входов в чат
        query =self.session.query(
            self.UsersAll.user_name,
            self.UsersAll.last_login,
        )

        return query.all()

    def active_users_list(self):
        # выборка данных активных пользователей
        query = self.session.query(
            self.UsersAll.user_name,
            self.UsersActive.ip,
            self.UsersActive.port,
            self.UsersActive.logged_at).join(self.UsersAll)
        return query.all()

    def login_history(self, user_name=None):
        # выборка историй входа
        query = self.session.query(
            self.UsersAll.user_name,
            self.LoginHistory.logged_at,
            self.LoginHistory.ip,
            self.LoginHistory.port
        ).join(self.UsersAll)
        if user_name:
            query = query.filter(self.UsersAll.user_name==user_name)
        return query.all()


# debug
if __name__ == '__main__':
    test_base = ServerStorage()
    test_base.user_login('client_1', '192.168.1.4', 8080)
    test_base.user_login('client_2', '192.168.1.5', 7777)
    print('active users')
    print(test_base.active_users_list())

    test_base.user_logout('client_1')
    print('active users after logout')
    print(test_base.active_users_list())

    print('history')
    print(test_base.login_history('client_1'))

    print('all users')
    print(test_base.users_list())
