# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import hashlib

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.clave = hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        return self.clave == hashlib.md5(password.encode()).hexdigest()


class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    correo = db.Column(db.String(100))

    ventas = db.relationship('Venta', backref='cliente', lazy=True)


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    correo = db.Column(db.String(100))

    compras = db.relationship('Compra', backref='proveedor', lazy=True)


class Producto(db.Model):
    __tablename__ = "productos"

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_compra = db.Column(db.Numeric(10, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'))

    @property
    def stock(self):
        from sqlalchemy import func
        comprado = db.session.query(func.sum(DetalleCompra.cantidad)).filter_by(id_producto=self.id_producto).scalar() or 0
        vendido = db.session.query(func.sum(DetalleVenta.cantidad)).filter_by(id_producto=self.id_producto).scalar() or 0
        return comprado - vendido


class Venta(db.Model):
    __tablename__ = "ventas"

    id_venta = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'))
    fecha_venta = db.Column(db.Date, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2))

    detalles = db.relationship('DetalleVenta', backref='venta', cascade="all, delete-orphan", lazy=True)


class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id_venta'))
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    producto = db.relationship('Producto', backref='detalles_venta')

    @property
    def subtotal(self):
        return float(self.cantidad) * float(self.precio_unitario)


class Compra(db.Model):
    __tablename__ = "compras"

    id_compra = db.Column(db.Integer, primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    fecha_compra = db.Column(db.Date, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    detalles = db.relationship('DetalleCompra', backref='compra', cascade="all, delete-orphan", lazy=True)


class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compras'

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_compra = db.Column(db.Integer, db.ForeignKey('compras.id_compra'))
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2))

    producto = db.relationship('Producto', backref='detalles_compra', lazy=True)

    @property
    def calcular_subtotal(self):
        return self.cantidad * self.precio_unitario