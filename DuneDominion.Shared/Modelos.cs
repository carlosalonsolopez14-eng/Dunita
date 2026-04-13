using System;
using System.Collections.Generic;
using System.Linq;

namespace DuneDominion.Shared
{
    public enum Medio { Desierto, Aereo, Subterraneo }
    public enum Alimentacion { Recolector, Depredador }
    public enum NivelAdquisitivo { Alto, Medio, Bajo }
    public enum TipoEnclave { Aclimatacion, Exhibicion }

    public class Partida
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string AliasJugador { get; set; }
        public int Solaris { get; set; }
        public int MesActual { get; set; } = 1;
        public List<Enclave> Enclaves { get; set; } = new List<Enclave>();
        public List<string> RegistroEventos { get; set; } = new List<string>();
    }

    public class Enclave
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; }
        public TipoEnclave Tipo { get; set; }
        public int Hectareas { get; set; }
        public int Suministros { get; set; }
        public int VisitantesMensuales { get; set; }
        public NivelAdquisitivo NivelPublico { get; set; }
        public List<Instalacion> Instalaciones { get; set; } = new List<Instalacion>();
        public int CapacidadSuministros => Hectareas * 3;
    }

    public class Instalacion
    {
        public string Codigo { get; set; }
        public int Coste { get; set; }
        public TipoEnclave TipoRecinto { get; set; }
        public Medio MedioSoportado { get; set; }
        public Alimentacion AlimentacionSoportada { get; set; }
        public int HectareasOcupadas { get; set; }
        public int CapacidadCriaturas { get; set; }
        public List<Criatura> CriaturasAlojadas { get; set; } = new List<Criatura>();
    }

    public class Criatura
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string NombreEspecie { get; set; }
        public Medio MedioRequerido { get; set; }
        public Alimentacion PatronAlimentacion { get; set; }
        public int EdadActual { get; set; }
        public int EdadAdulta { get; set; }
        public int ApetitoBase { get; set; }
        public int Salud { get; set; } = 100;
        public int VecesFavorita { get; set; }
        public int CosteCompra { get; set; }
        public bool EnLetargo => Salud <= 0;
    }

    public abstract class Agent
    {
        public abstract Task ExecuteAsync(Partida partida);
    }
}
