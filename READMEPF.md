# Prueba Técnica: API de Productos con Autenticación JWT

Este proyecto consiste en un sistema de gestión de productos con un backend construido en **FastAPI (Python 3.12)** y un frontend desarrollado en **React (TypeScript)** utilizando **Vite**. La aplicación implementa un flujo completo de autenticación mediante JSON Web Tokens (JWT), incluyendo tokens de acceso, tokens de refresco y revocación de sesión.

## Requisitos Previos

* **Python 3.12** o superior.
* **Node.js** (versión LTS recomendada).
* **npm** (incluido con Node.js).

---

## Configuración del Backend

El servidor se encuentra en la carpeta `backend-python`. Utiliza una base de datos en memoria para usuarios y productos.

1.  Acceda al directorio del backend:
    cd backend-python
2.  Cree un entorno virtual:
    python -m venv venv
3.  Active el entorno virtual:
    * Dependiendo su sistema operativo (Windows, Linux)
4.  Instale las dependencias:
    pip install -r requirements.txt
5.  Inicie el servidor:
    python main.py
---

## Configuración del Frontend

El cliente se encuentra en la carpeta `frontend-react` y está configurado para comunicarse con el puerto 8000 del backend.

1.  Acceda al directorio del frontend:
    cd frontend-react
2.  Instale las dependencias:
    npm install
3.  Inicie el entorno de desarrollo:
    npm run dev
---

## Detalles de Autenticación y Endpoints

### Credenciales de Prueba
El sistema cuenta con dos usuarios predefinidos en `main.py`:
* **Administrador:** `username: alice` / `password: alicepass` (Permisos de lectura y creación).
* **Usuario:** `username: bob` / `password: bobpass` (Permisos de lectura).

### Flujo JWT
* **Access Token:** Expira en 3 minutos.
* **Refresh Token:** Expira en 1 día.
* **Interceptores:** El frontend utiliza interceptores de Axios para renovar automáticamente el Access Token mediante el Refresh Token cuando este expira.

### Endpoints Principales
* `POST /auth/login`: Autenticación de usuario.
* `POST /auth/refresh`: Renovación de tokens.
* `POST /auth/logout`: Revocación de tokens.
* `GET /products`: Listado de productos (Protegido).
* `POST /products`: Creación de productos (Solo Administradores).