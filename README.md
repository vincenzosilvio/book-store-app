#Postgresql installation
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres psql
#To run make lint-js/html
sudo apt install nodejs
sudo apt install npm

1) CREATE DATABASE book_store;
2) GRANT ALL PRIVILEGES ON DATABASE book_store TO user_name;


#Accesso al database book_store
psql -U vincenzo -d book_store

flask db init
#Generare una migrazione
flask db migrate -m "updating Book table"
flask db upgrade


#Elimina righe da una tabella
DELETE FROM nome_tabella;

#Elimina tabella
DROP TABLE IF EXISTS BOOK;