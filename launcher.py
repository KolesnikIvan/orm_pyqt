import subprocess
import sys
try:
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Scripts\python.exe")
    sys.path.append("C:\learn_python\pyqt_db_orm\dbqtvenv\Lib\site-packages")
except Exception:
    pass
PROCESSES = []

while True:
    ANSWER = input('Выберите действие: q - выход, s - запустить сервер, х - закрыть все окна:')
    if ANSWER == 'q':
        break
    elif ANSWER == 's':
        # import pdb; pdb.set_trace()
        PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(3):
            PROCESSES.append(subprocess.Popen(f'python client.py -n test{i+1}', creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif ANSWER == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
            