FROM openjdk:8u171-jre-alpine

WORKDIR /app
COPY . /app
COPY app/target/ctakes-misc-*.jar ./app/ctakes-misc.jar

EXPOSE 8080

CMD ["java","-jar","./app/ctakes-misc.jar"]

FROM python:3.6-slim

RUN pip install --trusted-host pypi.python.org flask
ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

EXPOSE 81

CMD ["python","/app/test.py"]
