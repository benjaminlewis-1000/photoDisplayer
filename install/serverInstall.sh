#! /bin/bash
  
# Change apache configurations so that the site contained in this project is the default site. 

sudo apt-get install php5-xmlrpc

ONE_DIR_UP="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"   
PROJECT_ROOT_DIR=$(echo $ONE_DIR_UP | sed 's/\//\\\//g')

read -r -d '' APACHE_CONF_VAR << EOM
<Directory $PROJECT_ROOT_DIR>
   Options Indexes FollowSymLinks
   AllowOverride None
   Require all granted
   AddHandler mod\_python .py # Note the space before .py
   PythonHandler mod\_python.publisher
   PythonDebug on
<\/Directory>
EOM

sudo perl -0777 -p -i -e 's/<Directory \/var\/www.*?<\/Directory>/'"$APACHE_CONF_VAR"'/gs' /etc/apache2/apache2.conf

# Change the document root directory 

read -r -d '' DEFAULT_000_VAR << EOM
DocumentRoot $PROJECT_ROOT_DIR\/site
EOM

echo $DEFAULT_000_VAR
sudo sed -i 's/DocumentRoot \/var\/www\/html/'"$DEFAULT_000_VAR"'/g' /etc/apache2/sites-available/000-default.conf

# Change dir.conf to adapt the order of sites loaded

read -r -d '' MOD_DIR_VAR << EOM
<IfModule mod\_dir.c>
    DirectoryIndex mainPage.php info.php mainPage.html index.html index.cgi index.pl index.php index.xhtml index.htm
<\/IfModule>
EOM

sudo perl -0777 -p -i -e 's/<IfModule mod.*?IfModule>/'"$MOD_DIR_VAR"'/gs' /etc/apache2/mods-available/dir.conf

sudo /etc/init.d/apache2 restart
