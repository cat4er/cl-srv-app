# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
# в байтовое и выполнить обратное преобразование (используя методы encode и decode).

a = "разработка".encode('utf-8')
b = "администрирование".encode('utf-8')
c = "protocol".encode('utf-8')
print(type(a))
print(type(b))
print(type(c))
print(a.decode('utf-8'))
print(b.decode('utf-8'))
print(c.decode('utf-8'))

# <class 'bytes'>
# <class 'bytes'>
# <class 'bytes'>
# разработка
# администрирование
# protocol