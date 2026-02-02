# Sistema de Inventario para Taller Automotriz

Sistema web completo para la gestión de inventario de repuestos en talleres de mantenimiento automotriz, con control de roles, alertas automáticas de stock y módulo de facturación.

## 🚀 Características

### Gestión de Usuarios y Roles
- **Administrador**: Control total del sistema
- **Almacenista**: Gestión de inventario, entradas y salidas
- **Vendedor**: Confirmación de ventas y facturación
- **Técnico**: Consulta de información (solo lectura)

### Funcionalidades Principales
- ✅ Gestión completa de repuestos (CRUD)
- ✅ Control de entradas y salidas de inventario
- ✅ Sistema de alertas automáticas de stock bajo/agotado
- ✅ Notificaciones en tiempo real para administradores y almacenistas
- ✅ Gestión de clientes y vehículos
- ✅ Compatibilidad de repuestos con múltiples marcas/modelos
- ✅ Módulo de facturación
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Búsqueda y filtrado avanzado
- ✅ Interfaz completamente en español (latinoamericano)
- ✅ Responsive design (adaptable a móviles)

## 📋 Requisitos Previos

- Python 3.8 o superior
- MySQL 5.7 o superior (o MariaDB)
- phpMyAdmin (opcional, para administración de base de datos)

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd taller_inventario
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

#### Opción A: Usando MySQL desde línea de comandos

```bash
mysql -u root -p < database/schema.sql
```

#### Opción B: Usando phpMyAdmin

