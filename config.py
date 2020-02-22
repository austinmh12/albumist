import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "`< /dev/urandom tr -dc 'a-zA-Z0-9' | head -c16`"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://zgbakvrmlxpmqq:b6726a650bf313755c5fa6089b09f5560900f36e9839b5d0721e47be96b342e2@ec2-3-230-106-126.compute-1.amazonaws.com:5432/d81aremahv5dg1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False