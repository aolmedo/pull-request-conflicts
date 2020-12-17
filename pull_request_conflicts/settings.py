# -*- coding: utf-8 -*-
import os

# DB Settings
DB_NAME = 'ghtorrent_restore'
DB_USER = 'aolmedo'
DB_PASSWORD = ''
DB_HOST = '192.168.1.44'
DB_PORT = '5432'

# Data Settings
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(CURRENT_PATH, '../data')
CONFLICT_MATRIX_PATH = os.path.join(CURRENT_PATH, '../conflict_matrix')