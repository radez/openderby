#vim /boot/config.txt #disable-overscan=1 # black border fix
yum install python-cherrypy python-flask python-flask-sqlalchemy python-flask-admin python-rpi-gpio i2c-tools i2c-tools-python mariadb-server MySQL-python
#vim /etc/modprobe.d/blacklist.conf # remove i2c-dev
modprobe ic2-dev
ln -sf /lib/systemd/system/multi-user.target /etc/systemd/system/default.target

