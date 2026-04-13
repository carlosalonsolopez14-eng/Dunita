using System;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Persistence
{
    public class PersistenceAgent : Agent
    {
        private readonly DatabasePersistenceService _persistenceService;

        public PersistenceAgent(DatabasePersistenceService persistenceService)
        {
            _persistenceService = persistenceService;
        }

        public override async Task ExecuteAsync(Partida partida)
        {
            // El agente de persistencia no ejecuta automáticamente, se llama manualmente para guardar/cargar
            // Pero podemos implementar lógica de auto-guardado si es necesario
        }

        public async Task GuardarPartidaAsync(Partida partida)
        {
            await _persistenceService.GuardarPartidaAsync(partida);
        }

        public async Task<Partida> CargarPartidaAsync()
        {
            return await _persistenceService.CargarPartidaAsync();
        }

        public async Task<List<Partida>> ListarPartidasAsync()
        {
            return await _persistenceService.ListarPartidasAsync();
        }
    }
}