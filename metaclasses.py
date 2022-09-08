import dis

from pprint import pprint

class ServerVerifier(type):
    '''метакласс контроля сервера'''
    def __init__(cls, clsname, bases, clsdict):
        # cls - экземпляр метакласса или класс, создание которого управляется метаклассом
        # bases - иные классы-предки (от которых можно наследоваться)
        # clsdict - словарь методов класса, определяемого метаклассом
        methods = []  # методы, LOAD_GLOBALвызываемые при создании класса Server
        methods2 = [] # методы LOAD_METHOD
        attrs = []    # атрибуты функций класса Server
        for func in clsdict:
            # перебор метдов класса Server
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    # разбор выдачи disassembler'а
                    print(i)
                    if i.opname == "LOAD_GLOBAL":
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == "LOAD_METHOD":
                        if i.argval not in methods2:
                            methods2.append(i.argval)
                    elif i.opname == "LOAD_ATTR":
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        # import pdb; pdb.set_trace()
        print('_methods_' * 5)
        pprint(methods)
        print('_methods2_' * 5)
        pprint(methods2)
        print('_attrs_' * 7)
        pprint(attrs)
        print(30 * '_')
        if 'connect' in methods or 'connect' in methods2:
            raise TypeError('connect() method is not allowed in Server class')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('при инциализации сокета использовать атрибуты SOCK_STREAM и AF_INET')
        super().__init__(clsname, bases, clsdict)

class ClientVerifier(type):
    # метакласс контроля клиента
    def __init__(cls, clsname, bases, clsdict):
        # cls - экземпляр метакласса, т.е. создаваемый класс ClientSender или ClientReader
        # clsname - имя экземпляра метакласса или, что то же, управляемого им класса
        # clsdict - словарь метдов клиентского класса
        # {'__classcell__': <cell at 0x000001E81405FC40: ClientVerifier object at 0x000001E8145D2020>,
        # '__init__': <function ClientSender.__init__ at 0x000001E814888310>,
        # '__module__': '__main__',
        # '__qualname__': 'ClientSender',
        # 'create_exit_message': <function log_function.<locals>.log_fname at 0x000001E81488BEB0>,
        # 'create_message': <function log_function.<locals>.log_fname at 0x000001E8148B0040>,
        # 'list_available_commands': <function ClientSender.list_available_commands at 0x000001E8148B01F0>,
        # 'run': <function log_function.<locals>.log_fname at 0x000001E8148B0160>}
        methods = []  # методы. используемые в клиентском классе
        attrs = []
        import pdb; pdb.set_trace()
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError as e:
                print(e)
                pass
            except Exception as e:
                pprint(e)
                pass
            else:
                # разбор выдачи disassembler'а
                # import pdb; pdb.set_trace()
                for i in ret:
                    print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        # поиск недопустимых для клиента методов
        print('-methods-' * 7)
        pprint(methods)
        print('-attrs-' * 7)
        pprint(attrs)
        print('-' * 30)
        # import pdb; pdb.set_trace()
        for forbidden_cmd in ('accept', 'listen'):
            if forbidden_cmd in methods:
                raise TypeError('found forbidden method in a class')
        # проверка использования TCP протокола
        # if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
        # if 'get_message' in methods or 'send_message' in methods:
        #     pass
        # else:
        #     raise TypeError('нет признаков исользования протокола TCP клиентским сокетом')
        super().__init__(clsname, bases, clsdict)
