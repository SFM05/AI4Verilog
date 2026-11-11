FROM mcr.azure.cn/devcontainers/base:ubuntu-24.04

# 安装系统级依赖
RUN apt-get update
RUN apt-get upgrade -y

# 下载OSS-CAD-Suite
WORKDIR /tmp
RUN wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-11-02/oss-cad-suite-linux-x64-20261102.tgz
RUN tar -zxvf oss-cad-suite-linux-x64-20261102.tgz -C /opt

# 下载工艺库
WORKDIR /edatools
RUN wget https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/raw/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib

# 安装 Python 依赖
RUN apt-get install -y python3 python3-pip
# COPY requirements.txt /tmp/
# RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 安装Opencode
USER vscode
RUN curl -fsSL https://opencode.ai/v2/install | bash
USER root

# 清理
WORKDIR /
RUN rm -f /tmp/oss-cad-suite-linux-x64-20261011.tgz

WORKDIR /workspace

# 如果希望使用完整的OSS-CAD-Suite环境，可以执行source /opt/oss-cad-suite/environment
ENTRYPOINT ["bash", "-c", "export PATH=/opt/oss-cad-suite/bin:$PATH && exec /bin/bash"]