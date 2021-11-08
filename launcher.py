import subprocess


processes = []

while True:
    action = input('Укажите действие:\n'
                   ' q - выход\n'
                   ' s - запустить сервер\n'
                   ' с - запустить клиент\n'
                   ' x - закрыть все окна\n'
                   ' t <количесвто> - тестовый вариант\n'
                   ' запускающий сервер и соответствующее количество клиентов')

    if action == 'q':
        break

    elif action == 's':
        processes.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'c':
        processes.append(subprocess.Popen('python client.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif action == 'x':
        while processes:
            process = processes.pop()
            process.kill()

    elif action[0] == 't':
        processes.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for _ in range(int(action.split()[1])):
            processes.append(subprocess.Popen(f'python client.py -n test{_}', creationflags=subprocess.CREATE_NEW_CONSOLE))


