#FROM nginx:latest

#ARG USER_ID=101825
#ARG GROUP_ID=4222

#RUN groupadd -g $GROUP_ID nginx-user && \
#    useradd -u $USER_ID -g nginx-user -s /bin/bash nginx-user

#RUN chmod -R 755 /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
#    mkdir -p /var/run/nginx && \
#    chown -R nginx-user:nginx-user /var/run/nginx && \
#    chmod -R 755 /var/run/nginx

#COPY default.conf /etc/nginx/conf.d/default.conf

#RUN sed -i 's/user nginx;/user nginx-user;/' /etc/nginx/nginx.conf \
#    sed -i 's/pid        \/var\/run\/nginx.pid;/pid        \/var\/run\/nginx\/nginx.pid;/' /etc/nginx/nginx.conf

#CMD ["nginx", "-g", "daemon off;"]

FROM nginx:latest

# Ajuster les permissions sans changer le propriétaire
#RUN chmod -R 755 /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
#    chmod 755 /var/run && \
#    touch /var/run/nginx.pid && \
#    chmod 644 /var/run/nginx.pid

#RUN groupadd nginxgroup && \
#    usermod -aG nginxgroup nginx && \
#    chown -R root:nginxgroup /media && \
#    chmod -R 755 /media
    

# Copier la configuration personnalisée
COPY default.conf /etc/nginx/conf.d/default.conf

# S'assurer que nginx.conf utilise l'utilisateur nginx
#RUN sed -i 's/user  nginx;/user  nginx;/' /etc/nginx/nginx.conf

# Créer des répertoires pour les fichiers temporaires et le cache si nécessaire
#RUN mkdir -p /var/cache/nginx/client_temp /var/cache/nginx/proxy_temp \
#    /var/cache/nginx/fastcgi_temp /var/cache/nginx/uwsgi_temp /var/cache/nginx/scgi_temp && \
#    chmod 755 /var/cache/nginx/*_temp

# On ne change pas l'utilisateur ici, nginx le fera lui-même au démarrage
CMD ["nginx", "-g", "daemon off;"]

