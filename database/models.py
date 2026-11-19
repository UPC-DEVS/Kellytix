from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# 1. TABLA DE USUARIOS
class Usuario(Base):
    __tablename__ = 'usuarios'     

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    bankroll_fiat = Column(Numeric(10, 2), default=0.0)
    bankroll_unidades = Column(Numeric(10, 2), default=0.0)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relación con apuestas
    apuestas = relationship("ApuestaUsuario", back_populates="usuario")


# 2. TABLA DE PARTIDOS HISTÓRICOS (37 Columnas del Dataset Procesado)
class PartidoHistorico(Base):
    __tablename__ = 'partidos_historico'
    __table_args__ = (
        UniqueConstraint(
            'liga',
            'fecha',
            'equipo_local',
            'equipo_visitante',
            name='uq_partido_historico_clave',
        ),
    )

    id_partido = Column(Integer, primary_key=True, autoincrement=True)
    liga = Column(String(10), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(String(8), nullable=True)
    equipo_local = Column(String(50), nullable=False)
    equipo_visitante = Column(String(50), nullable=False)

    # Ratings Elo y Forma pre-partido
    elo_local = Column(Numeric(6, 2), nullable=True)
    elo_visitante = Column(Numeric(6, 2), nullable=True)
    forma3_local = Column(Integer, nullable=True)
    forma5_local = Column(Integer, nullable=True)
    forma3_visitante = Column(Integer, nullable=True)
    forma5_visitante = Column(Integer, nullable=True)
    puntos_ult5_local = Column(Numeric(5, 2), nullable=True)
    goles_favor_ult5_local = Column(Numeric(5, 2), nullable=True)
    goles_contra_ult5_local = Column(Numeric(5, 2), nullable=True)
    dias_descanso_local = Column(Integer, nullable=True)
    puntos_ult5_visitante = Column(Numeric(5, 2), nullable=True)
    goles_favor_ult5_visitante = Column(Numeric(5, 2), nullable=True)
    goles_contra_ult5_visitante = Column(Numeric(5, 2), nullable=True)
    dias_descanso_visitante = Column(Integer, nullable=True)

    # Marcador final y al descanso
    goles_local = Column(Integer, nullable=False)
    goles_visitante = Column(Integer, nullable=False)
    resultado_final = Column(String(5), nullable=False)
    goles_ht_local = Column(Integer, nullable=True)
    goles_ht_visitante = Column(Integer, nullable=True)
    resultado_ht = Column(String(5), nullable=True)

    # Estadísticas de juego
    tiros_local = Column(Integer, nullable=True)
    tiros_visitante = Column(Integer, nullable=True)
    tiros_puerta_local = Column(Integer, nullable=True)
    tiros_puerta_visitante = Column(Integer, nullable=True)
    faltas_local = Column(Integer, nullable=True)
    faltas_visitante = Column(Integer, nullable=True)
    corneres_local = Column(Integer, nullable=True)
    corneres_visitante = Column(Integer, nullable=True)
    amarillas_local = Column(Integer, nullable=True)
    amarillas_visitante = Column(Integer, nullable=True)
    rojas_local = Column(Integer, nullable=True)
    rojas_visitante = Column(Integer, nullable=True)

    # Cuotas 1X2 (Bet365, Pinnacle apertura y Pinnacle cierre)
    cuota_b365_local = Column(Numeric(5, 2), nullable=True)
    cuota_b365_empate = Column(Numeric(5, 2), nullable=True)
    cuota_b365_visitante = Column(Numeric(5, 2), nullable=True)
    cuota_pinnacle_local = Column(Numeric(5, 2), nullable=True)
    cuota_pinnacle_empate = Column(Numeric(5, 2), nullable=True)
    cuota_pinnacle_visitante = Column(Numeric(5, 2), nullable=True)
    cuota_pinnacle_cierre_local = Column(Numeric(5, 2), nullable=True)
    cuota_pinnacle_cierre_empate = Column(Numeric(5, 2), nullable=True)
    cuota_pinnacle_cierre_visitante = Column(Numeric(5, 2), nullable=True)

    # Relación con predicciones
    predicciones = relationship("PrediccionLog", back_populates="partido")


# 3. TABLA DE MODELOS PREDICTIVOS
class ModeloPredictivo(Base):
    __tablename__ = 'modelos_predictivos'

    id_modelo = Column(Integer, primary_key=True, autoincrement=True)
    archivo_pkl = Column(String(100), nullable=False)
    algoritmo_base = Column(String(50), nullable=False)
    accuracy_test = Column(Numeric(5, 2), nullable=False)
    yield_esperado = Column(Numeric(5, 2), nullable=False)
    fecha_entrenamiento = Column(DateTime, default=datetime.utcnow)
    en_produccion = Column(Boolean, default=False)

    # Relación con predicciones
    predicciones = relationship("PrediccionLog", back_populates="modelo")


# 4. TABLA DE PREDICCIONES LOG
class PrediccionLog(Base):
    __tablename__ = 'predicciones_log'

    id_prediccion = Column(Integer, primary_key=True, autoincrement=True)
    id_partido = Column(Integer, ForeignKey('partidos_historico.id_partido'), nullable=False)
    id_modelo = Column(Integer, ForeignKey('modelos_predictivos.id_modelo'), nullable=False)
    probabilidad_ia = Column(Numeric(5, 4), nullable=False)
    cuota_mercado = Column(Numeric(5, 2), nullable=False)
    valor_esperado = Column(Numeric(5, 4), nullable=False)
    porcentaje_kelly = Column(Numeric(5, 4), nullable=False)
    inversion_unidades = Column(Numeric(10, 2), nullable=False)
    tipo_pick = Column(String(20), default='Normal')
    resultado = Column(String(20), default='Pendiente')

    # Relaciones
    partido = relationship("PartidoHistorico", back_populates="predicciones")
    modelo = relationship("ModeloPredictivo", back_populates="predicciones")
    apuestas_usuarios = relationship("ApuestaUsuario", back_populates="prediccion")


# 5. TABLA TRANSACCIONAL DE APUESTAS POR USUARIO
class ApuestaUsuario(Base):
    __tablename__ = 'apuestas_usuario'

    id_apuesta = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    id_prediccion = Column(Integer, ForeignKey('predicciones_log.id_prediccion'), nullable=False)
    unidades_invertidas = Column(Numeric(10, 2), nullable=False)
    cuota_tomada = Column(Numeric(5, 2), nullable=False)
    estado = Column(String(20), default='Pendiente')
    fecha_apuesta = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="apuestas")
    prediccion = relationship("PrediccionLog", back_populates="apuestas_usuarios")