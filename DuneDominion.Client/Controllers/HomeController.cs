using Microsoft.AspNetCore.Mvc;
using DuneDominion.Shared;
using System.Text;

namespace DuneDominion.Client.Controllers
{
    public class HomeController : Controller
    {
        private readonly MainOrchestrator _orquestador = new MainOrchestrator();

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> NuevaPartida()
        {
            var partida = InicializarEscenarioArrakeen();
            HttpContext.Session.SetString("Partida", System.Text.Json.JsonSerializer.Serialize(partida));
            return RedirectToAction("Juego");
        }

        [HttpPost]
        public async Task<IActionResult> CargarPartida()
        {
            try
            {
                var partida = await _orquestador.CargarPartidaAsync();
                HttpContext.Session.SetString("Partida", System.Text.Json.JsonSerializer.Serialize(partida));
                return RedirectToAction("Juego");
            }
            catch (Exception ex)
            {
                ViewBag.Error = ex.Message;
                return View("Index");
            }
        }

        public IActionResult Juego()
        {
            var partidaJson = HttpContext.Session.GetString("Partida");
            if (string.IsNullOrEmpty(partidaJson))
                return RedirectToAction("Index");

            var partida = System.Text.Json.JsonSerializer.Deserialize<Partida>(partidaJson);
            return View(partida);
        }

        [HttpPost]
        public async Task<IActionResult> VerEstado()
        {
            var partidaJson = HttpContext.Session.GetString("Partida");
            var partida = System.Text.Json.JsonSerializer.Deserialize<Partida>(partidaJson);
            return View("Estado", partida);
        }

        [HttpPost]
        public async Task<IActionResult> EjecutarRonda()
        {
            var partidaJson = HttpContext.Session.GetString("Partida");
            var partida = System.Text.Json.JsonSerializer.Deserialize<Partida>(partidaJson);

            await _orquestador.EjecutarRondaMensual(partida);

            HttpContext.Session.SetString("Partida", System.Text.Json.JsonSerializer.Serialize(partida));
            return RedirectToAction("Juego");
        }

        [HttpPost]
        public async Task<IActionResult> GuardarPartida()
        {
            var partidaJson = HttpContext.Session.GetString("Partida");
            var partida = System.Text.Json.JsonSerializer.Deserialize<Partida>(partidaJson);

            await _orquestador.GuardarPartidaAsync(partida);

            ViewBag.Message = "Partida guardada exitosamente.";
            return View("Juego", partida);
        }

        private Partida InicializarEscenarioArrakeen()
        {
            var partida = new Partida
            {
                AliasJugador = "Jugador",
                Solaris = 100000,
                MesActual = 1,
                Enclaves = new List<Enclave>
                {
                    new Enclave
                    {
                        Nombre = "Cuenca Experimental",
                        Tipo = TipoEnclave.Aclimatacion,
                        Hectareas = 50,
                        Suministros = 20000,
                        VisitantesMensuales = 0,
                        NivelPublico = NivelAdquisitivo.Medio,
                        Instalaciones = new List<Instalacion>
                        {
                            new Instalacion
                            {
                                Codigo = "JAULA_BASIC",
                                Coste = 5000,
                                TipoRecinto = TipoEnclave.Aclimatacion,
                                MedioSoportado = Medio.Desierto,
                                AlimentacionSoportada = Alimentacion.Recolector,
                                HectareasOcupadas = 10,
                                CapacidadCriaturas = 5,
                                CriaturasAlojadas = new List<Criatura>
                                {
                                    new Criatura
                                    {
                                        NombreEspecie = "Muad'Dib",
                                        MedioRequerido = Medio.Desierto,
                                        PatronAlimentacion = Alimentacion.Recolector,
                                        EdadActual = 2,
                                        EdadAdulta = 12,
                                        ApetitoBase = 10,
                                        Salud = 100,
                                        CosteCompra = 10000
                                    }
                                }
                            }
                        }
                    },
                    new Enclave
                    {
                        Nombre = "Arrakeen",
                        Tipo = TipoEnclave.Exhibicion,
                        Hectareas = 100,
                        Suministros = 10000,
                        VisitantesMensuales = 5000,
                        NivelPublico = NivelAdquisitivo.Alto,
                        Instalaciones = new List<Instalacion>()
                    }
                }
            };
            return partida;
        }
    }
}