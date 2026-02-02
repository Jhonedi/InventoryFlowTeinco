from functools import wraps
from flask import session, redirect, url_for, flash, request
import bcrypt
from database import execute_query

def hash_password(password):
    """Genera un hash de la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Verifica si una contraseña coincide con el hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(username, password):
    """
    Autentica un usuario
    
    Args:
        username: Nombre de usuario
        password: Contraseña
    
    Returns:
        dict con datos del usuario si es exitoso, None si falla
    """
    query = """
        SELECT u.id, u.username, u.nombre_completo, u.email, u.password_hash,
               u.activo, r.id as rol_id, r.nombre as rol_nombre
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.username = %s AND u.activo = TRUE
    """
    
    user = execute_query(query, (username,), fetch_one=True)
    
    if user and check_password(password, user['password_hash']):
        # Crear sesión
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['nombre_completo'] = user['nombre_completo']
        session['rol_id'] = user['rol_id']
        session['rol_nombre'] = user['rol_nombre']
        session.permanent = True
        
        return {
            'id': user['id'],
            'username': user['username'],
            'nombre_completo': user['nombre_completo'],
            'email': user['email'],
            'rol_id': user['rol_id'],
            'rol_nombre': user['rol_nombre']
        }
    
    return None

def logout_user():
    """Cierra la sesión del usuario"""
    session.clear()

def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'username': session['username'],
            'nombre_completo': session['nombre_completo'],
            'rol_id': session['rol_id'],
            'rol_nombre': session['rol_nombre']
        }
    return None

def is_authenticated():
    """Verifica si hay un usuario autenticado"""
    return 'user_id' in session

# Decoradores para proteger rutas

def login_required(f):
    """Decorador que requiere autenticación para acceder a una ruta"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Decorador que requiere uno de los roles especificados
    
    Uso:
        @role_required('ADMINISTRADOR', 'ALMACENISTA')
        def mi_ruta():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Debe iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('login', next=request.url))
            
            user = get_current_user()
            if user['rol_nombre'] not in allowed_roles:
                flash('No tiene permisos para acceder a esta página', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Funciones de verificación de permisos

def can_view_inventory():
    """Verifica si el usuario puede ver el inventario"""
    user = get_current_user()
    if not user:
        return False
    return user['rol_nombre'] in ['ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR', 'TECNICO']

def can_edit_inventory():
    """Verifica si el usuario puede editar el inventario"""
    user = get_current_user()
    if not user:
        return False
    return user['rol_nombre'] in ['ADMINISTRADOR', 'ALMACENISTA']

def can_create_sales():
    """Verifica si el usuario puede crear ventas"""
    user = get_current_user()
    if not user:
        return False
    return user['rol_nombre'] in ['ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR']

def can_confirm_sales():
    """Verifica si el usuario puede confirmar ventas (facturación)"""
    user = get_current_user()
    if not user:
        return False
    return user['rol_nombre'] in ['ADMINISTRADOR', 'VENDEDOR']

def can_manage_users():
    """Verifica si el usuario puede gestionar usuarios"""
    user = get_current_user()
    if not user:
        return False
    return user['rol_nombre'] == 'ADMINISTRADOR'

def can_view_reports():
    """Verifica si el usuario puede ver reportes"""
    user = get_current_user()
    if not user:
        return False
    return user['rol_nombre'] in ['ADMINISTRADOR', 'ALMACENISTA', 'VENDEDOR']

def get_permissions():
    """Obtiene los permisos del usuario actual"""
    return {
        'can_view_inventory': can_view_inventory(),
        'can_edit_inventory': can_edit_inventory(),
        'can_create_sales': can_create_sales(),
        'can_confirm_sales': can_confirm_sales(),
        'can_manage_users': can_manage_users(),
        'can_view_reports': can_view_reports()
    }
