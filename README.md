# 📊 Sistema de Conversión SIRE SUNAT a CONCAR

Sistema integral web para la conversión de registros electrónicos SIRE (SUNAT) a macros Excel (.xlsx) compatibles con CONCAR, incluyendo el cálculo automatizado de la Liquidación de Impuestos mensual.

## ✨ Características Principales

* **Procesamiento de Archivos SIRE:** Lectura y normalización automática de archivos CSV de compras y ventas exportados desde SUNAT.
* **Exportación a CONCAR:** Generación de archivos .xlsx formateados con las columnas exactas requeridas para la importación directa en el sistema contable CONCAR.
* **Calculadora de Liquidación de Impuestos:** Cálculo interno y en tiempo real del IGV (Ventas, Compras, Crédito Fiscal) y Renta mensual basándose en la data procesada.
* **Roles y Permisos:** Sistema multi-usuario con roles de Administrador (gestión global) y Contador (acceso restringido a sus propias empresas).
* **Dashboard Dinámico:** Panel de control con estadísticas de los procesos, ranking de empresas y estados de carga conectados a la base de datos en vivo.
* **Validación de RUCs:** Integración con APIs externas (apiperu.dev / api.json.pe) para consultar deudas coactivas y validar razones sociales.
* **Gestión Inteligente de Cuentas Contables:** Auto-asignación de cuentas basada en la frecuencia e historial de uso por proveedor.

## 🛠️ Tecnologías Utilizadas

* **Frontend:** React.js, Vite, Tailwind CSS, Framer Motion.
* **Backend:** Python, Django REST Framework, Pandas (procesamiento masivo de datos), OpenPyXL.
* **Base de Datos:** PostgreSQL.
* **Infraestructura:** Docker & Docker Compose, Nginx.

## 🚀 Guía de Instalación para Colaboradores

Este proyecto está 100% contenerizado con **Docker** para garantizar que funcione idénticamente en cualquier computadora sin necesidad de instalar Python o Node.js de forma local. Las dependencias locales (como 
ode_modules o entornos virtuales) no se suben al repositorio por buenas prácticas, ya que Docker se encarga de instalarlas internamente.

### Requisitos Previos
* Tener instalado [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/).
* Tener instalado [Git](https://git-scm.com/downloads).

### Pasos para Desplegar el Proyecto Localmente

1. **Clonar el repositorio**
   `ash
   git clone https://github.com/JhonorB/PROYECTODECONVERSIONSUNAT.git
   cd PROYECTODECONVERSIONSUNAT
   `

2. **Configurar las Variables de Entorno**
   Renombrar el archivo de ejemplo para crear tu propio entorno local:
   `ash
   cp .env.example .env
   `
   *(Asegúrate de llenar las credenciales necesarias dentro del archivo .env como los tokens de la API de SUNAT).*

3. **Construir y Levantar los Contenedores**
   Ejecuta el siguiente comando en la raíz del proyecto. Esto descargará las dependencias de Python y Node, y construirá la base de datos dentro de Docker:
   `ash
   docker-compose up -d --build
   `

4. **Acceder a la Aplicación**
   Una vez que los contenedores estén corriendo, abre tu navegador en:
   * **Frontend (Interfaz Gráfica):** [http://localhost:5173](http://localhost:5173)
   * **Backend (API de Datos):** [http://localhost:8000/api](http://localhost:8000/api)

### 🛑 Detener el servidor
Para apagar los contenedores de forma segura y liberar los puertos, ejecuta:
`ash
docker-compose down
`
