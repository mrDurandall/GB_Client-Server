import subprocess


processes = []

while True:
    action = input('Укажите действие:\n'
                   ' q - выход\n'
                   ' s - запустить сервер\n'
                   ' сs - запустить клиент, отправляющий сообщения\n'
                   ' cr - запустить клиент, читающий сообщения\n'
                   ' x - закрыть все окна\n'
                   ' t <количесвто слушающих> <количество отправляющих> - тестовый вариант\n'
                   ' запускающий сервер и соответствующее количество клиентов')

    if action == 'q':
        break

    elif action == 's':
        processes.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'cs':
        processes.append(subprocess.Popen('python client.py -m send',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'cr':
        processes.append(subprocess.Popen('python client.py -m listen',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'x':
        while processes:
            process = processes.pop()
            process.kill()

    elif action[0] == 't':
        processes.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for _ in range(int(action.split()[1])):
            processes.append(subprocess.Popen('python client.py -m listen', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for _ in range(int(action.split()[2])):
            processes.append(subprocess.Popen('python client.py -m send',
                                              creationflags=subprocess.CREATE_NEW_CONSOLE))

