ARG BUILD_FROM
FROM $BUILD_FROM

# Install python 3
RUN apk add --no-cache python3 && \
	python3 -m ensurepip && \
	pip3 install --no-cache --upgrade pip setuptools wheel && \
	pip3 install flask requests

# Copy data for add-on
COPY server.py /
COPY run.sh /
RUN chmod a+x /run.sh

# Install nginx
RUN apk --no-cache add nginx \
	&& mkdir -p /run/nginx

#Copy our conf into the nginx http.d folder.
COPY ingress.conf /etc/nginx/http.d/

RUN mkdir /hikaccess

WORKDIR /hikaccess

COPY . /hikaccess

CMD [ "/run.sh" ]
