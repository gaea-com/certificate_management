# 域名ssl证书管理

用于给域名创建ssl证书，目前集成了cloudflare、阿里云、dnspod三家DNS厂商。

主要功能:
* 创建域名证书及通配符证书
* 每次创建的证书有效期为: 90天
* 证书在剩余7天过期时，自动更新证书
* 自动检查https的域名及子域名，并在证书有效期剩余5天时，发送提醒邮件
* 域名解析（添加、修改、暂停）

环境:

python3.7 + mariadb10.4.7 + django2.1.7  + gunicorn

访问地址: http://127.0.0.1/index

后台地址: http://127.0.0.1/ssl-cert-admin

默认后台账号: admin

默认后台密码: admin


## docker-compose方式部署

-  数据库准备
    * mariadb 10.4.7

- 修改环境配置参数

在 docker/docker-compose 目录下编辑docker-compose.yaml文件，填写环境配置对应的值
    
```text
DB_NAME:                # 数据库名称, 默认: ssl_cert
DB_USER:                # 数据库账号, 默认: root
DB_PASSWORD:            # 数据库密码, 默认: root123456
DB_HOST:                # 数据库地址, 默认: 127.0.0.1
DB_PORT:                # 数据库端口, 默认: 3306
ADMINS_EMAIL:           # 管理员邮箱, admin账号对应的邮箱, 默认admin@admin.com
EMAIL_HOST:             # 发送邮件的服务器地址
EMAIL_HOST_USER:        # 发送邮件的邮箱
EMAIL_PASSWORD:         # 发送邮件的邮箱密码
EMAIL_PORT:             # 发送邮件的邮箱服务器端口号
EMAIL_SSL:              # 发送邮件的邮箱是否开启加密, True|False (默认为True)
STAGING:                # 是否使用测试模式创建证书, True: 测试模式, False: 关闭测试模式（用于正式环境）。注: 测试模式下创建的证书不能使用，此模式只适用于代码测试
```

- 启动容器

```text
docker-compose pull
docker-compose up -d
```


## k8s方式部署

-  数据库准备
    * mariadb 10.4.7
    
- 修改环境配置参数

在 docker/open-k8s 目录下编辑cert-deploy.yaml文件，填写对应的环境配置的值

```text
DB_NAME:                # 数据库名称, 默认: ssl_cert
DB_USER:                # 数据库账号, 默认: root
DB_PASSWORD:            # 数据库密码, 默认: root123456
DB_HOST:                # 数据库地址, 默认: 127.0.0.1
DB_PORT:                # 数据库端口, 默认: 3306
ADMINS_EMAIL:           # 管理员邮箱, admin账号对应的邮箱, 默认admin@admin.com
EMAIL_HOST:             # 发送邮件的服务器地址
EMAIL_HOST_USER:        # 发送邮件的邮箱
EMAIL_PASSWORD:         # 发送邮件的邮箱密码
EMAIL_PORT:             # 发送邮件的邮箱服务器端口号
EMAIL_SSL:              # 发送邮件的邮箱是否开启加密, True|False (默认为True)
STAGING:                # 是否使用测试模式创建证书, True: 测试模式, False: 关闭测试模式（用于正式环境）。注: 测试模式下创建的证书不能使用，此模式只适用于代码测试
```

> yaml文件中namespace: domain-cert

- 启动容器

```text
kubectl create -f cert-deploy.yaml
```

## 测试通过
* 浏览器: chrome 版本 73.0.3683.103

 
# License
License is GPLv3
