# Nginx 配置文件修改说明

## 📝 需要修改的位置

在您的配置文件中，找到 `location ~ .*\\.(js|css)?$` 这一行，**在这之前**添加以下配置：

---

## ✅ 完整的修改后配置

```nginx
server
{
    listen 80;
    server_name kpl.17kx.net;
    index index.html index.htm default.htm default.html;
    root /www/wwwroot/gendan/frontend/dist;
    include /www/server/panel/vhost/nginx/extension/kpl.17kx.net/*.conf;

    #CERT-APPLY-CHECK--START
    # 用于SSL证书申请时的文件验证相关配置 -- 请勿删除并保持这段设置在优先级高的位置
    include /www/server/panel/vhost/nginx/well-known/kpl.17kx.net.conf;
    #CERT-APPLY-CHECK--END

    #SSL-START SSL相关配置，请勿删除或修改下一行带注释的404规则
    #error_page 404/404.html;
    #SSL-END

    #ERROR-PAGE-START  错误页配置，可以注释、删除或修改
    #error_page 404 /404.html;
    #error_page 502 /502.html;
    #ERROR-PAGE-END

    #REWRITE-START URL重写规则引用,修改后将导致面板设置的伪静态规则失效
    include /www/server/panel/vhost/rewrite/html_kpl.17kx.net.conf;
    #REWRITE-END

    #禁止访问的文件或目录
    location ~ ^/(\.user.ini|\.htaccess|\.git|\.env|\.svn|\.project|LICENSE|README.md)
    {
        return 404;
    }

    #一键申请SSL证书验证目录相关设置
    location ~ \.well-known{
        allow all;
    }

    #禁止在证书验证目录放入敏感文件
    if ( $uri ~ "^/\.well-known/.*\.(php|jsp|py|js|css|lua|ts|go|zip|tar\.gz|rar|7z|sql|bak)$" ) {
        return 403;
    }

    # ========== 新增配置开始 ==========
    
    # 前端路由（支持 Vue Router）- 必须放在静态资源之前
    location / {
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # ========== 新增配置结束 ==========

    location ~ .*\\.(gif|jpg|jpeg|png|bmp|swf)$
    {
        expires      30d;
        error_log /dev/null;
        access_log /dev/null;
    }

    location ~ .*\\.(js|css)?$
    {
        expires      12h;
        error_log /dev/null;
        access_log /dev/null;
    }
    
    access_log  /www/wwwlogs/kpl.17kx.net.log;
    error_log  /www/wwwlogs/kpl.17kx.net.error.log;
}
```

---

## 📍 关键修改点

### 1. 添加的位置

在 `location ~ .*\\.(gif|jpg|jpeg|png|bmp|swf)$` **之前**添加以下两段配置：

```nginx
# 前端路由（支持 Vue Router）
location / {
    try_files $uri $uri/ /index.html;
    index index.html;
}

# API 反向代理
location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # 缓冲设置
    proxy_buffering off;
    proxy_request_buffering off;
}
```

### 2. 为什么放在这里？

- `location /` 必须放在静态资源匹配规则之前，否则静态资源会被优先匹配
- `location /api` 放在 `location /` 之后，确保 API 请求优先匹配

---

## 🔧 操作步骤

1. **打开配置文件**
   - 在宝塔面板中，点击网站右侧「**设置**」
   - 点击「**配置文件**」

2. **找到位置**
   - 找到 `location ~ .*\\.(gif|jpg|jpeg|png|bmp|swf)$` 这一行
   - 在这**之前**添加新配置

3. **添加配置**
   - 复制上面的两段 `location` 配置
   - 粘贴到指定位置

4. **保存并重载**
   - 点击「**保存**」
   - 点击「**重载配置**」或「**重启**」

---

## ✅ 验证配置

### 1. 测试前端

访问：`http://kpl.17kx.net/`

应该能看到前端界面。

### 2. 测试 API

访问：`http://kpl.17kx.net/api/health`

应该返回：
```json
{"status": "ok"}
```

### 3. 测试 API 文档

访问：`http://kpl.17kx.net/api/docs`

应该能看到 FastAPI 的 API 文档页面。

---

## ⚠️ 注意事项

1. **不要删除**宝塔面板自动生成的配置（如 `include` 语句）
2. **保持顺序**：`location /` 和 `location /api` 必须在静态资源匹配之前
3. **保存后重载**：修改后必须重载 Nginx 配置才能生效

---

## 🐛 如果遇到问题

1. **检查后端是否运行**：访问 `http://127.0.0.1:8000/docs`（在服务器上）
2. **查看错误日志**：网站设置 → 「日志」→ 「错误日志」
3. **检查配置语法**：保存时宝塔面板会检查语法错误

---

**按照以上步骤修改即可！** 🚀


