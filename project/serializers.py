import settings
import sqlite3


class Id:
    def __init__(self):
        self.__id = -1

    def __next__(self):
            self.__id += 1
            return self.__id

    def reset(self):
        self.__id = -1


class Serializer:
    def __init__(self):
        self.db_name = settings.DATABASE
        self.__change_list = dict()
        self.__id = Id()

    def __str__(self):
        return self.__class__.__name__.lower()

    @property
    def change_list(self):
        # TODO: Проверить, нужно ли делать change_list статиком
        return self.__change_list

    @change_list.setter
    def change_list(self, value):
        self.__change_list[self.__id] = value

    @change_list.deleter
    def change_list(self):
            self.__change_list = dict()
            self.__id.reset()

    def create(self, **kwargs):
        query = 'insert into %s (' % self
        values = '( '
        for k, v in kwargs.items():
            query += '%s, ' % k
            values += "'%s', " % v
        self.change_list[self.__id] = query[:-2]+') VALUES '+values[:-2]+');'

    def get(self, id_=None):
        # TODO: Протестировать коректность возврата коммита
        if id_:
            self.change_list[self.__id] = 'select * from %s where id = %s; ' % (self, id_)
            result = self.commit()
            if result:
                return result[len(result)]
        return

    def all(self):
        self.change_list[self.__id] = 'select * from %s;' % self
        self.commit()

    def update(self, id_=None, **kwargs):
        if id_:
            query = "UPDATE %s SET id='%s', " % (self, id_)
            for k, v in kwargs.items():
                query += "%s='%s', " % (k, v)
            self.change_list[self.__id] = query[:-2]+";"

    def delete(self, id_):
        self.change_list[self.__id] = "DELETE FROM %s WHERE id='%s'" % (self, id_)

    def commit(self):
        # TODO: Протестировать работу коммита
        # TODO: Протестировать коректность возврата коммита
        # TODO: Перенести вывод ошибки в views
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            response = [cursor.execute(i).fetchall() for i in self.change_list.values()]
            conn.commit()
            conn.close()
            return response[0]
        except sqlite3.Error as e:
            print(e)
            return None

    def rollback(self):
        del self.change_list

if __name__ == '__main__':
    print('Тест работы serializer.py:\n')
    s = Serializer()
    s.update(id_=10, name='name', date='22-04-2016 20:40', mail='lubchenko@wdc.org.ua')
