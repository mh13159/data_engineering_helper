# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 10:19:08 2023

@author: Muhammad Hamza
"""
from sqlalchemy import create_engine

# Define PostgreSQL connection parameters
def get_postgres_connection_params():
    p_host = ''
    p_port = 5432
    db = ''
    psql_user = ''
    psql_pass = ''
    return p_host, p_port, db, psql_user, psql_pass

# Create a PostgreSQL engine
def create_postgres_engine():
    p_host, p_port, db, psql_user, psql_pass = get_postgres_connection_params()
    engine = create_engine(f'postgresql://{psql_user}:{psql_pass}@{p_host}:{p_port}/{db}')
    return engine