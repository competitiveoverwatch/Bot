1. Copy all services/timers
    * `cp reboot.service /etc/systemd/system`
    * `cp reboot.timer /etc/systemd/system`
    * `cp bot.service /etc/systemd/system/`
    * `cp update.service /etc/systemd/system`
2. `systemctl daemon-reload`
3. Enable all services/timers
    * `systemctl enable reboot.timer`
    * `systemctl enable bot.service`
    * `systemctl enable update.service`
4. Start services/timers
    * `systemctl start reboot.timer`
    * `systemctl start bot.service`
    * `systemctl start update.service`