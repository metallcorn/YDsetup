#!/bin/bash

echo "Будет установлен НЕ официальный 
индикатор Яндекс.Диск";

sudo add-apt-repository ppa:slytomcat/ppa 
sudo apt-get update 
sudo apt-get install -y yd-tools
