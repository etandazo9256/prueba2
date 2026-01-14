# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import func
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ----------------------
# CONFIGURACIÓN APP SIMPLIFICADA (SIN DOCKER)
# ----------------------

app = Flask(__name__)

# Configuración directa para Supabase o PostgreSQL local
# Opción 1: Conectar a Supabase (RECOMENDADO)
SUPABASE_URL = os.getenv("SUPABASE_URL", "postgresql://postgres.chfuqwpcagmioazqrsjp:Pa0la9256.2204@aws-0-us-west-2.pooler.supabase.com:5432/postgres")

# Opción 2: PostgreSQL local (para desarrollo)
LOCAL_DB = "postgresql://postgres:2637278910@localhost:5432/usuarios_app"

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-inventario-789")
app.config["SQLALCHEMY_DATABASE_URI"] = SUPABASE_URL  # Cambia a LOCAL_DB si usas local
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ----------------------
# IMPORTAR MODELOS
# ----------------------

# Importar después de configurar la app para evitar circular imports
from models import db, Usuario, Producto, Cliente, Proveedor, Venta, Compra, DetalleVenta, DetalleCompra

# Inicializar la base de datos con la app
db.init_app(app)

# ----------------------
# LOGIN MANAGER
# ----------------------

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para acceder al sistema."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ----------------------
# FUNCIONES DE REPORTES (Versión simplificada)
# ----------------------

