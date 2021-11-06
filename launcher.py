import subprocess


processes = []

while True:
    action = input('Укажите действие:\n'
                   ' q - выход\n'
                   ' s - запустить сервер\n'
                   ' сs - запустить клиент, отправляющий сообщения\n'
                   ' cr - запустить клиент, читающий сообщения\n'
                   ' x - закрыть все окна\n')

    if action == 'q':
        break

    elif action == 's':
        processes.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'cs':
        processes.append(subprocess.Popen('python client.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'cr':
        processes.append(subprocess.Popen('python client.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'x':
        while processes:
            process = processes.pop()
            process.kill()

