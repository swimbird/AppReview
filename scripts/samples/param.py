#!/usr/bin/python

def test1(id, **kwargs):
    print id, kwargs

def test2(*args, **kwargs):
    print args
    print kwargs

def test3(id, name, mail,
          phone = None, addr = None):
    print id, name
    print mail, phone, addr

def test4(id, *args, **kwargs):
    print id
    print args
    print kwargs

if __name__ == "__main__":
    testt = ("a", "b", "c")
    testd = {
        "id"   : "hogehoge",
        "name" : "abcdefg",
        "mail" : "test@example.com",
        }

    test1(**testd)
    test1("foobar", name = "aabbcc")
    test2(*testt, **testd)
    test3(**testd)

#   test4(*testt, **testd) # Error
#   test1(id = "ovwrt", **testd) # Error


# Result:
#     hogehoge {'mail': 'test@example.com', 'name': 'abcdefg'}
#
#     foobar {'name': 'aabbcc'}
#
#     ('a', 'b', 'c')
#     {'mail': 'test@example.com', 'id': 'hogehoge', 'name': 'abcdefg'}
#
#     hogehoge abcdefg
#     test@example.com None None