def generar_reporte_simple(titulo, datos, tipo="pdf"):
    """Función simple para generar reportes básicos"""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    
    buffer = BytesIO()
    
    if tipo == "pdf":
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Reporte de {titulo}")
        c.drawString(50, height - 70, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Contenido
        c.setFont("Helvetica", 10)
        y_position = height - 100
        
        for i, item in enumerate(datos[:30]):  # Limitar a 30 items
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - 50
            
            if isinstance(item, dict):
                texto = f"{i+1}. {item.get('nombre', 'Sin nombre')}"
            else:
                texto = f"{i+1}. {str(item)}"
            
            c.drawString(50, y_position, texto[:80])  # Limitar longitud
            y_position -= 20
        
        c.save()
        buffer.seek(0)
        return buffer
    
    return None

# ----------------------
# CONTEXT PROCESSOR
# ----------------------

@app.context_processor
def inject_hoy():
    return dict(hoy=datetime.now())

# ----------------------
# AUTENTICACIÓN
# ----------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()
        
        user = Usuario.query.filter_by(usuario=usuario).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'¡Bienvenido {user.usuario}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

# ----------------------
# DASHBOARD
# ----------------------

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        stats = {
            'total_ventas': float(db.session.query(func.sum(Venta.total)).scalar() or 0),
            'total_compras': float(db.session.query(func.sum(Compra.total)).scalar() or 0),
            'total_productos': Producto.query.count(),
            'total_clientes': Cliente.query.count(),
            'total_proveedores': Proveedor.query.count()
        }

        ventas_recientes = (
            Venta.query
            .order_by(Venta.fecha_venta.desc())
            .limit(5)
            .all()
        )

        # Productos con stock bajo
        productos_bajo_stock = []
        for producto in Producto.query.all():
            if producto.stock <= 5:
                productos_bajo_stock.append(producto)

        return render_template(
            'dashboard.html',
            stats=stats,
            ventas_recientes=ventas_recientes,
            productos_bajo_stock=productos_bajo_stock
        )

    except Exception as e:
        flash(f'Error al cargar dashboard: {str(e)}', 'danger')

        stats = {
            'total_ventas': 0,
            'total_compras': 0,
            'total_productos': 0,
            'total_clientes': 0,
            'total_proveedores': 0
        }

        return render_template(
            'dashboard.html',
            stats=stats,
            ventas_recientes=[],
            productos_bajo_stock=[]
        )

# ----------------------
# REPORTES - DASHBOARD
# ----------------------

@app.route('/reportes')
@login_required
def reportes_dashboard():
    """Dashboard de reportes"""
    try:
        stats = {
            'total_ventas': float(db.session.query(func.sum(Venta.total)).scalar() or 0),
            'total_compras': float(db.session.query(func.sum(Compra.total)).scalar() or 0),
            'total_productos': Producto.query.count(),
            'total_clientes': Cliente.query.count(),
            'total_proveedores': Proveedor.query.count(),
            'total_usuarios': Usuario.query.count()
        }
        
        return render_template('reportes/dashboard.html', stats=stats)
    except Exception as e:
        flash(f'Error al cargar dashboard de reportes: {str(e)}', 'danger')
        stats = {
            'total_ventas': 0,
            'total_compras': 0,
            'total_productos': 0,
            'total_clientes': 0,
            'total_proveedores': 0,
            'total_usuarios': 0
        }
        return render_template('reportes/dashboard.html', stats=stats)

# ----------------------
# CLIENTES
# ----------------------

@app.route('/clientes')
@login_required
def listar_clientes():
    try:
        clientes = Cliente.query.order_by(Cliente.nombre).all()
        return render_template('clientes/listar.html', clientes=clientes)
    except Exception as e:
        flash(f'Error al cargar clientes: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def crear_cliente():
    if request.method == 'POST':
        try:
            cliente = Cliente(
                nombre=request.form['nombre'],
                cedula=request.form.get('cedula', ''),
                telefono=request.form.get('telefono', ''),
                direccion=request.form.get('direccion', ''),
                correo=request.form.get('correo', '')
            )
            
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cliente: {str(e)}', 'danger')
    
    return render_template('clientes/crear.html')

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            cliente.nombre = request.form['nombre']
            cliente.cedula = request.form.get('cedula', '')
            cliente.telefono = request.form.get('telefono', '')
            cliente.direccion = request.form.get('direccion', '')
            cliente.correo = request.form.get('correo', '')
            
            db.session.commit()
            flash('Cliente actualizado exitosamente', 'success')
            return redirect(url_for('listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cliente: {str(e)}', 'danger')
    
    return render_template('clientes/editar.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    try:
        tiene_ventas = Venta.query.filter_by(id_cliente=id).first()
        if tiene_ventas:
            flash('No se puede eliminar: el cliente tiene ventas registradas', 'warning')
        else:
            db.session.delete(cliente)
            db.session.commit()
            flash('Cliente eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('listar_clientes'))

# ----------------------
# PRODUCTOS
# ----------------------

@app.route('/productos')
@login_required
def listar_productos():
    try:
        productos = Producto.query.order_by(Producto.nombre).all()
        return render_template('productos/listar.html', productos=productos)
    except Exception as e:
        flash(f'Error al cargar productos: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        try:
            producto = Producto(
                nombre=request.form['nombre'],
                descripcion=request.form.get('descripcion', ''),
                precio_compra=float(request.form.get('precio_compra', 0)),
                precio_venta=float(request.form.get('precio_venta', 0)),
                id_proveedor=request.form.get('id_proveedor') or None
            )
            
            db.session.add(producto)
            db.session.commit()
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('listar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear producto: {str(e)}', 'danger')
    
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('productos/crear.html', proveedores=proveedores)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            producto.nombre = request.form['nombre']
            producto.descripcion = request.form.get('descripcion', '')
            producto.precio_compra = float(request.form.get('precio_compra', 0))
            producto.precio_venta = float(request.form.get('precio_venta', 0))
            producto.id_proveedor = request.form.get('id_proveedor') or None
            
            db.session.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('listar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar producto: {str(e)}', 'danger')
    
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('productos/editar.html', producto=producto, proveedores=proveedores)

@app.route('/productos/<int:id>')
@login_required
def ver_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template('productos/ver.html', producto=producto)

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        tiene_ventas = DetalleVenta.query.filter_by(id_producto=id).first()
        tiene_compras = DetalleCompra.query.filter_by(id_producto=id).first()
        
        if tiene_ventas or tiene_compras:
            flash('No se puede eliminar: el producto tiene ventas o compras registradas', 'warning')
        else:
            db.session.delete(producto)
            db.session.commit()
            flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('listar_productos'))

# ----------------------
# VENTAS
# ----------------------

@app.route('/ventas')
@login_required
def listar_ventas():
    try:
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
        return render_template('ventas/listar.html', ventas=ventas)
    except Exception as e:
        flash(f'Error al cargar ventas: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
def crear_venta():
    if request.method == 'POST':
        try:
            producto_id = request.form['producto_id']
            cantidad = int(request.form['cantidad'])
            
            producto = Producto.query.get(producto_id)
            if not producto:
                flash('Producto no encontrado', 'danger')
                return redirect(url_for('crear_venta'))
            
            if producto.stock < cantidad:
                flash(f'Stock insuficiente. Disponible: {producto.stock}', 'danger')
                return redirect(url_for('crear_venta'))
            
            total = producto.precio_venta * cantidad
            
            venta = Venta(
                id_cliente=int(request.form.get('id_cliente') or 0),
                total=total
            )
            db.session.add(venta)
            db.session.flush()
            
            detalle = DetalleVenta(
                id_venta=venta.id_venta,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_venta
            )
            db.session.add(detalle)
            
            db.session.commit()
            flash(f'Venta registrada exitosamente. Total: ${total:.2f}', 'success')
            return redirect(url_for('listar_ventas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar venta: {str(e)}', 'danger')
    
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    productos = Producto.query.order_by(Producto.nombre).all()
    
    return render_template('ventas/crear_simple.html', clientes=clientes, productos=productos)

@app.route('/ventas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_venta(id):
    venta = Venta.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Aquí iría la lógica de edición completa
            flash('Funcionalidad de edición en desarrollo', 'info')
            return redirect(url_for('listar_ventas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar venta: {str(e)}', 'danger')
    
    return render_template('ventas/editar.html', venta=venta)

@app.route('/ventas/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    venta = Venta.query.get_or_404(id)
    
    try:
        db.session.delete(venta)
        db.session.commit()
        flash('Venta eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('listar_ventas'))

# ----------------------
# COMPRAS
# ----------------------

@app.route('/compras')
@login_required
def listar_compras():
    try:
        compras = Compra.query.order_by(Compra.fecha_compra.desc()).all()
        return render_template('compras/listar.html', compras=compras)
    except Exception as e:
        flash(f'Error al cargar compras: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/compras/nueva', methods=['GET', 'POST'])
@login_required
def crear_compra():
    if request.method == 'POST':
        try:
            producto_id = request.form['producto_id']
            cantidad = int(request.form['cantidad'])
            precio = float(request.form['precio'])
            
            producto = Producto.query.get(producto_id)
            if not producto:
                flash('Producto no encontrado', 'danger')
                return redirect(url_for('crear_compra'))
            
            total = precio * cantidad
            
            compra = Compra(
                id_proveedor=int(request.form['id_proveedor']),
                total=total
            )
            db.session.add(compra)
            db.session.flush()
            
            detalle = DetalleCompra(
                id_compra=compra.id_compra,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=total
            )
            db.session.add(detalle)
            
            db.session.commit()
            flash(f'Compra registrada exitosamente. Total: ${total:.2f}', 'success')
            return redirect(url_for('listar_compras'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar compra: {str(e)}', 'danger')
    
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    productos = Producto.query.order_by(Producto.nombre).all()
    
    return render_template('compras/crear_simple.html', proveedores=proveedores, productos=productos)

@app.route('/compras/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_compra(id):
    compra = Compra.query.get_or_404(id)
    
    try:
        db.session.delete(compra)
        db.session.commit()
        flash('Compra eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('listar_compras'))

# ----------------------
# PROVEEDORES
# ----------------------

@app.route('/proveedores')
@login_required
def listar_proveedores():
    try:
        proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
        return render_template('proveedores/listar.html', proveedores=proveedores)
    except Exception as e:
        flash(f'Error al cargar proveedores: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def crear_proveedor():
    if request.method == 'POST':
        try:
            proveedor = Proveedor(
                nombre=request.form['nombre'],
                ruc=request.form.get('ruc', ''),
                telefono=request.form.get('telefono', ''),
                direccion=request.form.get('direccion', ''),
                correo=request.form.get('correo', '')
            )
            
            db.session.add(proveedor)
            db.session.commit()
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear proveedor: {str(e)}', 'danger')
    
    return render_template('proveedores/crear.html')

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            proveedor.nombre = request.form['nombre']
            proveedor.ruc = request.form.get('ruc', '')
            proveedor.telefono = request.form.get('telefono', '')
            proveedor.direccion = request.form.get('direccion', '')
            proveedor.correo = request.form.get('correo', '')
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'danger')
    
    return render_template('proveedores/editar.html', proveedor=proveedor)

# ----------------------
# INVENTARIO
# ----------------------

@app.route('/inventario')
@login_required
def inventario():
    try:
        productos = Producto.query.order_by(Producto.nombre).all()
        
        total_valor_inventario = 0
        total_productos = len(productos)
        productos_bajo_stock = 0
        productos_sin_stock = 0
        
        for producto in productos:
            stock = producto.stock
            valor_producto = float(producto.precio_compra) * stock
            total_valor_inventario += valor_producto
            
            if stock <= 0:
                productos_sin_stock += 1
            elif stock <= 5:
                productos_bajo_stock += 1
        
        return render_template('inventario/dashboard.html',
                             productos=productos,
                             total_valor_inventario=total_valor_inventario,
                             total_productos=total_productos,
                             productos_bajo_stock=productos_bajo_stock,
                             productos_sin_stock=productos_sin_stock)
    except Exception as e:
        flash(f'Error al cargar inventario: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ----------------------
# USUARIOS
# ----------------------

@app.route('/usuarios')
@login_required
def listar_usuarios():
    try:
        usuarios = Usuario.query.order_by(Usuario.usuario).all()
        return render_template('usuarios/listar.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Error al cargar usuarios: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if request.method == 'POST':
        try:
            usuario_nombre = request.form['usuario']
            password = request.form['password']
            confirmar_password = request.form['confirmar_password']
            
            if password != confirmar_password:
                flash('Las contraseñas no coinciden', 'warning')
                return redirect(url_for('crear_usuario'))
            
            usuario_existente = Usuario.query.filter_by(usuario=usuario_nombre).first()
            if usuario_existente:
                flash('El nombre de usuario ya existe', 'danger')
                return redirect(url_for('crear_usuario'))
            
            usuario = Usuario(usuario=usuario_nombre)
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')
    
    return render_template('usuarios/crear.html')

# ----------------------
# REPORTES - SIMPLIFICADOS
# ----------------------

@app.route('/reportes/ventas/descargar')
@login_required
def descargar_reporte_ventas():
    """Descargar reporte de ventas en PDF"""
    try:
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
        pdf_buffer = generar_reporte_simple("Ventas", ventas)
        
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f'reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                mimetype='application/pdf'
            )
        else:
            flash('Error al generar PDF', 'danger')
            return redirect(url_for('listar_ventas'))
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'danger')
        return redirect(url_for('listar_ventas'))

@app.route('/reportes/inventario/descargar')
@login_required
def descargar_reporte_inventario():
    """Descargar reporte de inventario en PDF"""
    try:
        productos = Producto.query.order_by(Producto.nombre).all()
        pdf_buffer = generar_reporte_simple("Inventario", productos)
        
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f'reporte_inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                mimetype='application/pdf'
            )
        else:
            flash('Error al generar PDF', 'danger')
            return redirect(url_for('inventario'))
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'danger')
        return redirect(url_for('inventario'))

# ----------------------
# INICIALIZACIÓN
# ----------------------

def init_sistema():
    print('🔍 Iniciando sistema...')
    
    with app.app_context():
        try:
            db.create_all()
            
            admin = Usuario.query.filter_by(usuario='admin').first()
            
            if not admin:
                print('👤 Creando usuario admin...')
                admin = Usuario(usuario='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print('✅ Usuario admin creado: admin / admin123')
            else:
                print('✅ Usuario admin ya existe')
                
        except Exception as e:
            print(f'⚠️ Error: {e}')

# ----------------------
# MAIN
# ----------------------

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 SISTEMA DE INVENTARIO - FLASK')
    print('=' * 60)
    print(f'📊 Base de datos: {app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1]}')
    
    init_sistema()
    
    print('🌐 Servidor: http://localhost:5000')
    print('👤 Usuario: admin / admin123')
    print('=' * 60)
    print('⚠️  Presiona Ctrl+C para detener el servidor')
    print('=' * 60)
    
    # Ejecutar servidor
    app.run(host="127.0.0.1", debug=True, port=5000)