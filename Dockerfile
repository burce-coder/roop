FROM nvidia/cuda:11.8.0-devel-ubuntu22.04 as builder

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends \
        build-essential libcurl4-openssl-dev libssl-dev \
        python3.10 python3.10-dev python3.10-venv \
        wget git git-lfs ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv
# FORCE_CUDA 是编译安装 pytorch3d 所需要的环境变量
ENV VIRTUAL_ENV=/app/venv \
    PATH="/app/venv/bin:/usr/local/cuda/bin:$PATH" \
    CUDA_HOME="/usr/local/cuda" \
    CUDA_TOOLKIT_ROOT_DIR="/usr/local/cuda" \
    LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}" \
    FORCE_CUDA=1

# ADD . /app
WORKDIR /app

RUN pip install torch==2.0.1+cu118 --find-links https://download.pytorch.org/whl/torch_stable.html
RUN pip install fvcore iopath
RUN pip install --no-index --no-cache-dir pytorch3d --find-links https://dl.fbaipublicfiles.com/pytorch3d/packaging/wheels/py310_cu118_pyt201/download.html
COPY requirements-roop.txt requirements-roop.txt
RUN pip install --upgrade -r requirements-roop.txt --find-links https://dl.fbaipublicfiles.com/pytorch3d/packaging/wheels/py310_cu118_pyt201/download.html
COPY . /app/

# FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND noninteractive

# os packages and timezone
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libssl-dev libcurl4-openssl-dev \
        software-properties-common \
        python3.10 python3.10-dev python3.10-venv  \
        ffmpeg \
        git git-lfs wget curl zip unzip bzip2 vim inetutils-ping sudo net-tools iproute2 \
        ca-certificates tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean &&  \
    apt install -y libosmesa6 && \
    add-apt-repository ppa:oibaf/graphics-drivers -r && \
    rm -rf /var/lib/apt/lists/*

# 安装 TensorRT
RUN wget "https://drive.usercontent.google.com/download?id=1xB6zEO_rzqCXuiR2QCaUTexzBQY6yFUk&export=download&authuser=0&confirm=t&uuid=f24eb993-6822-4d0d-9c21-3bd6fe32ac3a&at=APZUnTWEQkLYuvBTNGBTE2v6PjTW%3A1713520294452" -O nv-tensorrt-local-repo-ubuntu2204-8.5.3-cuda-11.8_1.0-1_amd64.deb && \
    dpkg -i nv-tensorrt-local-repo-ubuntu2204-8.5.3-cuda-11.8_1.0-1_amd64.deb && rm -rf nv-tensorrt-local-repo-ubuntu2204-8.5.3-cuda-11.8_1.0-1_amd64.deb && \
    cp /var/nv-tensorrt-local-repo-ubuntu2204-8.5.3-cuda-11.8/*-keyring.gpg /usr/share/keyrings/ && \
    cd /var/nv-tensorrt-local-repo-ubuntu2204-8.5.3-cuda-11.8 && \
    dpkg -i libnvinfer8_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvonnxparsers8_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvparsers8_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvinfer-plugin8_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvinfer-dev_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvinfer-plugin-dev_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvparsers-dev_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvonnxparsers8_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvonnxparsers-dev_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i libnvinfer-samples_8.5.3-1+cuda11.8_all.deb && \
    dpkg -i python3-libnvinfer_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i onnx-graphsurgeon_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i graphsurgeon-tf_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i uff-converter-tf_8.5.3-1+cuda11.8_amd64.deb && \
    dpkg -i tensorrt-libs_8.5.3.1-1+cuda11.8_amd64.deb && rm -rf /var/nv-tensorrt-local-repo-ubuntu2204-8.5.3-cuda-11.8/*


ENV TIME_ZONE="Asia/Shanghai" \
    TZ="Asia/Shanghai" \
    VIRTUAL_ENV=/app/venv \
    PATH="/app:/app/venv/bin:${PATH}" \
    CUDA_TOOLKIT_ROOT_DIR="/usr/local/cuda" \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/lib/x86_64-linux-gnu/ \
    CODE_BRANCH=${CODE_BRANCH:-main} \
    AWS_ACCESS_KEY_ID="XXX" \
    AWS_SECRET_ACCESS_KEY="XXX" \
    AWS_DEFAULT_REGION="us-east-1" \
    AWS_S3_ACCELERATE="false" \
    LOCAL_CACHE_PATH="/var/s3_cache" \
    PYOPENGL_PLATFORM="osmesa" \
    PYTHONPATH="/app:/app/guruai_image" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    

WORKDIR /app
COPY --from=builder /app /app
