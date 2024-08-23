#!/bin/bash

source env/general.env

mkdir -p $BUILD_DIR
sudo mkdir -p $DB_DIR
sudo mkdir -p $BACKUP_DIR

alias k=kubectl

NODE=$HOST

k create namespace $NAMESPACE

k create secret generic -n $NAMESPACE --from-env-file=env/postgres.env db
k create secret generic -n $NAMESPACE --from-env-file=env/rabbit.env rabbit

sed -e 's/%PG_VERSION%/${PG_VERSION}/g' \
    -e 's/%DB_DIR%/${DB_DIR}/g' \
    -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    -e 's/%NODE%/${NODE}/g' \
    k8s/db.yml > $BUILD_DIR/db.yml

sed -e 's/%RABBIT_VERSION%/${PG_VERSION}/g' \
    -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    k8s/rabbit.yml > $BUILD_DIR/rabbit.yml

sed -e 's/%BACKUP_DIR%/${BACKUP_DIR}/g' \
    -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    k8s/auth.yml > $BUILD_DIR/auth.yml

sed -e 's/%BACKUP_DIR%/${BACKUP_DIR}/g' \
    -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    -e 's/%NODE%/${NODE}/g' \
    k8s/admin.yml > $BUILD_DIR/admin.yml

sed -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    -e 's/%NODE%/${NODE}/g' \
    k8s/external.yml > $BUILD_DIR/external.yml

sed -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    k8s/front.yml > $BUILD_DIR/front.yml

sed -e 's/%NAMESPACE%/${NAMESPACE}/g' \
    k8s/admin-front.yml > $BUILD_DIR/admin-front.yml


k create -f $BUILD_DIR/db.yml
k create -f $BUILD_DIR/rabbit.yml
k create -f $BUILD_DIR/auth.yml
k create -f $BUILD_DIR/external.yml
k create -f $BUILD_DIR/front.yml
k create -f $BUILD_DIR/admin.yml
k create -f $BUILD_DIR/admin-front.yml

if [ $ROUTING = "DOMAIN" ] then
  sed -e 's/%DOMAIN%/${DOMAIN}/g' \
    k8s/ingress-domain.yml > $BUILD_DIR/ingress-domain.yml
  k create -f $BUILD_DIR/ingress-domain.yml
else
  cp k8s/ingress-path.yml $BUILD_DIR/ingress-path.yml
  k create -f $BUILD_DIR/ingress-path.yml
fi



