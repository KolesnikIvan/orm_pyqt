import subprocess
import sys
try:
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Scripts\python.exe")
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Lib\site-packages")
except Exception:
    pass

def main():
    PROCESSES = []

    while True:
        action = input('Выберите действие: q - выход, s - запустить сервер, k - запустить клиентов, х - закрыть все окна:')
        if action == 'q':
            break
        elif action == 's':
            import pdb; pdb.set_trace()
            try:
                PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
                input()
            except Exception as e:
                print(e)
                pass
            finally:
                input()
        elif action == 'k':
            print('check there is eonugh users registered on server; ', 'first launch causes keys generation')
            clients_num = 3  # int(input('insert a number of clients to start '))
            for i in range(clients_num):
                import pdb; pdb.set_trace()
                PROCESSES.append(subprocess.Popen(f'python client.py -n test{i+1} -s 1234', creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'x':
            while PROCESSES:
                VICTIM = PROCESSES.pop()
                VICTIM.kill()
                
if __name__ == '__main__':
    import pdb; pdb.set_trace()
    main()