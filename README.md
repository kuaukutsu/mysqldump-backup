**mysqldump**
=============

## Install
### Requirements:

Install from requirements.txt
```
pip install -r requirements.txt
```

Install 7zip (for add files to archive before attach to mail)
```
. install p7zip p7zip-plugins
```

Install webdavclient
https://github.com/designerror/webdav-client-python
```
# yum install libcurl-devel
# pip uninstall pycurl
# export PYCURL_SSL_LIBRARY=nss
# pip install pycurl
```

```
$ sudo apt-get install libxml2-dev libxslt-dev python-dev
$ sudo apt-get install libcurl4-openssl-dev python-pycurl 
$ sudo easy_install webdavclient
```

## Settings

Mysql connect (mysql --login-path=local):
```bash
mysql_config_editor set --login-path=local --host=localhost --user=username --password
```

Edit ./mysqldump.cfg
```bash
cp ./mysqldump.cfg.example ./mysqldump.cfg
```

## Run

```bash
/usr/local/bin/python /mysqldump.py -d BASENAME --sendmail=NAMESPACE --encrypt-pass=YOUPASS
```

Help
```bash
/usr/local/bin/python /mysqldump.py --help
```
