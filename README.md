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


### Развёртывание

Гайд по развёртыванию: https://www.sinyawskiy.ru/telegramdeploy.html

Конфиг (/etc/supervisor/conf.d/bot.conf):

```
[program:telegram_bot]
command=/etc/supervisor/telegram_bot.sh
user=root
stdout_logfile=/root/repostbot/supervisor.log
stderr_logfile=/root/repostbot/supervisor.log
stopsignal=TERM
autostart=true
autorestart=true
startsecs=10
```

Запуск сервисов: \
`sudo service supervisor restart`

Мониторинг работы: \
`supervisorctl`
