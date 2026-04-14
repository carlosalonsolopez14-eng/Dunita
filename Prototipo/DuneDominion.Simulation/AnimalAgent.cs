using System;
using System.Linq;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Simulation
{
    public class AnimalAgent : Agent
    {
        private static readonly Random _rnd = new Random();

        public override async Task ExecuteAsync(Partida partida)
        {
            foreach (var enclave in partida.Enclaves)
            {
                await ProcesarCriaturasEnEnclave(enclave, partida);
            }
        }

        private async Task ProcesarCriaturasEnEnclave(Enclave enclave, Partida partida)
        {
            foreach (var instalacion in enclave.Instalaciones)
            {
                foreach (var criatura in instalacion.CriaturasAlojadas)
                {
                    if (criatura.EnLetargo) continue;

                    // 1. Calcular Ingesta
                    double alpha = enclave.Tipo == TipoEnclave.Exhibicion ? 1.0 : 1.5;
                    double ingestaRequerida = criatura.EdadActual < criatura.EdadAdulta
                        ? criatura.ApetitoBase * criatura.EdadActual
                        : criatura.ApetitoBase * Math.Pow(2, criatura.EdadActual - criatura.EdadAdulta) * alpha;

                    double ingestaRecibida = Math.Min(ingestaRequerida, enclave.Suministros);
                    enclave.Suministros -= (int)ingestaRecibida;

                    // 2. Calcular Salud
                    double porcentaje = ingestaRequerida > 0 ? (ingestaRecibida / ingestaRequerida) * 100 : 100;
                    if (porcentaje < 25) criatura.Salud -= 30;
                    else if (porcentaje < 75) criatura.Salud -= 20;
                    else if (porcentaje < 100) criatura.Salud -= 10;
                    else if (criatura.Salud < 100) criatura.Salud += 5;

                    criatura.Salud = Math.Clamp(criatura.Salud, 0, 100);
                    criatura.EdadActual++;
                }
            }
        }
    }
}