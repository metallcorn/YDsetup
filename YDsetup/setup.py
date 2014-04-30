#!/usr/bin/python
# -*- coding: utf-8 -*-

import os #для ииспользования средств ОС, для выполнения внешних скриптов
import sys
import subprocess
import commands
import shutil #для копирования файлов и создания папок
import urllib2

from gi.repository import Gtk

home_folder = os.getenv('HOME') + "/"

#проверка подключения к интернету
def internet_on():
    try:
        response=urllib2.urlopen('http://www.yandex.ru/',timeout=1)
        return True
    except: 
        return False

def critical_err(message_text):
    critical_message.set_text(message_text)
    critical_win.show_all()
    critical_win.connect("delete-event", Gtk.main_quit)

def error_message(message_text):
    Err_message.set_text(message_text)
    err_msg.show_all()
    err_msg.connect("delete-event", Gtk.main_quit)

def close_app():
    window.destroy()
    install_dialog.destroy()
    err_msg.destroy()
    critical_win.destroy()
    sys.exit(0)

#функция для открытия терминала с устновкой нужного пакета
def install_software(package):
    global retcode
    script_path = os.getcwd() + "/install/" + package
    command = ('x-terminal-emulator -e "/bin/sh ' + script_path + '"')
    retcode = subprocess.check_call(command, shell=True) 
    if retcode == 0:
        return True
    else:
        critical_err("ERROR! не смог запустить установку пакета")
        return False

#проверяет установлен ли нужный пакет в системе через dpkg
def check_software(package):
    try:
        soft_status = os.popen('dpkg -l | grep ' + package ).read()
        if (soft_status[0:2] == "ii"):
            print "Пакет "+ package + " найден на компьютере"
            return True
        else:
            print "ERROR, пакет " + package + " не установлен на компьютере"
            return False
    except:
        critical_err("ERROR! Ошибка на этапе проверки утановленного ПО \n проверка выполняется средствами dpkg")
        print "ERROR! не смог проверить статус установки пакета"
        sys.exit(9)

#добавляет файл в автозагрузку
def autostart_app(filename):
    autostart_path = os.getenv('HOME') + "/.config/autostart/"
    if os.path.exists(autostart_path):
        print "путь автозагрузки уже существует"
    else:
        create_folder(autostart_path)
        
    file1 = os.getcwd() + "/autostart/" + filename
    file2 = autostart_path + filename
    print ("копируем " + file1 + "\n в " + file2)
    try:
        shutil.copy2(file1, file2)
        return True
    except:
        print "ERROR, не смог добавить " + filename + " в автозагрузку"
        return False

#получение токена средствами консольного клиента yandex-disk        
def get_token():
    token = "yandex-disk token --password='" + passwd_entry.get_text() + "' " + username_entry.get_text()
    print token
    proc = subprocess.Popen(token, shell=True)
    out, err = proc.communicate()
    
    if (proc.returncode != 0):
        error_message("Ошибка входа, проверьте логин/пароль")
        return False
    else:
        return True
    #print out, err
    print ("код выполнения: " + proc.returncode)

def sync_fonder_set():
    global sync_folder
    if (str(folder_select.get_filename()) == "None"):
        sync_folder = home_folder + "Yandex.Disk"
    else:
        sync_folder = folder_select.get_filename()
    
    if os.path.exists(sync_folder):
        print "путь " + sync_folder + " уже существует"
        return True
    else:
        if (create_folder(sync_folder) == True):
            return True

    print ("выраная папка для синхронизации" + sync_folder)

def create_folder(folder_name):
    try:
        os.makedirs(folder_name, 0775)
        print ("была создана папка " + folder_name)
        return True
    except:
        error_message("Невозможно создать папку " + folder_name )
        return False

def make_config():
    config_path = home_folder + ".config/yandex-disk/"
    #проверяем папку для конфига
    if os.path.exists(config_path):
        print "путь для хранения конфигов уже существует"
    else:
        create_folder(config_path)
    #Собираем конфиг
    try:
        config_file = open(config_path + "config.cfg", "w")
        config_file.write('auth="' + config_path + 'passwd"\ndir="' + sync_folder + '\nproxy="no"')
        config_file.close()
        print ("конфиг собран\n") 
        return True
    except:
        critical_err("Не удалось собрать конфигурационный файл")
        print "конфиг не собрался"
        return False


def on_exit_clicked(button):
    print "Exit clicked"
    close_app()
    
def install(button):
    print "install clicked"
    install_software("disk.sh")
    close_app()

def cancel(button):
    close_app()
    
def err_close(button):
    err_msg.hide()
    
def setup_close(button):
    close_app()

def critical_close(button):
    close_app()



#работа самой главной кнопки
def on_save_clicked(button):
    global setup_err_count
    setup_err_count = 0
    if (get_token() == True):
        if (sync_fonder_set() == True):
            if (make_config() == True):
            #отрабатываем переключатели
                if (autostart.get_active() == True): 
                    if (autostart_app("Yandex.Disk.desktop") != True):
                        setup_err_count+=1
                if (indicator_install.get_active() == True):
                    if (install_software("indicator.sh") != True):
                        setup_err_count+=1
                        
                    if (autostart_app("Yandex.Disk-indicator.desktop") != True):
                        setup_err_count+=1
                if (setup_err_count != 0):
                    error_message("Настройка завершилась с ошибками")
                else:
                    success_win.show_all()
                    success_win.connect("delete-event", Gtk.main_quit)
            


builder = Gtk.Builder()
builder.add_from_file("main.ui")

#подключаем все окошки
install_dialog = builder.get_object("YDinstall")
window = builder.get_object("YDsetup")
err_msg = builder.get_object("YDerror")
success_win = builder.get_object("YDsuccess")
critical_win = builder.get_object("YDcritical")

#подключаем все активные элементы
username_entry = builder.get_object( 'username')
passwd_entry = builder.get_object( 'passwd')
autostart = builder.get_object ( 'autostart' )
indicator_install = builder.get_object ( 'indicator_install' )
folder_select = builder.get_object("folder_select")
critical_message = builder.get_object("critical_message")
Err_message = builder.get_object("Err_message")

#обработчики событий с формы
handlers = {
            "on_save_clicked" : on_save_clicked,
            "on_exit_clicked" : on_exit_clicked,
            "on_install_bt_clicked" : install,
            "on_cancel_bt_clicked" : cancel,
            "on_err_close_bt_clicked" : err_close,
            "on_exit_button_clicked" : setup_close,
            "on_critical_bt_clicked" : critical_close
        }

if __name__ == "__main__":
    if (internet_on() == False):
        critical_err("Проверьте подключение к интернету")
    else:
        if (check_software("yandex-disk") == False):
            install_dialog = builder.get_object("YDinstall")
            install_dialog.show_all()
            install_dialog.connect("delete-event", Gtk.main_quit)
        else:
            window.show_all()
            window.connect("delete-event", Gtk.main_quit)
        
    builder.connect_signals(handlers)
    Gtk.main()
