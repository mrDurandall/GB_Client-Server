import dis


class ServerVerifier(type):

    def __init__(cls, clsname, bases, clsdict):

        class_methods = []
        class_attributes = []

        for el in clsdict:
            try:
                el_methods = dis.get_instructions(clsdict[el])
            except TypeError:
                pass
            else:
                for method in el_methods:
                    if method.opname == 'LOAD_GLOBAL' and method.argval not in class_methods:
                        class_methods.append(method.argval)
                    elif method.opname == 'LOAD_ATTR' and method.argval not in class_attributes:
                        class_attributes.append(method.argval)

        if 'connect' in class_methods:
            raise TypeError('В серверной части не должен испольхзоваться метод connect')
        if 'AF_INET' not in class_attributes and 'SOCK_STREAM' not in class_attributes:
            raise TypeError('Сокеты должны работать по протоколу TCP')

        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):

    def __init__(cls, clsname, bases, clsdict):

        class_methods = []
        class_attributes = []

        for el in clsdict:
            try:
                el_methods = dis.get_instructions(clsdict[el])
            except TypeError:
                pass
            else:
                for method in el_methods:
                    if method.opname == 'LOAD_GLOBAL' and method.argval not in class_methods:
                        class_methods.append(method.argval)
                    elif method.opname == 'LOAD_ATTR' and method.argval not in class_attributes:
                        class_attributes.append(method.argval)

        if 'accept' in class_methods or 'listen' in class_methods:
            raise TypeError('В клиентской части не должны использоваться функции accept и listen!')
        if 'AF_INET' not in class_attributes and 'SOCK_STREAM' not in class_attributes:
            raise TypeError('Сокеты должны работать по протоколу TCP')

        super().__init__(clsname, bases, clsdict)