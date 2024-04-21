# yumi
 hacking on ai companions

## setup
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## run
```
python main.py ./characters/aurora.json
```

## env vars
make sure you have a `.env` file with the following populated:

```
DISCORD_KEY=
OPEN_AI_BASE_URL=
COMPLETIONS_MODEL=
```