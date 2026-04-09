using System;
using System.Linq;
using DuneDominion.Shared;

namespace DuneDominion.Simulation
{
    public class SimulationEngine
    {
        private static readonly Random _rnd = new Random();

        public void EjecutarRondaMensual(Partida partida)
        {
            partida.RegistroEventos.Add($"--- INICIO MES {partida.MesActual} ---");

            foreach (var enclave in partida.Enclaves)
            {
                ProcesarEnclave(enclave, partida);
            }

            partida.MesActual++;
        }

        private void ProcesarEnclave(Enclave enclave, Partida partida)
        {
            double donacionesTotales = 0;

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
