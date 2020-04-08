#!/bin/bash
email="ddavo@ucm.es"
pass="L08S2WCxu3f"

myip=$(curl -q "http://v4.ipv6-test.com/api/myip.php")
curl -q "https://tb.netassist.ua/autochangeip.php?l=$email&p=$pass&ip=$myip"
echo

sudo ip tunnel add netassist mode sit remote 62.205.132.12 local $myip ttl 200
sudo ip link set netassist up
sudo ip addr add 2a01:d0:ffff:74ea::2/64 dev netassist
sudo ip route add 2a02:2e02:2d66:1400:cffc:14ca:df53:5368/64 dev netassist
# sudo ip -f inet6 addr
