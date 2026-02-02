from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from config import config
from database import init_db, execute_query
from auth import (
    login_user, logout_user, get_current_user, is_authenticated,
    login_required, role_required, get_permissions, hash_password
)
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar base de datos
    init_db(app)
    
    # Context processor para variables globales en templates
    @app.context_processor
    def inject_globals():
        return {
            'current_user': get_current_user(),
            'permissions': get_permissions() if is_authenticated() else {},
            'now': datetime.now()
        }
    
    # ==================== RUTAS DE AUTENTICACIÓN ====================
    
    @app.route('/')
    def index():
        """Página de inicio - redirige según autenticación"""
        if is_authenticated():
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Página de inicio de sesión"""
        if is_authenticated():
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = login_user(username, password)
            if user:
                flash(f'¡Bienvenido {user["nombre_completo"]}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Cerrar sesión"""
        logout_user()
        flash('Sesión cerrada exitosamente', 'success')
        return redirect(url_for('login'))
    
    # ==================== DASHBOARD ====================
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard principal"""
        user = get_current_user()
        
        # Estadísticas generales
        stats = {}
        
        # Total de repuestos
        stats['total_repuestos'] = execute_query(
            "SELECT COUNT(*) as count FROM repuestos WHERE activo = TRUE",
            fetch_one=True
        )['count']
        
        # Valor total del inventario
        stats['valor_inventario'] = execute_query(
            "SELECT SUM(cantidad_actual * precio_venta) as total FROM repuestos WHERE activo = TRUE",
            fetch_one=True
        )['total'] or 0
        
        # Alertas activas
        stats['alertas_activas'] = execute_query(
            "SELECT COUNT(*) as count FROM alertas_inventario WHERE estado = 'ACTIVA'",
            fetch_one=True
        )['count']
        
        # Movimientos del día
        stats['movimientos_hoy'] = execute_query(
            "SELECT COUNT(*) as count FROM movimientos_inventario WHERE DATE(created_at) = CURDATE()",
            fetch_one=True
        )['count']
        
        # Repuestos con stock bajo
        repuestos_bajo_stock = execute_query("""
            SELECT r.codigo, r.nombre, r.cantidad_actual, r.cantidad_minima,
                   c.nombre as categoria
            FROM repuestos r
            LEFT JOIN categorias_repuestos c ON r.categoria_id = c.id
            WHERE r.activo = TRUE 
            AND r.cantidad_actual <= r.cantidad_minima
            ORDER BY r.cantidad_actual ASC
            LIMIT 10
        """, fetch_all=True)
        
        # Últimos movimientos
        ultimos_movimientos = execute_query("""
            SELECT mi.id, mi.cantidad, mi.created_at,
                   r.codigo as repuesto_codigo, r.nombre as repuesto_nombre,
                   tm.nombre as tipo_movimiento, tm.tipo,
                   u.nombre_completo as usuario
            FROM movimientos_inventario mi
            JOIN repuestos r ON mi.repuesto_id = r.id
            JOIN tipos_movimiento tm ON mi.tipo_movimiento_id = tm.id
            JOIN usuarios u ON mi.usuario_id = u.id
            ORDER BY mi.created_at DESC
            LIMIT 10
        """, fetch_all=True)
        
        return render_template('dashboard.html',
                             stats=stats,
                             repuestos_bajo_stock=repuestos_bajo_stock,
                             ultimos_movimientos=ultimos_movimientos)
    
    # ==================== GESTIÓN DE REPUESTOS ====================
    
    @app.route('/repuestos')
    @login_required
    def lista_repuestos():
        """Lista de repuestos"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        categoria_id = request.args.get('categoria', type=int)
        
        per_page = app.config['ITEMS_PER_PAGE']
        offset = (page - 1) * per_page
        
        # Construir query
        where_clauses = ["r.activo = TRUE"]
        params = []
        
        if search:
            where_clauses.append("(r.codigo LIKE %s OR r.nombre LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if categoria_id:
            where_clauses.append("r.categoria_id = %s")
            params.append(categoria_id)
        
        where_sql = " AND ".join(where_clauses)
        
        # Total de registros
        total = execute_query(
            f"SELECT COUNT(*) as count FROM repuestos r WHERE {where_sql}",
            tuple(params),
            fetch_one=True
        )['count']
        
        # Obtener repuestos
        params.extend([per_page, offset])
        repuestos = execute_query(f"""
            SELECT r.*, c.nombre as categoria_nombre
            FROM repuestos r
            LEFT JOIN categorias_repuestos c ON r.categoria_id = c.id
            WHERE {where_sql}
            ORDER BY r.nombre
            LIMIT %s OFFSET %s
        """, tuple(params), fetch_all=True)
        
        # Obtener categorías para filtro
        categorias = execute_query(
            "SELECT * FROM categorias_repuestos ORDER BY nombre",
            fetch_all=True
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('repuestos/lista.html',
                             repuestos=repuestos,
                             categorias=categorias,
                             page=page,
                             total_pages=total_pages,
                             search=search,
                             categoria_id=categoria_id)
    
    @app.route('/repuestos/nuevo', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA')
    def nuevo_repuesto():
        """Crear nuevo repuesto"""
        if request.method == 'POST':
            try:
                # Insertar repuesto
                repuesto_id = execute_query("""
                    INSERT INTO repuestos 
                    (codigo, nombre, descripcion, categoria_id, precio_venta, 
                     cantidad_actual, cantidad_minima, ubicacion_fisica, marca_fabricante, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    request.form['codigo'],
                    request.form['nombre'],
                    request.form.get('descripcion', ''),
                    request.form.get('categoria_id') or None,
                    request.form['precio_venta'],
                    request.form.get('cantidad_actual', 0),
                    request.form.get('cantidad_minima', 5),
                    request.form.get('ubicacion_fisica', ''),
                    request.form.get('marca_fabricante', ''),
                    request.form.get('observaciones', '')
                ), commit=True)
                
                flash('Repuesto creado exitosamente', 'success')
                return redirect(url_for('lista_repuestos'))
            
            except Exception as e:
                logger.error(f"Error creando repuesto: {e}")
                flash('Error al crear el repuesto', 'danger')
        
        # Obtener categorías
        categorias = execute_query(
            "SELECT * FROM categorias_repuestos ORDER BY nombre",
            fetch_all=True
        )
        
        return render_template('repuestos/form.html', categorias=categorias, repuesto=None)
    
    @app.route('/repuestos/<int:id>/editar', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA')
    def editar_repuesto(id):
        """Editar repuesto"""
        repuesto = execute_query(
            "SELECT * FROM repuestos WHERE id = %s",
            (id,),
            fetch_one=True
        )
        
        if not repuesto:
            flash('Repuesto no encontrado', 'danger')
            return redirect(url_for('lista_repuestos'))
        
        if request.method == 'POST':
            try:
                execute_query("""
                    UPDATE repuestos 
                    SET codigo = %s, nombre = %s, descripcion = %s, categoria_id = %s,
                        precio_venta = %s, cantidad_minima = %s, ubicacion_fisica = %s,
                        marca_fabricante = %s, observaciones = %s
                    WHERE id = %s
                """, (
                    request.form['codigo'],
                    request.form['nombre'],
                    request.form.get('descripcion', ''),
                    request.form.get('categoria_id') or None,
                    request.form['precio_venta'],
                    request.form.get('cantidad_minima', 5),
                    request.form.get('ubicacion_fisica', ''),
                    request.form.get('marca_fabricante', ''),
                    request.form.get('observaciones', ''),
                    id
                ), commit=True)
                
                flash('Repuesto actualizado exitosamente', 'success')
                return redirect(url_for('lista_repuestos'))
            
            except Exception as e:
                logger.error(f"Error actualizando repuesto: {e}")
                flash('Error al actualizar el repuesto', 'danger')
        
        categorias = execute_query(
            "SELECT * FROM categorias_repuestos ORDER BY nombre",
            fetch_all=True
        )
        
        return render_template('repuestos/form.html', categorias=categorias, repuesto=repuesto)
    
    @app.route('/repuestos/<int:id>/eliminar', methods=['POST'])
    @role_required('ADMINISTRADOR')
    def eliminar_repuesto(id):
        """Eliminar (desactivar) repuesto"""
        try:
            execute_query(
                "UPDATE repuestos SET activo = FALSE WHERE id = %s",
                (id,),
                commit=True
            )
            flash('Repuesto eliminado exitosamente', 'success')
        except Exception as e:
            logger.error(f"Error eliminando repuesto: {e}")
            flash('Error al eliminar el repuesto', 'danger')
        
        return redirect(url_for('lista_repuestos'))
    
    @app.route('/repuestos/<int:id>/ajustar-cantidad', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA')
    def ajustar_cantidad_repuesto(id):
        """Ajustar cantidad actual de repuesto"""
        repuesto = execute_query(
            "SELECT * FROM repuestos WHERE id = %s",
            (id,),
            fetch_one=True
        )
        
        if not repuesto:
            flash('Repuesto no encontrado', 'danger')
            return redirect(url_for('lista_repuestos'))
        
        if request.method == 'POST':
            try:
                nueva_cantidad = int(request.form['nueva_cantidad'])
                motivo = request.form.get('motivo', '')
                user = get_current_user()
                
                cantidad_anterior = repuesto['cantidad_actual']
                diferencia = nueva_cantidad - cantidad_anterior
                
                # Registrar en historial de ajustes
                execute_query("""
                    INSERT INTO historial_ajustes_inventario
                    (repuesto_id, cantidad_anterior, cantidad_nueva, diferencia, usuario_id, motivo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id, cantidad_anterior, nueva_cantidad, diferencia, user['id'], motivo
                ), commit=True)
                
                # Actualizar cantidad en repuestos
                execute_query(
                    "UPDATE repuestos SET cantidad_actual = %s, updated_by = %s WHERE id = %s",
                    (nueva_cantidad, user['id'], id),
                    commit=True
                )
                
                # Verificar alertas
                verificar_alertas(id)
                
                flash('Cantidad ajustada exitosamente', 'success')
                return redirect(url_for('lista_repuestos'))
            
            except Exception as e:
                logger.error(f"Error ajustando cantidad: {e}")
                flash('Error al ajustar la cantidad', 'danger')
        
        return render_template('repuestos/ajustar_cantidad.html', repuesto=repuesto)
    
    # ==================== MOVIMIENTOS DE INVENTARIO ====================
    
    @app.route('/movimientos')
    @login_required
    def lista_movimientos():
        """Lista de movimientos de inventario"""
        page = request.args.get('page', 1, type=int)
        tipo = request.args.get('tipo', '')
        
        per_page = app.config['ITEMS_PER_PAGE']
        offset = (page - 1) * per_page
        
        where_clauses = []
        params = []
        
        if tipo:
            where_clauses.append("tm.tipo = %s")
            params.append(tipo)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        total = execute_query(
            f"""SELECT COUNT(*) as count FROM movimientos_inventario mi
                JOIN tipos_movimiento tm ON mi.tipo_movimiento_id = tm.id
                WHERE {where_sql}""",
            tuple(params),
            fetch_one=True
        )['count']
        
        params.extend([per_page, offset])
        movimientos = execute_query(f"""
            SELECT mi.*, r.codigo as repuesto_codigo, r.nombre as repuesto_nombre,
                   tm.nombre as tipo_movimiento, tm.tipo,
                   u.nombre_completo as usuario,
                   ts.nombre_completo as tecnico_solicitante
            FROM movimientos_inventario mi
            JOIN repuestos r ON mi.repuesto_id = r.id
            JOIN tipos_movimiento tm ON mi.tipo_movimiento_id = tm.id
            JOIN usuarios u ON mi.usuario_id = u.id
            LEFT JOIN usuarios ts ON mi.tecnico_solicitante_id = ts.id
            WHERE {where_sql}
            ORDER BY mi.created_at DESC
            LIMIT %s OFFSET %s
        """, tuple(params), fetch_all=True)
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('movimientos/lista.html',
                             movimientos=movimientos,
                             page=page,
                             total_pages=total_pages,
                             tipo=tipo)
    
    @app.route('/movimientos/entrada', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA')
    def entrada_inventario():
        """Registrar entrada de inventario"""
        if request.method == 'POST':
            try:
                repuesto_id = request.form['repuesto_id']
                cantidad = int(request.form['cantidad'])
                tipo_movimiento_id = request.form['tipo_movimiento_id']
                precio_unitario = float(request.form.get('precio_unitario', 0))
                
                user = get_current_user()
                
                # Insertar movimiento
                execute_query("""
                    INSERT INTO movimientos_inventario
                    (repuesto_id, tipo_movimiento_id, cantidad, precio_unitario, 
                     usuario_id, estado, observaciones)
                    VALUES (%s, %s, %s, %s, %s, 'CONFIRMADO', %s)
                """, (
                    repuesto_id, tipo_movimiento_id, cantidad, precio_unitario,
                    user['id'], request.form.get('observaciones', '')
                ), commit=True)
                
                # Actualizar cantidad en repuestos
                execute_query("""
                    UPDATE repuestos 
                    SET cantidad_actual = cantidad_actual + %s
                    WHERE id = %s
                """, (cantidad, repuesto_id), commit=True)
                
                # Verificar alertas
                verificar_alertas(repuesto_id)
                
                flash('Entrada registrada exitosamente', 'success')
                return redirect(url_for('lista_movimientos'))
            
            except Exception as e:
                logger.error(f"Error en entrada de inventario: {e}")
                flash('Error al registrar la entrada', 'danger')
        
        # Obtener repuestos activos
        repuestos = execute_query(
            "SELECT id, codigo, nombre FROM repuestos WHERE activo = TRUE ORDER BY nombre",
            fetch_all=True
        )
        
        # Obtener tipos de movimiento de entrada
        tipos_movimiento = execute_query(
            "SELECT * FROM tipos_movimiento WHERE tipo = 'ENTRADA' ORDER BY nombre",
            fetch_all=True
        )
        
        return render_template('movimientos/entrada.html',
                             repuestos=repuestos,
                             tipos_movimiento=tipos_movimiento)
    
    @app.route('/movimientos/salida', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA')
    def salida_inventario():
        """Registrar salida de inventario"""
        if request.method == 'POST':
            try:
                repuesto_id = request.form['repuesto_id']
                cantidad = int(request.form['cantidad'])
                tipo_movimiento_id = request.form['tipo_movimiento_id']
                tecnico_solicitante_id = request.form.get('tecnico_solicitante_id') or None
                vehiculo_cliente_id = request.form.get('vehiculo_cliente_id') or None
                
                # Verificar stock disponible
                repuesto = execute_query(
                    "SELECT cantidad_actual, nombre FROM repuestos WHERE id = %s",
                    (repuesto_id,),
                    fetch_one=True
                )
                
                if repuesto['cantidad_actual'] < cantidad:
                    flash(f'Stock insuficiente. Disponible: {repuesto["cantidad_actual"]}', 'danger')
                    return redirect(url_for('salida_inventario'))
                
                user = get_current_user()
                
                # Insertar movimiento
                execute_query("""
                    INSERT INTO movimientos_inventario
                    (repuesto_id, tipo_movimiento_id, cantidad, usuario_id, 
                     tecnico_solicitante_id, vehiculo_cliente_id, estado, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, 'PENDIENTE', %s)
                """, (
                    repuesto_id, tipo_movimiento_id, cantidad, user['id'],
                    tecnico_solicitante_id, vehiculo_cliente_id,
                    request.form.get('observaciones', '')
                ), commit=True)
                
                # Actualizar cantidad en repuestos
                execute_query("""
                    UPDATE repuestos 
                    SET cantidad_actual = cantidad_actual - %s
                    WHERE id = %s
                """, (cantidad, repuesto_id), commit=True)
                
                # Verificar alertas
                verificar_alertas(repuesto_id)
                
                flash('Salida registrada exitosamente. Pendiente de confirmación en facturación.', 'success')
                return redirect(url_for('lista_movimientos'))
            
            except Exception as e:
                logger.error(f"Error en salida de inventario: {e}")
                flash('Error al registrar la salida', 'danger')
        
        # Obtener datos para el formulario
        repuestos = execute_query(
            "SELECT id, codigo, nombre, cantidad_actual FROM repuestos WHERE activo = TRUE ORDER BY nombre",
            fetch_all=True
        )
        
        tipos_movimiento = execute_query(
            "SELECT * FROM tipos_movimiento WHERE tipo = 'SALIDA' ORDER BY nombre",
            fetch_all=True
        )
        
        tecnicos = execute_query("""
            SELECT u.id, u.nombre_completo 
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE r.nombre = 'TECNICO' AND u.activo = TRUE
            ORDER BY u.nombre_completo
        """, fetch_all=True)
        
        clientes = execute_query(
            "SELECT id, nombre_completo, numero_documento FROM clientes WHERE activo = TRUE ORDER BY nombre_completo",
            fetch_all=True
        )
        
        return render_template('movimientos/salida.html',
                             repuestos=repuestos,
                             tipos_movimiento=tipos_movimiento,
                             tecnicos=tecnicos,
                             clientes=clientes)
    
    # ==================== ALERTAS ====================
    
    @app.route('/alertas')
    @login_required
    def lista_alertas():
        """Lista de alertas activas"""
        alertas = execute_query("""
            SELECT ai.*, r.codigo, r.nombre, r.cantidad_actual, r.cantidad_minima
            FROM alertas_inventario ai
            JOIN repuestos r ON ai.repuesto_id = r.id
            WHERE ai.estado = 'ACTIVA'
            ORDER BY ai.nivel_prioridad DESC, ai.created_at DESC
        """, fetch_all=True)
        
        return render_template('alertas/lista.html', alertas=alertas)
    
    @app.route('/api/alertas/marcar-leida/<int:id>', methods=['POST'])
    @login_required
    def marcar_alerta_leida(id):
        """Marcar alerta como leída"""
        try:
            execute_query(
                "UPDATE alertas_inventario SET estado = 'LEIDA' WHERE id = %s",
                (id,),
                commit=True
            )
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== GESTIÓN DE CLIENTES ====================
    
    @app.route('/clientes')
    @login_required
    def lista_clientes():
        """Lista de clientes"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        per_page = app.config['ITEMS_PER_PAGE']
        offset = (page - 1) * per_page
        
        where_clauses = ["c.activo = TRUE"]
        params = []
        
        if search:
            # Búsqueda por documento, nombre o placa de vehículo
            where_clauses.append("""
                (c.numero_documento LIKE %s OR c.nombre_completo LIKE %s OR 
                 EXISTS (SELECT 1 FROM vehiculos_clientes vc 
                         WHERE vc.cliente_id = c.id AND vc.placa LIKE %s AND vc.activo = TRUE))
            """)
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        where_sql = " AND ".join(where_clauses)
        
        # Consulta con subconsulta para contar vehículos
        total = execute_query(
            f"SELECT COUNT(DISTINCT c.id) as count FROM clientes c WHERE {where_sql}",
            tuple(params),
            fetch_one=True
        )['count']
        
        params.extend([per_page, offset])
        clientes = execute_query(f"""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM vehiculos_clientes vc 
                    WHERE vc.cliente_id = c.id AND vc.activo = TRUE) as total_vehiculos,
                   (SELECT GROUP_CONCAT(vc.placa SEPARATOR ', ') 
                    FROM vehiculos_clientes vc 
                    WHERE vc.cliente_id = c.id AND vc.activo = TRUE 
                    LIMIT 3) as placas_vehiculos
            FROM clientes c
            WHERE {where_sql}
            ORDER BY c.nombre_completo
            LIMIT %s OFFSET %s
        """, tuple(params), fetch_all=True)
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('clientes/lista.html',
                             clientes=clientes,
                             page=page,
                             total_pages=total_pages,
                             search=search)
    
    @app.route('/clientes/nuevo', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR')
    def nuevo_cliente():
        """Crear nuevo cliente"""
        if request.method == 'POST':
            try:
                execute_query("""
                    INSERT INTO clientes
                    (tipo_documento, numero_documento, nombre_completo, telefono, email, direccion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    request.form['tipo_documento'],
                    request.form['numero_documento'],
                    request.form['nombre_completo'],
                    request.form.get('telefono', ''),
                    request.form.get('email', ''),
                    request.form.get('direccion', '')
                ), commit=True)
                
                flash('Cliente creado exitosamente', 'success')
                return redirect(url_for('lista_clientes'))
            
            except Exception as e:
                logger.error(f"Error creando cliente: {e}")
                flash('Error al crear el cliente. Verifica que el número de documento no esté duplicado.', 'danger')
        
        return render_template('clientes/form.html', cliente=None)
    
    @app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR')
    def editar_cliente(id):
        """Editar cliente"""
        cliente = execute_query(
            "SELECT * FROM clientes WHERE id = %s",
            (id,),
            fetch_one=True
        )
        
        if not cliente:
            flash('Cliente no encontrado', 'danger')
            return redirect(url_for('lista_clientes'))
        
        if request.method == 'POST':
            try:
                execute_query("""
                    UPDATE clientes
                    SET tipo_documento = %s, numero_documento = %s, nombre_completo = %s,
                        telefono = %s, email = %s, direccion = %s
                    WHERE id = %s
                """, (
                    request.form['tipo_documento'],
                    request.form['numero_documento'],
                    request.form['nombre_completo'],
                    request.form.get('telefono', ''),
                    request.form.get('email', ''),
                    request.form.get('direccion', ''),
                    id
                ), commit=True)
                
                flash('Cliente actualizado exitosamente', 'success')
                return redirect(url_for('lista_clientes'))
            
            except Exception as e:
                logger.error(f"Error actualizando cliente: {e}")
                flash('Error al actualizar el cliente', 'danger')
        
        return render_template('clientes/form.html', cliente=cliente)
    
    @app.route('/clientes/<int:id>/vehiculos')
    @login_required
    def vehiculos_cliente(id):
        """Ver vehículos de un cliente"""
        cliente = execute_query(
            "SELECT * FROM clientes WHERE id = %s",
            (id,),
            fetch_one=True
        )
        
        if not cliente:
            flash('Cliente no encontrado', 'danger')
            return redirect(url_for('lista_clientes'))
        
        vehiculos = execute_query("""
            SELECT vc.*, mv.nombre as modelo_nombre, ma.nombre as marca_nombre
            FROM vehiculos_clientes vc
            JOIN modelos_vehiculos mv ON vc.modelo_vehiculo_id = mv.id
            JOIN marcas_vehiculos ma ON mv.marca_id = ma.id
            WHERE vc.cliente_id = %s AND vc.activo = TRUE
            ORDER BY vc.created_at DESC
        """, (id,), fetch_all=True)
        
        return render_template('clientes/vehiculos.html', cliente=cliente, vehiculos=vehiculos)
    
    # ==================== GESTIÓN DE VEHÍCULOS ====================
    
    @app.route('/vehiculos/nuevo/<int:cliente_id>', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR')
    def nuevo_vehiculo(cliente_id):
        """Crear nuevo vehículo para un cliente"""
        cliente = execute_query(
            "SELECT * FROM clientes WHERE id = %s",
            (cliente_id,),
            fetch_one=True
        )
        
        if not cliente:
            flash('Cliente no encontrado', 'danger')
            return redirect(url_for('lista_clientes'))
        
        if request.method == 'POST':
            try:
                execute_query("""
                    INSERT INTO vehiculos_clientes
                    (cliente_id, placa, modelo_vehiculo_id, anio, color, 
                     numero_motor, numero_chasis, kilometraje_actual, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    cliente_id,
                    request.form['placa'].upper(),
                    request.form['modelo_vehiculo_id'],
                    request.form.get('anio') or None,
                    request.form.get('color', ''),
                    request.form.get('numero_motor', ''),
                    request.form.get('numero_chasis', ''),
                    request.form.get('kilometraje_actual') or None,
                    request.form.get('observaciones', '')
                ), commit=True)
                
                flash('Vehículo registrado exitosamente', 'success')
                return redirect(url_for('vehiculos_cliente', id=cliente_id))
            
            except Exception as e:
                logger.error(f"Error registrando vehículo: {e}")
                flash('Error al registrar el vehículo. Verifica que la placa no esté duplicada.', 'danger')
        
        # Obtener marcas y modelos
        marcas = execute_query(
            "SELECT * FROM marcas_vehiculos ORDER BY nombre",
            fetch_all=True
        )
        
        modelos = execute_query(
            "SELECT mv.*, ma.nombre as marca_nombre FROM modelos_vehiculos mv JOIN marcas_vehiculos ma ON mv.marca_id = ma.id ORDER BY ma.nombre, mv.nombre",
            fetch_all=True
        )
        
        return render_template('vehiculos/form.html', cliente=cliente, vehiculo=None, marcas=marcas, modelos=modelos)
    
    @app.route('/vehiculos/<int:id>/editar', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR')
    def editar_vehiculo(id):
        """Editar vehículo"""
        vehiculo = execute_query(
            "SELECT * FROM vehiculos_clientes WHERE id = %s",
            (id,),
            fetch_one=True
        )
        
        if not vehiculo:
            flash('Vehículo no encontrado', 'danger')
            return redirect(url_for('lista_clientes'))
        
        cliente = execute_query(
            "SELECT * FROM clientes WHERE id = %s",
            (vehiculo['cliente_id'],),
            fetch_one=True
        )
        
        if request.method == 'POST':
            try:
                execute_query("""
                    UPDATE vehiculos_clientes
                    SET placa = %s, modelo_vehiculo_id = %s, anio = %s, color = %s,
                        numero_motor = %s, numero_chasis = %s, kilometraje_actual = %s,
                        observaciones = %s
                    WHERE id = %s
                """, (
                    request.form['placa'].upper(),
                    request.form['modelo_vehiculo_id'],
                    request.form.get('anio') or None,
                    request.form.get('color', ''),
                    request.form.get('numero_motor', ''),
                    request.form.get('numero_chasis', ''),
                    request.form.get('kilometraje_actual') or None,
                    request.form.get('observaciones', ''),
                    id
                ), commit=True)
                
                flash('Vehículo actualizado exitosamente', 'success')
                return redirect(url_for('vehiculos_cliente', id=vehiculo['cliente_id']))
            
            except Exception as e:
                logger.error(f"Error actualizando vehículo: {e}")
                flash('Error al actualizar el vehículo', 'danger')
        
        marcas = execute_query(
            "SELECT * FROM marcas_vehiculos ORDER BY nombre",
            fetch_all=True
        )
        
        modelos = execute_query(
            "SELECT mv.*, ma.nombre as marca_nombre FROM modelos_vehiculos mv JOIN marcas_vehiculos ma ON mv.marca_id = ma.id ORDER BY ma.nombre, mv.nombre",
            fetch_all=True
        )
        
        return render_template('vehiculos/form.html', cliente=cliente, vehiculo=vehiculo, marcas=marcas, modelos=modelos)
    
    # ==================== GESTIÓN DE USUARIOS ====================
    
    @app.route('/usuarios')
    @role_required('ADMINISTRADOR')
    def lista_usuarios():
        """Lista de usuarios"""
        usuarios = execute_query("""
            SELECT u.*, r.nombre as rol_nombre
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.nombre_completo
        """, fetch_all=True)
        
        return render_template('usuarios/lista.html', usuarios=usuarios)
    
    @app.route('/usuarios/nuevo', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR')
    def nuevo_usuario():
        """Crear nuevo usuario"""
        if request.method == 'POST':
            try:
                password_hash = hash_password(request.form['password'])
                current_user_data = get_current_user()
                
                execute_query("""
                    INSERT INTO usuarios
                    (username, password_hash, nombre_completo, email, rol_id, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    request.form['username'],
                    password_hash,
                    request.form['nombre_completo'],
                    request.form.get('email', ''),
                    request.form['rol_id'],
                    current_user_data['id']
                ), commit=True)
                
                flash('Usuario creado exitosamente', 'success')
                return redirect(url_for('lista_usuarios'))
            
            except Exception as e:
                logger.error(f"Error creando usuario: {e}")
                flash('Error al crear el usuario', 'danger')
        
        roles = execute_query("SELECT * FROM roles ORDER BY nombre", fetch_all=True)
        return render_template('usuarios/form.html', roles=roles, usuario=None)
    
    @app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
    @role_required('ADMINISTRADOR')
    def editar_usuario(id):
        """Editar usuario"""
        usuario = execute_query(
            "SELECT * FROM usuarios WHERE id = %s",
            (id,),
            fetch_one=True
        )
        
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('lista_usuarios'))
        
        if request.method == 'POST':
            try:
                current_user_data = get_current_user()
                
                # Si se proporciona nueva contraseña, actualizarla
                if request.form.get('password'):
                    password_hash = hash_password(request.form['password'])
                    execute_query("""
                        UPDATE usuarios 
                        SET nombre_completo = %s, email = %s, rol_id = %s, 
                            password_hash = %s, updated_by = %s
                        WHERE id = %s
                    """, (
                        request.form['nombre_completo'],
                        request.form.get('email', ''),
                        request.form['rol_id'],
                        password_hash,
                        current_user_data['id'],
                        id
                    ), commit=True)
                else:
                    execute_query("""
                        UPDATE usuarios 
                        SET nombre_completo = %s, email = %s, rol_id = %s, updated_by = %s
                        WHERE id = %s
                    """, (
                        request.form['nombre_completo'],
                        request.form.get('email', ''),
                        request.form['rol_id'],
                        current_user_data['id'],
                        id
                    ), commit=True)
                
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('lista_usuarios'))
            
            except Exception as e:
                logger.error(f"Error actualizando usuario: {e}")
                flash('Error al actualizar el usuario', 'danger')
        
        roles = execute_query("SELECT * FROM roles ORDER BY nombre", fetch_all=True)
        return render_template('usuarios/form.html', roles=roles, usuario=usuario)
    
    @app.route('/usuarios/<int:id>/toggle-estado', methods=['POST'])
    @role_required('ADMINISTRADOR')
    def toggle_estado_usuario(id):
        """Activar o desactivar usuario"""
        try:
            usuario = execute_query(
                "SELECT activo FROM usuarios WHERE id = %s",
                (id,),
                fetch_one=True
            )
            
            if not usuario:
                flash('Usuario no encontrado', 'danger')
                return redirect(url_for('lista_usuarios'))
            
            nuevo_estado = not usuario['activo']
            current_user_data = get_current_user()
            
            execute_query(
                "UPDATE usuarios SET activo = %s, updated_by = %s WHERE id = %s",
                (nuevo_estado, current_user_data['id'], id),
                commit=True
            )
            
            estado_texto = 'activado' if nuevo_estado else 'desactivado'
            flash(f'Usuario {estado_texto} exitosamente', 'success')
        except Exception as e:
            logger.error(f"Error cambiando estado de usuario: {e}")
            flash('Error al cambiar el estado del usuario', 'danger')
        
        return redirect(url_for('lista_usuarios'))
    
    # ==================== FUNCIONES AUXILIARES ====================
    
    def verificar_alertas(repuesto_id):
        """Verifica y crea alertas de inventario para un repuesto"""
        repuesto = execute_query("""
            SELECT id, codigo, nombre, cantidad_actual, cantidad_minima
            FROM repuestos WHERE id = %s
        """, (repuesto_id,), fetch_one=True)
        
        if not repuesto:
            return
        
        # Resolver alertas si el stock está bien
        if repuesto['cantidad_actual'] > repuesto['cantidad_minima']:
            execute_query("""
                UPDATE alertas_inventario 
                SET estado = 'RESUELTA', resolved_at = NOW()
                WHERE repuesto_id = %s AND estado = 'ACTIVA'
            """, (repuesto_id,), commit=True)
            return
        
        # Determinar tipo de alerta
        if repuesto['cantidad_actual'] == 0:
            tipo_alerta = 'AGOTADO'
            nivel = 'CRITICA'
            mensaje = f"El repuesto {repuesto['nombre']} ({repuesto['codigo']}) está AGOTADO"
        elif repuesto['cantidad_actual'] <= repuesto['cantidad_minima']:
            tipo_alerta = 'STOCK_BAJO'
            nivel = 'ALTA'
            mensaje = f"El repuesto {repuesto['nombre']} ({repuesto['codigo']}) tiene stock bajo: {repuesto['cantidad_actual']} unidades"
        else:
            return
        
        # Verificar si ya existe alerta activa
        alerta_existente = execute_query("""
            SELECT id FROM alertas_inventario
            WHERE repuesto_id = %s AND estado = 'ACTIVA' AND tipo_alerta = %s
        """, (repuesto_id, tipo_alerta), fetch_one=True)
        
        if not alerta_existente:
            # Crear alerta
            alerta_id = execute_query("""
                INSERT INTO alertas_inventario
                (repuesto_id, tipo_alerta, nivel_prioridad, mensaje)
                VALUES (%s, %s, %s, %s)
            """, (repuesto_id, tipo_alerta, nivel, mensaje), commit=True)
            
            # Notificar a administradores y almacenistas
            usuarios_notificar = execute_query("""
                SELECT u.id FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
                WHERE r.nombre IN ('ADMINISTRADOR', 'ALMACENISTA') AND u.activo = TRUE
            """, fetch_all=True)
            
            for usuario in usuarios_notificar:
                execute_query("""
                    INSERT INTO notificaciones_usuarios (usuario_id, alerta_id)
                    VALUES (%s, %s)
                """, (usuario['id'], alerta_id), commit=True)
    
    # ==================== API ENDPOINTS ====================
    
    @app.route('/api/repuestos/buscar')
    @login_required
    def api_buscar_repuestos():
        """API para buscar repuestos (autocomplete)"""
        query = request.args.get('q', '')
        
        repuestos = execute_query("""
            SELECT id, codigo, nombre, cantidad_actual, precio_venta
            FROM repuestos
            WHERE activo = TRUE AND (codigo LIKE %s OR nombre LIKE %s)
            LIMIT 10
        """, (f'%{query}%', f'%{query}%'), fetch_all=True)
        
        return jsonify([dict(r) for r in repuestos])
    
    @app.route('/api/vehiculos-cliente/<int:cliente_id>')
    @login_required
    def api_vehiculos_cliente(cliente_id):
        """API para obtener vehículos de un cliente"""
        vehiculos = execute_query("""
            SELECT vc.id, vc.placa, mv.nombre as modelo, ma.nombre as marca
            FROM vehiculos_clientes vc
            JOIN modelos_vehiculos mv ON vc.modelo_vehiculo_id = mv.id
            JOIN marcas_vehiculos ma ON mv.marca_id = ma.id
            WHERE vc.cliente_id = %s AND vc.activo = TRUE
        """, (cliente_id,), fetch_all=True)
        
        return jsonify([dict(v) for v in vehiculos])
    
    @app.route('/api/notificaciones')
    @login_required
    def api_notificaciones():
        """API para obtener notificaciones del usuario"""
        user = get_current_user()
        
        notificaciones = execute_query("""
            SELECT n.id, n.leida, n.created_at, 
                   a.mensaje, a.tipo_alerta, a.nivel_prioridad
            FROM notificaciones_usuarios n
            JOIN alertas_inventario a ON n.alerta_id = a.id
            WHERE n.usuario_id = %s AND n.leida = FALSE
            ORDER BY n.created_at DESC
            LIMIT 20
        """, (user['id'],), fetch_all=True)
        
        return jsonify([dict(n) for n in notificaciones])
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
