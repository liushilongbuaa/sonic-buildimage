# Get PID, SN, MAC and MAC block size from id sprom
eeprom=/sys/bus/i2c/devices/1-0052/eeprom

if ! [ -r $eeprom ]; then
  echo can not read file $eeprom
  exit 1
fi

od -j 0x22 -N 0x14 -w -t c $eeprom | head -n 1 | awk '{$1=""; gsub("\\\\0","",$0); gsub(" ","",$0); print "PID : " $0 }'
od -j 0x36 -N 0x14 -w -t c $eeprom | head -n 1 | awk '{$1=""; gsub("\\\\0","",$0); gsub(" ","",$0); print "S/N : " $0}'
od -j 0x4a -N 0x10 -w -t c $eeprom | head -n 1 | awk '{$1=""; gsub("\\\\0","",$0); gsub(" ","",$0); print "Part_Number : " $0}'
od -j 0x5a -N 0x4 -w -t c $eeprom | head -n 1 | awk '{$1=""; gsub("\\\\0","",$0); gsub(" ","",$0); print "Part_Revision : " $0}'
od -j 0x72 -N 0x4 -t d2 --endian=big $eeprom | head -n 1 | awk '{print "HW_Revision : " $2 "." $3 }'
od -j 0xb6 -N 0x2 -t u1 $eeprom | head -n 1 | awk '{print "CARD_INDEX : " $2*256+$3}'
od -j 0x10ae -N 0x8 -t u1 $eeprom | head -n 1 | awk '{print "HW_Change_Bit : " $9 }'
od -j 0x10b8 -N 0x6 -t x1 $eeprom | head -n 1 | awk '{print "MAC_BASE : " $2 ":" $3 ":" $4 ":" $5 ":" $6 ":" $7 }'
od -j 0x10be -N 0x2 -t u1 $eeprom | head -n 1 | awk '{print "NUMBER_MAC : " $2*256+$3}'


