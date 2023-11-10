# Introduction

This is a description of the installation of a Flask LibreOffice rest server, which allows Moodle to use a separate server for document conversion.

Most of the source code for the Flask application is taken from the website [Converting DOCX to PDF using Python](hhttps://michalzalecki.com/converting-docx-to-pdf-using-python/)

# Prerequisites
Before starting this guide, you should have:

* A server with Ubuntu 22.04 installed.
* Nginx installed.

## 0. Add a new user
Create a new non-root user called `flaskrun` and add the new user to the sudo group

```
adduser flaskrun

usermod -aG sudo flaskrun
```

Work with the user account `flaskrun`.

```
su flaskrun
```
Go to the HOME directory, clone the Repositors and move the folder `myproject`.

```
cd ~
git clone https://github.com/miotto/server_fileconverter_flasksoffice.git
mv ~/server_fileconverter_flasksoffice/myproject .
```
## 1. LibreOffice
Install LibreOffice.

```
sudo apt install libreoffice
```
Check if soffice is in the path and a conversion with a [sample file](https://filesamples.com/formats/docx) works.

```
soffice --headless --convert-to pdf sample.docx
```

## 2. Python and Flask
Details on the website [How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04).

Update the local package index and install the packages that will allow us to build our Python environment.

```
sudo apt update
sudo apt upgrade
sudo apt install curl vim
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
```

Installing the python3-venv package.

```
sudo apt install python3-venv
```

Create a virtual environment and activate it. 

```
cd ~/myproject
python3 -m venv myprojectenv
source myprojectenv/bin/activate
```
It will look something like this: `(myprojectenv)flaskrun@host:~/myproject$`.

Install Flask and Gunicorn in your virtual environment.

```
pip install wheel
pip install uwsgi gunicorn flask
```

Check the file `~/myproject/config.py` if the upload directory is set correctly.
Set the IP address `127.0.0.1` in the file `~/myproject/flaskconvert.py`. If you want to test the service from an onther server change the IP `127.0.0.1`  to public IP of your server.

Test the Flask app:

```
python3 flaskconvert.py
```

To test, execute the following command from another terminal on the same server. 

```
curl -F 'file=@/home/flaskrun/sample1.docx' http://127.0.0.1:5000/upload
```
Output

```
{"result":{"pdf":"/upload/pdf/sample1.pdf","source":"/upload/source/sample1.docx"}}
```
If everything is ok, the result file is in folder `~/myproject/tmp/pdf`.

To test from another server, the IP address of the server must be set in the `flaskconvert.py` file.

## 3. Gunicorn
Check if gunicorn is working correctly.

```
gunicorn --workers=4 --bind=127.0.0.1:5000 -m 007 wsgi:app
```

Output

```
[2021-02-17 15:44:51 +0000] [14095] [INFO] Starting gunicorn 20.0.4
[2021-02-17 15:44:51 +0000] [14095] [INFO] Listening at: http://127.0.0.1:5000 (14095)
[2021-02-17 15:44:51 +0000] [14095] [INFO] Using worker: sync
[2021-02-17 15:44:51 +0000] [14097] [INFO] Booting worker with pid: 14097
[2021-02-17 15:44:51 +0000] [14098] [INFO] Booting worker with pid: 14098
[2021-02-17 15:44:51 +0000] [14099] [INFO] Booting worker with pid: 14099
[2021-02-17 15:44:51 +0000] [14100] [INFO] Booting worker with pid: 14100
```

Test with the above curl command.

```
curl -F 'file=@/home/flaskrun/sample1.docx' http://127.0.0.1:5000/upload
```
(If you bind gunicorn to an IP other than 127.0.0.1 change IP 127.0.0.1 to your server IP address)



Create a systemd service unit file `flaskrun.service`.

```
sudo vi /etc/systemd/system/flaskrun.service
```

```
[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=flaskrun
Group=flaskrun

WorkingDirectory=/home/flaskrun/myproject
ExecStart=/home/flaskrun/myproject/myprojectenv/bin/gunicorn --workers=4 --bind=127.0.0.1:5000 -m 007 wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Start the Gunicorn service and enable it.

```
sudo systemctl start flaskrun
sudo systemctl enable flaskrun
```

Check the status.

```
sudo systemctl status flaskrun
```

Output

```
flaskrun.service - Gunicorn instance to serve myproject
     Loaded: loaded (/etc/systemd/system/flaskrun.service; disabled; vendor preset: enabled)
     Active: active (running) since Wed 2021-02-17 15:51:54 UTC; 33min ago
   Main PID: 14122 (gunicorn)
      Tasks: 5 (limit: 4915)
     Memory: 72.5M
     CGroup: /system.slice/flaskrun.service
             ├─14122 /home/flaskrun/myproject/myprojectenv/bin/python3 /home/flaskrun/myproject/myprojectenv/bin/gunicorn --workers=4 --bind=127.0.0.1:5000 -m 007 wsgi:app
             ├─14124 /home/flaskrun/myproject/myprojectenv/bin/python3 /home/flaskrun/myproject/myprojectenv/bin/gunicorn --workers=4 --bind=127.0.0.1:5000 -m 007 wsgi:app
             ├─14125 /home/flaskrun/myproject/myprojectenv/bin/python3 /home/flaskrun/myproject/myprojectenv/bin/gunicorn --workers=4 --bind=127.0.0.1:5000 -m 007 wsgi:app
             ├─14126 /home/flaskrun/myproject/myprojectenv/bin/python3 /home/flaskrun/myproject/myprojectenv/bin/gunicorn --workers=4 --bind=127.0.0.1:5000 -m 007 wsgi:app
             └─14127 /home/flaskrun/myproject/myprojectenv/bin/python3 /home/flaskrun/myproject/myprojectenv/bin/gunicorn
```

## 4. Nginx

The basic Nginx settings.

```
sudo vi /etc/nginx/nginx.conf
```

```
worker_processes 1;

user nobody nogroup;
# 'user nobody nobody;' for systems with 'nobody' as a group instead
error_log  /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
  worker_connections 1024; # increase if you have lots of clients
  accept_mutex off; # set to 'on' if nginx worker_processes > 1
  # 'use epoll;' to enable for Linux 2.6+
  # 'use kqueue;' to enable for FreeBSD, OSX
}

http {
        include /etc/nginx/mime.types;
        # fallback in case we can't determine a type
        default_type application/octet-stream;
        access_log /var/log/nginx/access.log combined;
        sendfile on;

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
}
```

Tell Nginx to listen on the default port 80. Let’s also tell it to use this block for requests for our server’s domain name or IP address. Replace the placeholder SERVER-NAME-OR-IP with the correct value.

```
sudo vi /etc/nginx/sites-available/flaskrun
```

```
upstream app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # for UNIX domain socket setups
    # server unix:/tmp/gunicorn.sock fail_timeout=0;

    # for a TCP configuration
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    client_max_body_size 1G;

    # set the correct host(s) for your site
    server_name SERVER-NAME-OR-IP;

    keepalive_timeout 5;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        # we don't want nginx trying to do something clever with
        # redirects, we set the Host: header above already.
        proxy_redirect off;
        proxy_pass http://app_server;

    }
}
```

Disable the Nginx `default` server block.

```
sudo rm -rf /etc/nginx/sites-enabled/default
```

Enable the Nginx `flaskrun` server block.

```
sudo ln -s /etc/nginx/sites-available/flaskrun /etc/nginx/sites-enabled/
```

Restart the Nginx process to read the new configuration.

```
sudo systemctl restart nginx
```

Test locally and/or from the Moodle server using the above curl command.

```
curl -F 'file=@/home/flaskrun/sample1.docx' http://SERVER-NAME-OR-IP/upload
```

**Attention! Set the server's firewall to only allow requests from the Moodle server on port 80.**

## 5. Privacy
To ensure data protection, a cron job can be created that deletes the converted files after a certain time.

Create a shell script.

```
sudo vi /root/delete_files_flask.sh
```

```
#!/bin/bash

uploads_dir=/home/flaskrun/myproject/tmp
retention_time=10
find ${uploads_dir} -type f -mmin +${retention_time} -exec rm {} \;
```

Add an entry in the Contab.

```
sudo crontab -e
```

```
* * * * * /bin/sh /root/delete_files_flask.sh
```

## Useful links

[Converting DOCX to PDF using Python](hhttps://michalzalecki.com/converting-docx-to-pdf-using-python/)

[How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04)
