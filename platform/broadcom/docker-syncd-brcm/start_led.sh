#!/usr/bin/env bash

PLATFORM_DIR=/usr/share/sonic/platform
SYNCD_SOCKET_FILE=/var/run/sswsyncd/sswsyncd.socket
LED_PROC_INIT_SOC=${PLATFORM_DIR}/led_proc_init.soc
PORT_LED_SCRIPT=${PLATFORM_DIR}/port_led.sh

# Function: wait until syncd has created the socket for bcmcmd to connect to
wait_syncd() {
    while true; do
        if [ -e ${SYNCD_SOCKET_FILE} ]; then
            break
        fi
        sleep 1
    done

    # wait until bcm sdk is ready to get a request
    counter=0
    while true; do
        /usr/bin/bcmcmd -t 1 "show unit" | grep BCM >/dev/null 2>&1
        rv=$?
        if [ $rv -eq 0 ]; then
            break
        fi
        counter=$((counter+1))
        if [ $counter -ge 60 ]; then
            echo "syncd is not ready to take commands after $counter re-tries; Exiting!"
            break
        fi
        sleep 1
    done
}

if [[ ! -f "$LED_PROC_INIT_SOC"  && ! -x "$PORT_LED_SCRIPT" ]]; then
   echo "No soc led configuration script found "
   exit 0
fi

# If this platform has an initialization file for the Broadcom LED microprocessor, load it
if [[ ( -r "$LED_PROC_INIT_SOC" || -x "$PORT_LED_SCRIPT" ) && ! -f /var/warmboot/warm-starting ]]; then
    wait_syncd
fi

if [[  -r "$LED_PROC_INIT_SOC"  ]]; then
    /usr/bin/bcmcmd -t 60 "rcload $LED_PROC_INIT_SOC"
elif [[ -x "$PORT_LED_SCRIPT" ]]; then
    supervisorctl start port_led.sh
fi
