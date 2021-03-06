#!/bin/sh
 
### BEGIN INIT INFO
# Provides:          autovelux
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Read redis queue and switch velux if too hot/cold
# Description:       Read redis queue and switch velux
### END INIT INFO
 
# Change the next 3 lines to suit where you install your script and what you want to call it
DIR=/usr/local/bin
DAEMON=${DIR}/velux_auto.py
DAEMON_NAME=velux_auto.py
 
# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root
 
# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid
 
. /lib/lsb/init-functions
 
do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    /sbin/start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --startas $DAEMON
#    start-stop-daemon --start --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER  --startas ${DAEMON}
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    /usr/local/bin/all_close.sh
    /sbin/start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}
 
case "$1" in
 
    start|stop)
        do_${1}
        ;;
 
    restart|reload|force-reload)
        do_stop
        do_start
        ;;
 
    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;
    *)
        echo "Usage: /etc/init.d/$DEAMON_NAME {start|stop|restart|status}"
        exit 1
        ;;
 
esac
exit 0
