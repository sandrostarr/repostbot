# Warpcast Follow Bot

### Run

Installing virtual env: \
`python3 -m venv venv`

Activating: \
`source venv/bin/activate`

Installing all dependencies: \
`pip install -r requirements.txt`

Copying .env.dist file to .env and fill variables


### Cron
 
Верификация выполненных заданий, запускается каждые 3 минуты
`*/3 * * * * /root/repostbot/venv/bin/python3 /root/repostbot/verify_tasks.py`