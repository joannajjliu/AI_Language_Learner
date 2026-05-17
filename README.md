# AI_Language_Learner

On local:

start postgres db:

```
docker compose up -d
```

wipe the database:

```
docker compose down -v
```

start server:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

run python unit tests:

```
python -m unittest discover -s tests -v
```

start frontend:

```
cd frontend
npm install
npm start
```

Video of work in progress:

https://github.com/user-attachments/assets/53c03fc1-5c95-44ee-8370-3db098fe0f2f
