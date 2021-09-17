from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql

load_dotenv()

configs = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PWD')
}

def create_table():
    conn = psycopg2.connect(**configs)
    cur = conn.cursor()

    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS animes (
                id BIGSERIAL PRIMARY KEY,
                anime VARCHAR(100) NOT NULL UNIQUE,
                released_date VARCHAR NOT NULL,
                seasons INTEGER NOT NULL
            );
        '''
    )

    conn.commit()
    cur.close()
    conn.close()


class Anime:

    def __init__(self, data) -> None:
        self.id, self.anime, self.released_data, self.seasons = data

    @staticmethod
    def save(data):

        create_table()

        expected_keys = ['anime', 'released_date', 'seasons']
        send_keys = []

        for key, value in data.items():

            if key not in expected_keys:
                send_keys.append(key)

        if len(send_keys) > 0:
            return send_keys

        conn = psycopg2.connect(**configs)
        cur = conn.cursor()

        columns = [sql.Identifier(key) for key in data.keys()]
        values = [sql.Literal(value) for value in data.values()]

        query = sql.SQL(
            '''
                INSERT INTO
                    animes (id, {columns})
                VALUES
                    (DEFAULT, {values})
                RETURNING *;
            '''
        ).format(
            columns=sql.SQL(',').join(columns),
            values=sql.SQL(',').join(values)
        )

        cur.execute(query)

        data_result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        anime = Anime(data_result).__dict__

        return anime


    @staticmethod
    def get_all():

        create_table()

        conn = psycopg2.connect(**configs)
        cur = conn.cursor()

        cur.execute('SELECT * FROM animes')
        data_result = cur.fetchall()

        conn.commit()
        cur.close()
        conn.close()

        animes = [Anime(anime_data).__dict__ for anime_data in data_result]

        return animes


    @staticmethod
    def get_by_id(id):

        conn = psycopg2.connect(**configs)
        cur = conn.cursor()

        cur.execute('SELECT * FROM animes WHERE id=(%s);', (id, ))
        data_result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        anime = Anime(data_result).__dict__

        return anime


    @staticmethod
    def update(id, data):

        expected_keys = ['anime', 'released_date', 'seasons']
        send_keys = []

        for key, value in data.items():

            if key not in expected_keys:
                send_keys.append(key)

        if len(send_keys) > 0:
            return send_keys

        conn = psycopg2.connect(**configs)
        cur = conn.cursor()

        columns = [sql.Identifier(key) for key in data.keys()]
        values = [sql.Literal(value) for value in data.values()]

        query = sql.SQL(
            '''
                UPDATE
                    animes
                SET
                    ({columns}) = row({values})
                WHERE
                    id={id}
                RETURNING *;
            '''
        ).format(
            id=sql.Literal(str(id)),
            columns=sql.SQL(',').join(columns),
            values=sql.SQL(',').join(values)
        )

        cur.execute(query)
        data_result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        updated_anime = Anime(data_result).__dict__

        return updated_anime


    @staticmethod
    def delete(id):

        conn = psycopg2.connect(**configs)
        cur = conn.cursor()

        cur.execute('SELECT * FROM animes WHERE id=(%s);', (id, ))
        data_result = cur.fetchone()

        if len(data_result) == 0:
            return {'error': 'Not Found'}, 404

        query = '''
                DELETE FROM
                    animes
                WHERE
                    id=(%s);
            '''
        
        cur.execute(query, (id,))

        conn.commit()
        cur.close()
        conn.close()