1. Abrir phpMyAdmin en el navegador (generalmente http://localhost/phpmyadmin)
2. Crear una nueva base de datos llamada `taller_inventario`
3. Importar el archivo `database/schema.sql`

### 5. Configurar Variables de Entorno (Opcional)

Crear un archivo `.env` en la raíz del proyecto:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña
MYSQL_DB=taller_inventario
MYSQL_PORT=3306
SECRET_KEY=tu-clave-secreta-muy-segura
FLASK_DEBUG=0
```

**Nota**: Si no se configuran las variables de entorno, la aplicación usará los valores por defecto en `config.py`

### 6. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 👤 Credenciales por Defecto

**Usuario**: `admin`  
**Contraseña**: `admin123`

⚠️ **IMPORTANTE**: Cambiar estas credenciales inmediatamente en producción.

## 📱 Uso del Sistema

### Dashboard
- Vista general con estadísticas del inventario
- Repuestos con stock bajo
- Últimos movimientos
- Alertas activas

### Gestión de Repuestos
1. Ir a **Repuestos** en el menú
2. Hacer clic en **Nuevo Repuesto**
3. Llenar el formulario con:
   - Código único
   - Nombre del repuesto
   - Categoría
   - Precio de venta
   - Cantidad mínima (para alertas)
   - Ubicación física
   - Observaciones

### Entradas de Inventario
1. Ir a **Movimientos** → **Entrada de Inventario**
2. Seleccionar el repuesto
3. Ingresar cantidad y precio unitario
4. Seleccionar tipo de movimiento (Compra, Ajuste, etc.)
5. Guardar

### Salidas de Inventario (Almacenista)
1. Ir a **Movimientos** → **Salida de Inventario**
2. Seleccionar repuesto
3. Ingresar cantidad
4. **Asociar técnico solicitante** (obligatorio)
5. **Asociar cliente y vehículo** (obligatorio)
6. El sistema verifica stock disponible automáticamente
7. Guardar (queda pendiente para confirmación en caja)

### Confirmación de Ventas (Vendedor)
1. Las salidas pendientes aparecen en el módulo de facturación
2. El vendedor confirma la venta al recibir el pago
3. El sistema genera la factura y actualiza el estado

### Alertas Automáticas
El sistema genera alertas automáticamente cuando:
- **Stock Bajo**: Cantidad actual ≤ cantidad mínima
- **Agotado**: Cantidad actual = 0

Las alertas se notifican a:
- Administradores
- Almacenistas

## 🏗️ Estructura del Proyecto

```
taller_inventario/
│
├── app.py                  # Aplicación principal Flask
├── config.py              # Configuración
├── database.py            # Conexión y operaciones BD
├── auth.py                # Autenticación y permisos
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
│
├── database/
│   └── schema.sql        # Esquema de base de datos
│
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   ├── js/
│   │   └── main.js       # JavaScript principal
│   └── img/              # Imágenes
│
└── templates/
    ├── base.html          # Template base
    ├── login.html         # Página de login
    ├── dashboard.html     # Dashboard principal
    ├── repuestos/         # Templates de repuestos
    ├── movimientos/       # Templates de movimientos
    ├── alertas/           # Templates de alertas
    └── usuarios/          # Templates de usuarios
```

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Sesiones seguras con Flask
- ✅ Control de acceso basado en roles
- ✅ Validación de datos en servidor
- ✅ Protección contra SQL injection (queries parametrizadas)

## 📊 Base de Datos

### Tablas Principales:
- `usuarios` - Usuarios del sistema
- `roles` - Roles y permisos
- `repuestos` - Catálogo de repuestos
- `categorias_repuestos` - Categorías de repuestos
- `marcas_vehiculos` - Marcas de vehículos
- `modelos_vehiculos` - Modelos de vehículos
- `repuestos_compatibilidad` - Compatibilidad con vehículos
- `repuestos_equivalentes` - Marcas equivalentes
- `clientes` - Clientes del taller
- `vehiculos_clientes` - Vehículos de clientes
- `movimientos_inventario` - Entradas y salidas
- `tipos_movimiento` - Tipos de movimiento
- `facturas` - Facturas de venta
- `detalles_factura` - Detalles de facturas
- `alertas_inventario` - Alertas del sistema
- `notificaciones_usuarios` - Notificaciones por usuario

## 🛠️ Tecnologías Utilizadas

### Backend:
- **Python 3.8+**
- **Flask 3.0** - Framework web
- **PyMySQL** - Conector MySQL
- **bcrypt** - Hashing de contraseñas

### Frontend:
- **HTML5**
- **CSS3**
- **Bootstrap 5** - Framework CSS
- **JavaScript (ES6+)**
- **jQuery 3.6** - Manipulación DOM
- **Bootstrap Icons** - Iconos

### Base de Datos:
- **MySQL 5.7+** o **MariaDB**

## 📝 Crear Nuevos Usuarios

Como administrador:
1. Ir a **Usuarios** en el menú
2. Clic en **Nuevo Usuario**
3. Llenar formulario:
   - Nombre de usuario
   - Contraseña
   - Nombre completo
   - Email
   - **Seleccionar rol**
4. Guardar

## 🔄 Flujo de Trabajo Recomendado

### Para Almacenista:
1. Registrar entradas de inventario cuando llegan repuestos
2. Revisar alertas de stock bajo diariamente
3. Procesar solicitudes de salida de técnicos
4. Verificar stock antes de autorizar salidas

### Para Vendedor:
1. Confirmar ventas pendientes en caja
2. Generar facturas
3. Registrar método de pago
4. Entregar factura al cliente

### Para Técnico:
1. Consultar disponibilidad de repuestos
2. Solicitar salidas a almacenista
3. Verificar compatibilidad con vehículos

### Para Administrador:
1. Monitorear dashboard general
2. Gestionar usuarios y permisos
3. Revisar alertas críticas
4. Supervisar movimientos de inventario

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
- Verificar que MySQL esté ejecutándose
- Revisar credenciales en `config.py` o `.env`
- Verificar que la base de datos `taller_inventario` exista

### Error 500 en la Aplicación
- Revisar los logs en consola
- Verificar que todas las dependencias estén instaladas
- Asegurarse de que el entorno virtual esté activado

### No se pueden crear usuarios
- Verificar permisos de rol de administrador
- Revisar que las contraseñas cumplan requisitos mínimos

## 📈 Próximas Mejoras (Roadmap)

- [ ] Reportes en PDF
- [ ] Exportación a Excel
- [ ] Gráficos de estadísticas
- [ ] Historial de precios
- [ ] Proveedores y órdenes de compra
- [ ] Integración con sistemas de pago
- [ ] App móvil
- [ ] Escáner de códigos de barras
- [ ] Notificaciones por email/SMS

## 📄 Licencia

Este proyecto es software propietario para uso interno del taller.

## 👨‍💻 Soporte

Para soporte técnico o consultas, contactar al administrador del sistema.

---

**Sistema desarrollado para la gestión eficiente de inventarios en talleres automotrices** 🔧🚗
