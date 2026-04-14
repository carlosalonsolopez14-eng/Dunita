using System;
using System.Linq;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Simulation
{
    public class ConstructionAgent : Agent
    {
        private static readonly Random _rnd = new Random();

        public override async Task ExecuteAsync(Partida partida)
        {
            foreach (var enclave in partida.Enclaves)
            {
                await ProcesarMonetizacionYVisitantes(enclave, partida);
            }
        }

        private async Task ProcesarMonetizacionYVisitantes(Enclave enclave, Partida partida)
        {
            double donacionesTotales = 0;

            foreach (var instalacion in enclave.Instalaciones)
            {
                foreach (var criatura in instalacion.CriaturasAlojadas)
                {
                    if (criatura.EnLetargo) continue;

                    // 3. Monetización en Exhibición
                    if (enclave.Tipo == TipoEnclave.Exhibicion && enclave.VisitantesMensuales > 0)
                    {
                        double sigma = enclave.NivelPublico == NivelAdquisitivo.Bajo ? 1 :
                                       enclave.NivelPublico == NivelAdquisitivo.Medio ? 15 : 30;

                        // Sistema aleatorio de visitantes y coste: la más cara atrae más donaciones
                        double rng = 0.5 + _rnd.NextDouble();
                        double extraPorCoste = criatura.CosteCompra > 500 ? (criatura.CosteCompra / 500.0) : 1.0;

                        double donacion = 10 * (criatura.Salud / 100.0) * ((double)criatura.EdadActual / criatura.EdadAdulta) * sigma * extraPorCoste * rng;
                        donacionesTotales += donacion;
                    }
                }
            }

            partida.Solaris += (int)donacionesTotales;

            // 4. Calcular Visitantes
            if (enclave.Tipo == TipoEnclave.Exhibicion && enclave.Instalaciones.Any())
            {
                double hectareasInst = enclave.Instalaciones.Sum(i => i.HectareasOcupadas);
                double saludMedia = enclave.Instalaciones.SelectMany(i => i.CriaturasAlojadas)
                                        .Select(c => c.Salud).DefaultIfEmpty(0).Average();

                double factor = (hectareasInst / enclave.Hectareas) * (saludMedia / 100.0);
                double visitantesLlegan = enclave.VisitantesMensuales * factor;
                double visitantesAbandonan = enclave.VisitantesMensuales - (enclave.VisitantesMensuales * factor);

                enclave.VisitantesMensuales += (int)(visitantesLlegan - visitantesAbandonan);
            }
        }
    }
}