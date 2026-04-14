using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Simulation
{
    public class SimulationOrchestrator : Agent
    {
        private readonly AnimalAgent _animalAgent;
        private readonly ConstructionAgent _constructionAgent;
        private readonly MapAgent _mapAgent;

        public SimulationOrchestrator(AnimalAgent animalAgent, ConstructionAgent constructionAgent, MapAgent mapAgent)
        {
            _animalAgent = animalAgent;
            _constructionAgent = constructionAgent;
            _mapAgent = mapAgent;
        }

        public override async Task ExecuteAsync(Partida partida)
        {
            partida.RegistroEventos.Add($"--- INICIO MES {partida.MesActual} ---");

            // Ejecutar agentes en orden
            await _mapAgent.ExecuteAsync(partida);
            await _animalAgent.ExecuteAsync(partida);
            await _constructionAgent.ExecuteAsync(partida);

            partida.MesActual++;
        }
    }
}