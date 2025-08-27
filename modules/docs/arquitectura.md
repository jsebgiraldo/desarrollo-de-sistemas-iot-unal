# Arquitectura General


Este módulo implementa una arquitectura IoT educativa basada en ThingsBoard Community Edition, siguiendo buenas prácticas de escalabilidad, robustez y modularidad. La solución es completamente reproducible usando Docker Compose y componentes open source.


## Diagrama
![Diagrama de arquitectura](https://img.thingsboard.io/reference/thingsboard-architecture.svg)

## Descripción de capas

- **Servidor ThingsBoard**: Plataforma central para ingesta, visualización y gestión de datos IoT. Provee APIs MQTT, HTTP y WebSocket, motor de reglas y una interfaz web para administración y dashboards. En este módulo se utiliza en modo monolítico, con base de datos PostgreSQL.
- **Gateway oficial ThingsBoard**: Actúa como puente entre dispositivos/nodos y el servidor ThingsBoard. Recibe mensajes MQTT de múltiples dispositivos, los traduce y enruta hacia ThingsBoard usando la API de gateway. Permite la integración de dispositivos que no soportan directamente la API de ThingsBoard.
- **Broker Mosquitto**: Broker MQTT ligero y confiable, punto de entrada para los dispositivos simulados y reales. Gestiona la mensajería entre nodos y gateway, y permite la observación de los flujos de datos.
- **Simuladores/Nodos**: Contenedores que simulan dispositivos IoT, publicando telemetría y eventos de conexión a través de MQTT. Permiten pruebas y validación sin hardware físico.
- **Redes Docker**: Cada componente se despliega en una red Docker dedicada, asegurando segmentación, aislamiento y control del tráfico entre servicios.
- **Flujo de datos**: Los nodos publican datos a Mosquitto, el gateway los recoge y reenvía a ThingsBoard, donde se almacenan, visualizan y procesan mediante el motor de reglas.

## Características clave de la arquitectura

- **Escalabilidad**: ThingsBoard soporta despliegues monolíticos y en microservicios. En este módulo se utiliza el modo monolítico por simplicidad, pero la arquitectura es extensible.
- **Durabilidad y robustez**: El uso de colas de mensajes y bases de datos robustas (PostgreSQL) asegura la persistencia y confiabilidad de los datos.
- **Customización**: El gateway y los nodos simulados pueden adaptarse fácilmente para nuevos protocolos o escenarios de práctica.
- **Reproducibilidad**: Todo el entorno se despliega con Docker Compose, facilitando la instalación y pruebas en cualquier entorno educativo o de laboratorio.

## Referencias

- [Documentación oficial ThingsBoard](https://thingsboard.io/docs/reference/)
- [API MQTT ThingsBoard](https://thingsboard.io/docs/reference/mqtt-api/)
- [Gateway MQTT API](https://thingsboard.io/docs/reference/gateway-mqtt-api/)
- [Motor de reglas](https://thingsboard.io/docs/user-guide/rule-engine-2-0/overview/)
