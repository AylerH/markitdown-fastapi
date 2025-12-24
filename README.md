# 文本文件转md后端

## 缺点
* 仅可转换文本内容内容；
* 格式可能丢失；

## 优点
* 可转换任意文件为md；
* 启动方便：docker compose一键启动（镜像1G左右）；

## 多分支说明
详：分支说明.md
```
backend:仅后端分支;
main:全栈分支
```

## 目录树结构
my_project/
├── app/
│   ├── app.py             <-- 后端逻辑
│   └── static/            <-- 新建文件夹
│       └── index.html     <-- 前端页面
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

# MarkItDown FastAPI

🚀 A simplified and containerized version of [MarkItDown](https://github.com/microsoft/markitdown) running as a FastAPI service, with a RESTful API for file-to-Markdown conversion.

## ✨ Features

- Convert files to Markdown via API
- Upload, list, download, and delete files
- Lightweight Dockerized setup using `docker-compose`
- Interactive API documentation via Swagger UI

## 📸 API Preview

Here’s a preview of the available endpoints exposed via Swagger UI:

![API Docs Screenshot](MarkItDown.png)

You can access the interactive docs at:
http://localhost:5000/docs
> Make sure the app is running using Docker or FastAPI directly.

## 📦 Getting Started
复制.env.example为.env
```bash
git clone https://github.com/Elkhn/markitdown-fastapi.git
cd markitdown-fastapi
docker compose up -d --build
```

## Credits & Inspiration

This project is heavily inspired by [MarkItDown](https://github.com/microsoft/markitdown) developed by Microsoft.
This is **not a fork** but a lightweight custom version built for my own needs, removing parts that were not essential for deployment or containerization.
Respect and thanks to the original developers for their excellent work!