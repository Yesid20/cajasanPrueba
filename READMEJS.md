# GESTIÓN DE PEDIDOS - PRUEBA TÉCNICA

Este repositorio contiene una solución Fullstack para la gestión de pedidos de clientes.

## TECNOLOGÍAS UTILIZADAS

**Backend:**
* Java 17+ / Spring Boot (API REST)
* Bean Validation / Almacenamiento en memoria

**Frontend:**
* Angular (Componentes Standalone)
* HttpClient + RxJS

---

## EJECUCIÓN DEL PROYECTO

### Backend (Spring Boot)
1. `cd backend/orders-api`
2. `./mvnw spring-boot:run` (o `mvn spring-boot:run`)
* Servidor en: http://localhost:8081

### Frontend (Angular)
1. `cd frontend/orders-ui`
2. `npm install`
3. `npm start`
* Cliente en: http://localhost:4200

---

## ENDPOINTS DEL BACKEND
* `GET /orders`: Listar todos los pedidos.
* `GET /orders/{id}`: Detalle de un pedido.
* `POST /orders`: Crear pedido.
* `PATCH /orders/{id}/status`: Actualizar estado (PENDING, CONFIRMED, SHIPPED, DELIVERED).