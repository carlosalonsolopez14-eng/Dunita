using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Persistence
{
    public class PersistenceOrchestrator : Agent
    {
        private readonly PersistenceAgent _persistenceAgent;

        public PersistenceOrchestrator(PersistenceAgent persistenceAgent)
        {
            _persistenceAgent = persistenceAgent;
        }

        public override async Task ExecuteAsync(Partida partida)
        {
            // Coordinar persistencia, por ejemplo auto-guardado periódico
            await _persistenceAgent.ExecuteAsync(partida);
        }

        public async Task GuardarPartidaAsync(Partida partida)
        {
            await _persistenceAgent.GuardarPartidaAsync(partida);
        }

        public async Task<Partida> CargarPartidaAsync()
        {
            return await _persistenceAgent.CargarPartidaAsync();
        }

        public async Task<List<Partida>> ListarPartidasAsync()
        {
            return await _persistenceAgent.ListarPartidasAsync();
        }
    }
}