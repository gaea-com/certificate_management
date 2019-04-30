# 域名ssl证书管理

用于给域名创建ssl证书，目前集成了cloudflare、阿里云、dnspod三家DNS厂商。

主要功能:
* 创建域名证书及通配符证书
* 每次创建的证书有效期为: 90天
* 证书在剩余7天过期时，自动更新证书
* 自动检查https的域名及子域名，并在证书有效期剩余5天时，发送提醒邮件
* 域名解析(添加、修改、暂停)

环境:

python3.7 + mysql5.7 + django2.1.7  + gunicorn

访问地址: http://127.0.0.1/index

后台地址: http://127.0.0.1/SSL-ADMIN

默认后台账号: admin

默认后台密码: admin


## docker-compose方式部署

-  数据库准备
    * mysql 5.7+ 版本

- 修改环境配置参数

在 docker/docker-compose 目录下编辑docker-compose.yaml文件，填写环境配置对应的值
    
```text
DB_NAME:   # 数据库名称
DB_USER:   # 数据库账号
DB_PASSWORD:   # 数据库密码
DB_HOST:   # 数据库地址
DB_PORT:  # 数据库端口
ADMINS_EMAIL:  # 管理员邮箱
EMAIL_PASSWORD:    # 管理员邮箱密码
EMAIL_HOST:    # 发送邮件服务器
EMAIL_PORT:    # 邮箱服务器端口号
EMAIL_SSL: # 邮箱是否开启加密, True|False (默认为True)
```

> Ps. 证书文件保存位置在容器中/root/.acme.sh/mycert目录下，如需持久化保存，

- 启动容器

```text
docker-compose pull
docker-compose up -d
```


## k8s方式部署

-  数据库准备
    * mysql 5.7+ 版本


- 修改环境配置参数

在 docker/open-k8s 目录下编辑cert-deploy.yaml文件，填写对应的环境配置的值

```text
DB_NAME:   # 数据库名称
DB_USER:   # 数据库账号
DB_PASSWORD:   # 数据库密码
DB_HOST:   # 数据库地址
DB_PORT:  # 数据库端口（默认为3306）
ADMINS_EMAIL:  # 管理员邮箱
EMAIL_PASSWORD:    # 管理员邮箱密码
EMAIL_HOST:    # 发送邮件服务器
EMAIL_PORT:    # 邮箱服务器端口号
EMAIL_SSL: # 邮箱是否开启加密, True|False (默认为True)
```

- 启动容器

```text
kubectl create -f cert-deploy.yaml
```

> Ps. 容器所在namespace: domain-cert

## 测试通过
* 浏览器: chrome 版本 73.0.3683.103

 
# License
License is GPLv3
