### 1. Get Linux
FROM alpine:3.7 as build

RUN mkdir -p /usr/app

WORKDIR /usr/app
COPY . /usr/app

### Adding user
RUN apk add sudo
RUN addgroup -S ctakesgroup
RUN adduser -S -D -h /usr/app ctakesuser -G ctakesgroup
###RUN chown -R ctakesuser:ctakesgroup /usr/
#USER root

### 2. Get Java via the package manager
RUN apk update
RUN apk fetch openjdk8
RUN apk add openjdk8
RUN apk add curl

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk/"
ENV PATH="$JAVA_HOME/bin:${PATH}"

RUN java -version
RUN javac -version

### 3. Get Maven
ENV MAVEN_VERSION 3.8.1

RUN wget http://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz && \
  tar -zxvf apache-maven-$MAVEN_VERSION-bin.tar.gz && \
  rm apache-maven-$MAVEN_VERSION-bin.tar.gz && \
  mv apache-maven-$MAVEN_VERSION /usr/lib/mvn
  
ENV MAVEN_HOME="/usr/lib/mvn"
ENV PATH="$MAVEN_HOME/bin:${PATH}"

RUN mvn --version

WORKDIR /usr/app
##RUN ["mvn","package","-DskipTests"]
RUN mvn clean install
###COPY /root/.m2/repository/org/apache/ctakes/ctakes-misc/4.0.0/ctakes-misc-4.0.0-jar-*.jar /usr/app/
#EXPOSE 8080
#CMD ["java","-jar","/root/.m2/repository/org/apache/ctakes/ctakes-misc/4.0.0/ctakes-misc-4.0.0-jar-*.jar"]

### 4. Get Python, PIP

RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

### 5. Get Flask for the app
RUN pip install --trusted-host pypi.python.org flask
RUN pip install Crypto
RUN pip install pycrypto
RUN python --version

EXPOSE 5000    
ADD test.py /
ENV FLASK_APP=test.py
CMD ["flask", "run", "--host", "0.0.0.0"]

#USER ctakesuser


