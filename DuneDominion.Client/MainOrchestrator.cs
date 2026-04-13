using System.Threading.Tasks;
using DuneDominion.Shared;
using DuneDominion.Simulation;
using DuneDominion.Persistence;

namespace DuneDominion.Client
{
    public class MainOrchestrator : Agent
    {
        private readonly SimulationOrchestrator _simulationOrchestrator = new SimulationOrchestrator();
        private readonly PersistenceOrchestrator _persistenceOrchestrator = new PersistenceOrchestrator();

        public override async Task ExecuteAsync(Partida partida)
        {
            // El orquestador principal coordina la simulación y persistencia
            await _simulationOrchestrator.ExecuteAsync(partida);
            // Persistencia se maneja manualmente en el cliente
        }

        public async Task EjecutarRondaMensual(Partida partida)
        {
            await _simulationOrchestrator.ExecuteAsync(partida);
        }

        public async Task GuardarPartidaAsync(Partida partida)
        {
            await _persistenceOrchestrator.GuardarPartidaAsync(partida);
        }

        public async Task<Partida> CargarPartidaAsync()
        {
            return await _persistenceOrchestrator.CargarPartidaAsync();
        }
    }
}