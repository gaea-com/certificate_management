#!/usr/bin/env bash

# django 启动脚本
# 使用trap命令捕获信号和执行命令

set -ex
set -u

cd $WEB_DIR || {
    echo "没有 \$WEB_DIR 目录"
    exit 0
}

# 创建日志目录
[ ! -d ${WEB_DIR}/logs ] && mkdir -p ${WEB_DIR}/logs || echo "dir: ${WEB_DIR}/logs exists"
[ ! -f ${WEB_DIR}/logs/info.log ] && touch ${WEB_DIR}/logs/info.log || echo "file: ${WEB_DIR}/logs/info.log exists"


# 退出容器
container_stop() {
    echo "container stop"
    exit 0
}

# nginx配置
nginx_conf() {
    [ -d "/etc/nginx/conf.d" ] || mkdir -p /etc/nginx/conf.d
    cp -f ${WEB_DIR}/docker/nginx/ssl_cert.conf /etc/nginx/conf.d/
}


start_django() {
    crond

    # 关闭django DEBUG模式
    sed -i 's/^DEBUG = True/DEBUG = False/g' ${WEB_DIR}/new_ssl_cert/settings.py

    # 数据迁移
    python3 manage.py makemigrations
    python3 manage.py migrate

    # 静态文件收集
    python3 manage.py collectstatic --no-input &>/dev/null

    # 添加定时计划
    python3 manage.py crontab add

    # 自动创建admin账号
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', '${ADMINS_EMAIL}', 'admin')" | python manage.py shell &>/dev/null | echo "create default account: admin"

    gunicorn new_ssl_cert.wsgi:application -w 2 -b 0.0.0.0:8000 --log-file ${WEB_DIR}/logs/gunicorn.log
}

nginx_conf
start_django

# 捕获到2(SIGINT) 9(SIGKILL) 15(SIGTERM)信号后，执行service_start函数
trap container_stop 2 9 15

while true; do
    sleep 5
done
