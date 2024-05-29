# daikyuu
 fork of ravens' [yumi.](https://github.com/ravens2d/yumi) ravens has different goals from me, but yumi is a personal project, so i wasn't about to burden them with my requests. (that's what forks are for, right? /gen)

basically talOS and character engine are like **right there** but also way too overbuilt for me to try and finish so. uh. yeah

 short term ("i can do this without learning anything new"):
 - port to ollama or kobold.cpp
 - break out generation params into config file (might just use .env tbh, it's there)

 long term ("i would have to learn how to do this"):
 - multiple characters at once via webhooks (this might be what ravens means by "async engagement" tho idk)
 - multimodal?????? maybe????
 - a

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
