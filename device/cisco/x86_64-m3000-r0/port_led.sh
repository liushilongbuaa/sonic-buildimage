#! /bin/bash

function daemon_mode {

  sleep 60

  while true
  do
    /usr/bin/bcmcmd -t 60 "cint /usr/share/sonic/platform/port_led.cint"
    sleep 3
  done

}

daemon_mode </dev/null >/dev/null 2>&1 &
disown
