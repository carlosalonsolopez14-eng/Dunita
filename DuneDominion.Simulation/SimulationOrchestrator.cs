using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Simulation
{
    public class SimulationOrchestrator : Agent
    {
        private readonly AnimalAgent _animalAgent = new AnimalAgent();
        private readonly ConstructionAgent _constructionAgent = new ConstructionAgent();
        private readonly MapAgent _mapAgent = new MapAgent();

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