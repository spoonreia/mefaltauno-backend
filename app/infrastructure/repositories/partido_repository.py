"""Repositorio de Partidos (Port/Interface)"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.models.partido import Partido
from app.domain.enums.estado import TipoFutbol


class PartidoRepositoryInterface(ABC):
    """Interface del repositorio de partidos"""

    @abstractmethod
    def crear(self, partido: Partido) -> Partido:
        pass

    @abstractmethod
    def obtener_por_id(self, partido_id: int) -> Optional[Partido]:
        pass

    @abstractmethod
    def actualizar(self, partido: Partido) -> Partido:
        pass

    @abstractmethod
    def eliminar(self, partido_id: int) -> bool:
        pass

    @abstractmethod
    def buscar(
        self,
        titulo: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        tipo_futbol: Optional[TipoFutbol] = None,
        edad_minima: Optional[int] = None,
    ) -> List[Partido]:
        pass


class PartidoRepository(PartidoRepositoryInterface):
    """Implementación en memoria del repositorio de partidos"""

    def __init__(self, db_storage):
        self.db = db_storage

    def crear(self, partido: Partido) -> Partido:
        """Crea un nuevo partido"""
        nuevo_id = max([p["id"] for p in self.db.partidos_db], default=0) + 1
        
        partido_dict = {
            "id": nuevo_id,
            "titulo": partido.titulo,
            "dinero_por_persona": partido.dinero_por_persona,
            "descripcion": partido.descripcion,
            "fecha_hora": partido.fecha_hora,
            "latitud": partido.latitud,
            "longitud": partido.longitud,
            "ubicacion_texto": partido.ubicacion_texto,
            "capacidad_maxima": partido.capacidad_maxima,
            "organizador_id": partido.organizador_id,
            "tipo_partido": partido.tipo_partido,
            "tipo_futbol": partido.tipo_futbol,
            "edad_minima": partido.edad_minima,
            "estado": partido.estado,
            "contrasena": partido.contrasena,
        }
        
        self.db.partidos_db.append(partido_dict)
        partido.id = nuevo_id
        return partido

    def obtener_por_id(self, partido_id: int) -> Optional[Partido]:
        """Obtiene un partido por ID"""
        partido_dict = next(
            (p for p in self.db.partidos_db if p["id"] == partido_id), None
        )
        if not partido_dict:
            return None
        return Partido(**partido_dict)

    def actualizar(self, partido: Partido) -> Partido:
        """Actualiza un partido existente"""
        for idx, p in enumerate(self.db.partidos_db):
            if p["id"] == partido.id:
                self.db.partidos_db[idx] = partido.dict()
                return partido
        return partido

    def eliminar(self, partido_id: int) -> bool:
        """Elimina un partido"""
        partido_dict = next(
            (p for p in self.db.partidos_db if p["id"] == partido_id), None
        )
        if partido_dict:
            self.db.partidos_db.remove(partido_dict)
            return True
        return False

    def buscar(
        self,
        titulo: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        tipo_futbol: Optional[TipoFutbol] = None,
        edad_minima: Optional[int] = None,
    ) -> List[Partido]:
        """Busca partidos según criterios"""
        resultados = []
        
        for partido_dict in self.db.partidos_db:
            if titulo and titulo.lower() not in partido_dict["titulo"].lower():
                continue
            if tipo_futbol and partido_dict["tipo_futbol"] != tipo_futbol:
                continue
            if edad_minima and partido_dict["edad_minima"] > edad_minima:
                continue
            if fecha_desde and partido_dict["fecha_hora"] < fecha_desde:
                continue
            if fecha_hasta and partido_dict["fecha_hora"] > fecha_hasta:
                continue
            
            resultados.append(Partido(**partido_dict))
        
        return resultados