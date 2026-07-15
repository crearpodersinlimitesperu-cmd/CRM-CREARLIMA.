from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db_core import Base

class Coordinadora(Base):
    __tablename__ = 'coordinadoras'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    rol = Column(String(50), default="CC")
    activa = Column(Boolean, default=True)

    asignaciones = relationship("Asignacion", back_populates="coordinadora")
    gestiones = relationship("GestionLlamada", back_populates="coordinadora")


class Participante(Base):
    __tablename__ = 'participantes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20), unique=True, index=True, nullable=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=True)
    telefono = Column(String(30), nullable=True, index=True)
    email = Column(String(150), nullable=True)
    imo_enrolador = Column(String(100), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    asignaciones = relationship("Asignacion", back_populates="participante")
    gestiones = relationship("GestionLlamada", back_populates="participante")


class Evento(Base):
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False) # Ej: C1E28
    nombre = Column(String(150), nullable=False)
    fecha_inicio = Column(DateTime, nullable=True)


class Asignacion(Base):
    __tablename__ = 'asignaciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    participante_id = Column(Integer, ForeignKey('participantes.id'))
    coordinadora_id = Column(Integer, ForeignKey('coordinadoras.id'))
    evento_id = Column(Integer, ForeignKey('eventos.id'))
    estado_c1 = Column(String(50), nullable=True) # Confirmado, Pendiente
    estado_c2 = Column(String(50), nullable=True)
    asistencia = Column(Boolean, default=False)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)

    participante = relationship("Participante", back_populates="asignaciones")
    coordinadora = relationship("Coordinadora", back_populates="asignaciones")


class GestionLlamada(Base):
    __tablename__ = 'gestiones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    participante_id = Column(Integer, ForeignKey('participantes.id'))
    coordinadora_id = Column(Integer, ForeignKey('coordinadoras.id'))
    resultado = Column(String(100), nullable=False) # OK, Rebote, No contesta
    nota = Column(String(500), nullable=True)
    fecha_gestion = Column(DateTime, default=datetime.utcnow)
    
    participante = relationship("Participante", back_populates="gestiones")
    coordinadora = relationship("Coordinadora", back_populates="gestiones")


class TransaccionFinanciera(Base):
    __tablename__ = 'transacciones_financieras'
    id = Column(Integer, primary_key=True, autoincrement=True)
    concepto = Column(String(200), nullable=False)
    monto = Column(Integer, nullable=False) # Guardamos en entero para evitar problemas de float si no hay centavos, o Float
    tipo = Column(String(20), nullable=False) # INGRESO, EGRESO
    categoria = Column(String(100), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    trazabilidad_hash = Column(String(64), unique=True, nullable=True) # Hash SHA-256 para inmutabilidad
