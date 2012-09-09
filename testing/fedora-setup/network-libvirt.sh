#!/bin/bash

for net in net/swan*
do
  if [ ! -d /sys/class/$net ];
  then
     sudo virsh net-create $net
     echo $net created and activated
  else
     echo $net already exists - not created
  fi
done
