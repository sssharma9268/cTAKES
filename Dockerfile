FROM maven:3.5-jdk-8-alpine as maven

WORKDIR /app
COPY . /app

RUN mvn dependency:go-offline -B

RUN mvn package

FROM openjdk:8u171-jre-alpine

WORKDIR /app

COPY --from=maven target/ctakes-misc-*.jar ./app/ctakes-misc.jar

EXPOSE 8080

CMD ["java","-jar","./app/ctakes-misc.jar"]


