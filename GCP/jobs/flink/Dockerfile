FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY jobs/flink/pom.xml .
COPY jobs/flink/src src
RUN mvn -B verify \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.8.1:copy \
       -Dartifact=org.apache.flink:flink-gs-fs-hadoop:1.20.3 -DoutputDirectory=/plugins \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.8.1:copy \
       -Dartifact=org.apache.flink:flink-metrics-prometheus:1.20.3 -DoutputDirectory=/plugins
FROM flink:1.20.3-scala_2.12-java17
COPY --from=build /build/target/orders-payments.jar /opt/flink/usrlib/orders-payments.jar
COPY --from=build /plugins/flink-gs-fs-hadoop-1.20.3.jar /opt/flink/plugins/gs-fs-hadoop/
COPY --from=build /plugins/flink-metrics-prometheus-1.20.3.jar /opt/flink/lib/
COPY jobs/flink/log4j-console.properties /opt/flink/conf/log4j-console.properties
USER flink
