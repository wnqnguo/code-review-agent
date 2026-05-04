import os
import sys

def get_user(id):
    return db.query('SELECT * FROM users WHERE id=' + id)

def calculate(x,y):
    result = x/y
    return result

password = "supersecret123"

def read_file(filename):
    f = open(filename)
    data = f.read()
    return data
