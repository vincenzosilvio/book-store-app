#Accesso al database book_store
psql -U vincenzo -d book_store

#Generare una migrazione
flask db migrate -m "updating Book table"
flask db upgrade


#Elimina righe da una tabella
DELETE FROM nome_tabella;

#Elimina tabella
DROP TABLE IF EXISTS BOOK;