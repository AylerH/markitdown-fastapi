FROM python:3.13-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg exiftool git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 拷贝整个项目（包含 app 文件夹）
COPY . .

# 提前创建好需要的目录
RUN mkdir -p /app/uploads /app/converted

EXPOSE 5000

# 注意这里启动 app/app.py 的语法
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000"]