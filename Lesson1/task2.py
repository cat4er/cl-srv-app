# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
# кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

a = b"class"
b = b"function"
c = b"method"

print(type(a))
print(type(b))
print(type(c))
print(a)
print(b)
print(c)
print(len(a))
print(len(b))
print(len(c))

# <class 'bytes'>
# <class 'bytes'>
# <class 'bytes'>
# b'class'
# b'function'
# b'method'
# 5
# 8
# 6