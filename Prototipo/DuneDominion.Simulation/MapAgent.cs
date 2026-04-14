using System;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Simulation
{
    public class MapAgent : Agent
    {
        public override async Task ExecuteAsync(Partida partida)
        {
            // Por ahora, el agente de mapas gestiona la inicialización y mantenimiento de enclaves
            // En futuras versiones, podría manejar expansión territorial, clima, etc.
            foreach (var enclave in partida.Enclaves)
            {
                // Mantener enclaves activos
                // Ejemplo: verificar capacidad de suministros
                if (enclave.Suministros > enclave.CapacidadSuministros)
                {
                    enclave.Suministros = enclave.CapacidadSuministros;
                }
            }
        }
    }
}