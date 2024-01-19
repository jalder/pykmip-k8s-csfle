# ARM64 base
FROM --platform=linux/arm64 node:18.19.0-bullseye

# AMD64 base
#FROM --platform=linux/amd64 node:18.19.0-bullseye

RUN mkdir /app && cd /app && mkdir /app/crypt && cd /app/crypt

WORKDIR /app/crypt

# Download crypt shared x86_64, we do not have an ARM64 build of crypt shared for Debian 11
#RUN curl -OL https://downloads.mongodb.com/linux/mongo_crypt_shared_v1-linux-x86_64-enterprise-debian11-6.0.12.tgz
#RUN tar zxvf mongo_crypt_shared_v1-linux-x86_64-enterprise-debian11-6.0.12.tgz

# Build from source tests
#RUN git clone https://github.com/mongodb/libmongocrypt --branch=1.8.4
#RUN cd /app/crypt/libmongocrypt
#RUN mkdir /app/crypt/libmongocrypt/cmake-build && cd /app/crypt/libmongocrypt/cmake-build
#RUN apt update -y
#RUN apt install cmake -y
#WORKDIR /app/crypt/libmongocrypt/cmake-build
#RUN cmake /app/crypt/libmongocrypt
#RUN make

#RUN sh -c 'curl -s --location https://www.mongodb.org/static/pgp/libmongocrypt.asc | gpg --dearmor >/etc/apt/trusted.gpg.d/libmongocrypt.gpg'
#RUN echo "deb https://libmongocrypt.s3.amazonaws.com/apt/debian bullseye/libmongocrypt/1.8 main" | tee /etc/apt/sources.list.d/libmongocrypt.list
#RUN apt update -y
#RUN apt install -y libmongocrypt-dev

#Alternatively, we do have ARM64 build of Ubuntu, the 20.04 release works with Debian 11
RUN curl -OL https://downloads.mongodb.com/linux/mongo_crypt_shared_v1-linux-aarch64-enterprise-ubuntu2004-6.0.12.tgz
RUN tar zxvf mongo_crypt_shared_v1-linux-aarch64-enterprise-ubuntu2004-6.0.12.tgz

WORKDIR /app
#Deps
RUN npm install mongodb@6.3.0 mongodb-client-encryption@6.0.0 --save

#Test App
COPY package.json /app
COPY app.js /app

CMD [ "/bin/bash" ]