from django.db import connection
import hashlib
import time

def executeSQL(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def only_executeSQL(sql):

    with connection.cursor() as cursor:
        cursor.execute(sql)

    return cursor.rowcount

def encoder_22_characters(txt, length=22):
    # This is just a hash for debugging purposes.
    #    It does not need to be unique, just fast and short.
    txt = (str(txt) + str(time.time())).encode("utf-8")
    hash = hashlib.sha1()
    hash.update(txt)
    return hash.hexdigest()[:length]