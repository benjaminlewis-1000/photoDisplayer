# Webserver container with CGI python script
# Using RHEL 7 base image and Apache Web server
# Version 1

# Pull the rhel image from the local repository
FROM php:7.0-apache
USER root

MAINTAINER Maintainer_Name

RUN apt-get update 
RUN apt-get install vim -y

# Fix per https://bugzilla.redhat.com/show_bug.cgi?id=1192200 
# RUN yum -y install deltarpm yum-utils --disablerepo=*-eus-* --disablerepo=*-htb-* \
    # --disablerepo=*-ha-* --disablerepo=*-rt-* --disablerepo=*-lb-* --disablerepo=*-rs-* --disablerepo=*-sap-*

# RUN yum-config-manager --disable *-eus-* *-htb-* *-ha-* *-rt-* *-lb-* *-rs-* *-sap-* > /dev/null


# Update image
# RUN yum update -y
# RUN yum install httpd procps-ng MySQL-python -y

# Add configuration file
ADD action /var/www/cgi-bin/action
# RUN echo "PassEnv DB_SERVICE_SERVICE_HOST" >> /etc/httpd/conf/httpd.conf
# RUN chown root:apache /var/www/cgi-bin/action
# RUN chmod 755 /var/www/cgi-bin/action
RUN echo "The Web Server is Running" > /var/www/html/index.html
EXPOSE 80
# docker run -it -v /home/lewis/gitRepos/photoDisplayer/site/:/var/www/html webserver  bash

ENV APACHE_CONF_VAR  \
<Directory /var/www> \\n\
   Options Indexes FollowSymLinks \\n\
   AllowOverride None \\n\
   Require all granted \\n\
   AddHandler mod_python .py # Note the space before .py \\n\
   PythonHandler mod_python.publisher \\n\
   PythonDebug on \\n\
</Directory> 

RUN echo -e $APACHE_CONF_VAR

RUN cp /etc/apache2/apache2.conf /etc/apache2/apache.conf.bk

RUN perl -0777 -p -i -e 's|<Directory /var/www.*?</Directory>|'"$APACHE_CONF_VAR"'|gs' /etc/apache2/apache2.conf

# Change the document root directory 

# No longer necessary
# ENV DEFAULT_000_VAR DocumentRoot $PROJECT_ROOT_DIR/site
# sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.bk
# echo $DEFAULT_000_VAR
# sudo sed -i "s|DocumentRoot /var/www/html|${DEFAULT_000_VAR}|g" /etc/apache2/sites-available/000-default.conf

# # Change dir.conf to adapt the order of sites loaded

ENV MOD_DIR_VAR \
<IfModule mod\_dir.c> \\n\
    DirectoryIndex controlPanel.php mainPage.php info.php mainPage.html index.html index.cgi index.pl index.php index.xhtml index.htm \\n\
<\/IfModule>

RUN cp /etc/apache2/mods-available/dir.conf /etc/apache2/mods-available/dir.conf.bk

RUN echo -e $MOD_DIR_VAR

RUN perl -0777 -p -i -e 's|<IfModule mod.*?IfModule>|'"$MOD_DIR_VAR"'|gs' /etc/apache2/mods-available/dir.conf

# # Install Python mod
RUN apt-get install libapache2-mod-python -y
RUN a2enmod python

# Clean up after apt-get installs 

ADD php.ini /usr/local/etc/php/php.ini

# Add dependencies for XMLRPC
RUN apt-get install libxml2-dev -y
RUN docker-php-ext-install xmlrpc
# RUN apt-get install php-xmlrpc -y

RUN apt-get install iputils-ping -y
# RUN apt-get install netstat -y
RUN apt-get install nmap -y

RUN rm -rf /var/lib/apt/lists/*
# sudo /etc/init.d/apache2 restart

# # Start the service
# CMD ["-D", "FOREGROUND"]
# ENTRYPOINT ["/usr/sbin/httpd"]

# FROM php:7.0-apache

# # Add configuration file
# ADD action /var/www/cgi-bin/action
# RUN echo "PassEnv DB_SERVICE_SERVICE_HOST" >> /etc/httpd/conf/httpd.conf
# RUN chown root:apache /var/www/cgi-bin/action
# RUN chmod 755 /var/www/cgi-bin/action
# RUN echo "The Web Server is Running" > /var/www/html/index.html
# EXPOSE 80

# docker run  \
#     --hostname Drone \
#     --env GITLAB_OMNIBUS_CONFIG="external_url 'http://Drone/'; gitlab_rails['lfs_enabled'] = true;" \
#     --publish 443:443 --publish 8080:80 --publish 2222:22 \
#     --restart always \
#     --volume /srv/gitlab/config:/etc/gitlab \
#     --volume /srv/gitlab/logs:/var/log/gitlab \
#     --volume /srv/gitlab/data:/var/opt/gitlab \
#     -d \
#     gitlab/gitlab-ce:latest