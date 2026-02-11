import os
import time
import psycopg as ps
from psycopg.errors import OperationalError
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

_model = None


def get_model():
    """
    Lazy initialization of SentenceTransformer.
    Model is loaded ONLY when need encode().
    """
    global _model
    if _model is None:
        model_cache = os.getenv("MODEL_CACHE_DIR", "/tmp/models")
        os.makedirs(model_cache, exist_ok=True)

        _model = SentenceTransformer(
            "lang-uk/ukr-paraphrase-multilingual-mpnet-base",
            cache_folder=model_cache
        )
    return _model

BATCH_SIZE = 30
RETRY_LIMIT = 3
RETRY_BACKOFF = 2

def connect_with_retry():
    # Trying to connect in RETRY_LIMIT number of attempts
    for attempt in range(RETRY_LIMIT):
        try:
            conn = ps.connect(DATABASE_URL)
            print("Connected to DB.")
            return conn
        except OperationalError as e:
            print(f"DB connection failed ({attempt+1}/{RETRY_LIMIT}). Retrying… Error:", e)
            # Putting a timeout to meet the Aiven free plan connection limits
            time.sleep(RETRY_BACKOFF)

    raise RuntimeError("Cannot reconnect to the database after several attempts.")


def fetch_batch(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, overview
            FROM film
            WHERE id NOT IN (SELECT film_id FROM vectors)
              AND overview IS NOT NULL
            ORDER BY id
            LIMIT %s
            """,
            (BATCH_SIZE,)
        )
        return cur.fetchall()


def insert_batch(conn, rows):
    with conn.cursor() as cur:
        for film_id, vector in rows:
            vector_str = '[' + ','.join(map(str, vector)) + ']'
            cur.execute(
                "INSERT INTO vectors (film_id, embedding) VALUES (%s, %s)",
                (film_id, vector_str)
            )

    conn.commit()


def batch_encode(texts):
    return get_model().encode(texts, batch_size=32)

# Main function
def process_overviews():
    print("Starting vectorization job…")

    # Connecting to database on aiven server
    conn = connect_with_retry()

    while True:
        try:
            # Trying to fetch 30 records per time to satisfy connection query data limit
            rows = fetch_batch(conn)
        except OperationalError:
            # Reconnecting in a case of error
            print("Lost connection while fetching. Reconnecting…")
            conn = connect_with_retry()
            continue

        if not rows:
            break

        texts = [text for (_id, text) in rows]

        # Encoding 30 vectors at ones
        vectors = get_model().encode(texts, batch_size=32)
        batch_to_insert = [
            (rows[i][0], vectors[i])
            for i in range(len(rows)) ]


        for attempt in range(RETRY_LIMIT):
            try:
                # Safe saving them one by one
                insert_batch(conn, batch_to_insert)
                print(f"Saved batch of {len(batch_to_insert)} vectors.")
                break
            except OperationalError:
                print(f"Lost connection during insert (attempt {attempt+1}). Reconnecting…")
                conn = connect_with_retry()
            except Exception as e:
                # In case of server failure setting a time out before trying again
                print(f"Batch insert failed: {e}")
                time.sleep(RETRY_BACKOFF)

        time.sleep(0.3)

    conn.close()
    print("Job finished.")

