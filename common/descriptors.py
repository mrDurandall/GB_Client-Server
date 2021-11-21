class CorrectPort:
    '''
    Дескриптор, проверяющий корректность номера порта при установке.
    '''

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            raise ValueError("Некорректный номер порта")
        instance.__dict__[self.my_attr] = value

    def __set_name__(self, owner, attribute_name):
        self.my_attr = attribute_name
