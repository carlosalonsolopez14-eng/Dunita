using DuneDominion.Client;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddSession();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.UseSession();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();using System;
using System.Linq;
using System.Threading.Tasks;
using DuneDominion.Shared;
using DuneDominion.Persistence;
using DuneDominion.Simulation;

namespace DuneDominion.Client
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var orquestador = new MainOrchestrator();
            Partida partidaActual = null;

            Console.WriteLine("=== DUNE: ARRAKIS DOMINION DISTRIBUTED ===");
            Console.WriteLine("1. Nueva Partida (Escenario Arrakeen)");
            Console.WriteLine("2. Cargar Partida");
            
            string opcionInicial = Console.ReadLine();
            if (opcionInicial == "2")
            {
                try { partidaActual = await orquestador.CargarPartidaAsync(); }
                catch (Exception e) { Console.WriteLine(e.Message); return; }
            }
            else
            {
                partidaActual = InicializarEscenarioArrakeen();
            }

            while (true)
            {
                try { Console.Clear(); } catch { }
                Console.WriteLine($"--- CENTRO DE MANDO | Mes: {partidaActual.MesActual} | Solaris: {partidaActual.Solaris} ---");
                Console.WriteLine("1. Ver Estado de Enclaves y Criaturas");
                Console.WriteLine("2. Ejecutar Ronda Mensual");
                Console.WriteLine("3. Guardar Partida");
                Console.WriteLine("4. Tienda");
                Console.WriteLine("5. Salir");
                Console.Write("Seleccione orden: ");
                
                string opcion = Console.ReadLine();

                switch (opcion)
                {
                    case "1":
                        MostrarEstado(partidaActual);
                        break;
                    case "2":
                        await orquestador.EjecutarRondaMensual(partidaActual);
                        Console.WriteLine("Simulación completada. Presione enter...");
                        Console.ReadLine();
                        break;
                    case "3":
                        await orquestador.GuardarPartidaAsync(partidaActual);
                        Console.WriteLine("Guardado exitoso. Presione enter...");
                        Console.ReadLine();
                        break;
                    case "4":
                        AbrirTienda(partidaActual);
                        break;
                    case "5":
                        await orquestador.GuardarPartidaAsync(partidaActual);
                        return;
                }
            }
        }

        static void AbrirTienda(Partida partida)
        {
            while (true)
            {
                try { Console.Clear(); } catch { }
                Console.WriteLine($"--- TIENDA | Solaris: {partida.Solaris} ---");
                Console.WriteLine("1. Comprar Suministros (1000 Solaris = 5000 unidades)");
                Console.WriteLine("2. Comprar Criatura");
                Console.WriteLine("3. Volver al Centro de Mando");
                Console.Write("Selecciona: ");
                string opt = Console.ReadLine();

                if (opt == "3") return;
                
                if (opt == "1")
                {
                    Console.WriteLine("¿A qué Enclave quieres enviar los suministros?");
                    for (int i=0; i<partida.Enclaves.Count; i++) Console.WriteLine($"{i}. {partida.Enclaves[i].Nombre} ({partida.Enclaves[i].Suministros}/{partida.Enclaves[i].CapacidadSuministros})");
                    if (int.TryParse(Console.ReadLine(), out int idx) && idx >= 0 && idx < partida.Enclaves.Count)
                    {
                        if (partida.Solaris >= 1000)
                        {
                            partida.Solaris -= 1000;
                            partida.Enclaves[idx].Suministros += 5000;
                            Console.WriteLine("Compra realizada. Suministros añadidos.");
                        }
                        else Console.WriteLine("Solaris insuficientes.");
                    }
                    Console.ReadLine();
                }
                else if (opt == "2")
                {
                    Console.WriteLine("Catálogo de Criaturas:");
                    Console.WriteLine("  A) Gusano de Arena (50.000 Solaris)");
                    Console.WriteLine("  B) Tiburón de Arena (15.000 Solaris)");
                    Console.WriteLine("  C) Lince del Desierto (5.000 Solaris)");
                    string cat = Console.ReadLine()?.ToUpper();
                    
                    int coste = 0;
                    Criatura nueva = null;
                    if (cat == "A") { coste = 50000; nueva = new Criatura { NombreEspecie = "Gusano de Arena", MedioRequerido = Medio.Subterraneo, PatronAlimentacion = Alimentacion.Depredador, EdadActual = 0, EdadAdulta = 100, ApetitoBase = 500, CosteCompra = 50000 }; }
                    else if (cat == "B") { coste = 15000; nueva = new Criatura { NombreEspecie = "Tiburón de Arena", MedioRequerido = Medio.Subterraneo, PatronAlimentacion = Alimentacion.Depredador, EdadActual = 0, EdadAdulta = 20, ApetitoBase = 50, CosteCompra = 15000 }; }
                    else if (cat == "C") { coste = 5000; nueva = new Criatura { NombreEspecie = "Lince del Desierto", MedioRequerido = Medio.Desierto, PatronAlimentacion = Alimentacion.Depredador, EdadActual = 0, EdadAdulta = 5, ApetitoBase = 10, CosteCompra = 5000 }; }

                    if (nueva != null)
                    {
                        if (partida.Solaris >= coste)
                        {
                            var instalaciones = partida.Enclaves.SelectMany(e => e.Instalaciones).ToList();
                            if (instalaciones.Any())
                            {
                                instalaciones.First().CriaturasAlojadas.Add(nueva);
                                partida.Solaris -= coste;
                                Console.WriteLine($"Criatura {nueva.NombreEspecie} comprada y alojada automáticamente en la primera instalación.");
                            }
                            else Console.WriteLine("No hay instalaciones disponibles en ningún enclave.");
                        }
                        else Console.WriteLine("Solaris insuficientes.");
                    }
                    Console.ReadLine();
                }
            }
        }

        static void MostrarEstado(Partida partida)
        {
            try { Console.Clear(); } catch { }
            foreach (var enclave in partida.Enclaves)
            {
                Console.WriteLine($"\nEnclave: {enclave.Nombre} ({enclave.Tipo}) - Suministros: {enclave.Suministros}/{enclave.CapacidadSuministros}");
                var criaturas = enclave.Instalaciones.SelectMany(i => i.CriaturasAlojadas).OrderByDescending(c => c.Salud);
                
                foreach (var c in criaturas)
                {
                    string estado = c.EnLetargo ? "[LETARGO]" : "[ACTIVA]";
                    Console.WriteLine($"  -> {c.NombreEspecie} | Salud: {c.Salud}% | Edad: {c.EdadActual} {estado}");
                }
            }
            Console.WriteLine("\nPresione enter para volver...");
            Console.ReadLine();
        }

        static Partida InicializarEscenarioArrakeen()
        {
            var partida = new Partida { AliasJugador = "Casa Menor", Solaris = 100000 };
            
            var aclimatacion = new Enclave { Nombre = "Cuenca Experimental", Tipo = TipoEnclave.Aclimatacion, Hectareas = 5000, Suministros = 20000 };
            var exhibicion = new Enclave { Nombre = "Arrakeen", Tipo = TipoEnclave.Exhibicion, Hectareas = 7700, Suministros = 10000, NivelPublico = NivelAdquisitivo.Alto };

            // Añadir una criatura inicial de prueba
            var instalacionPrueba = new Instalacion { Codigo = "EDR02", CapacidadCriaturas = 10, HectareasOcupadas = 200 };
            instalacionPrueba.CriaturasAlojadas.Add(new Criatura { NombreEspecie = "Muad'Dib", MedioRequerido = Medio.Desierto, PatronAlimentacion = Alimentacion.Recolector, EdadActual = 2, EdadAdulta = 12, ApetitoBase = 2, CosteCompra = 500 });
            aclimatacion.Instalaciones.Add(instalacionPrueba);

            partida.Enclaves.Add(aclimatacion);
            partida.Enclaves.Add(exhibicion);

            return partida;
        }
    }
}
