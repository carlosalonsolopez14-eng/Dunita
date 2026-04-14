using System;
using System.Diagnostics;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Deployment
{
    public class DeploymentAgent : Agent
    {
        private readonly string _dockerComposePath;
        private Process? _dockerProcess;

        public DeploymentAgent(string dockerComposePath = "docker-compose.yml")
        {
            _dockerComposePath = dockerComposePath;
        }

        public override async Task ExecuteAsync(Partida partida)
        {
            // El agente de despliegue se ejecuta manualmente
            // Este método se puede usar para verificar el estado del contenedor
        }

        /// <summary>
        /// Levanta todos los servicios del proyecto usando Docker Compose
        /// </summary>
        public async Task<bool> StartServicesAsync()
        {
            try
            {
                Console.WriteLine("🚀 Iniciando servicios de Dunita...");

                var processInfo = new ProcessStartInfo
                {
                    FileName = "docker-compose",
                    Arguments = $"-f {_dockerComposePath} up -d",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processInfo))
                {
                    if (process == null)
                        throw new Exception("No se pudo iniciar docker-compose");

                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();
                    
                    _dockerProcess = process;
                    await process.WaitForExitAsync();

                    if (process.ExitCode != 0)
                    {
                        Console.WriteLine($"❌ Error al iniciar servicios:\n{error}");
                        return false;
                    }

                    Console.WriteLine("✅ Servicios iniciados exitosamente");
                    Console.WriteLine($"📊 Salida:\n{output}");
                    return true;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error en DeploymentAgent: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Detiene los servicios del proyecto
        /// </summary>
        public async Task<bool> StopServicesAsync()
        {
            try
            {
                Console.WriteLine("🛑 Deteniendo servicios de Dunita...");

                var processInfo = new ProcessStartInfo
                {
                    FileName = "docker-compose",
                    Arguments = $"-f {_dockerComposePath} down",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processInfo))
                {
                    if (process == null)
                        throw new Exception("No se pudo iniciar docker-compose");

                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();

                    await process.WaitForExitAsync();

                    if (process.ExitCode != 0)
                    {
                        Console.WriteLine($"❌ Error al detener servicios:\n{error}");
                        return false;
                    }

                    Console.WriteLine("✅ Servicios detenidos");
                    return true;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error en DeploymentAgent: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Verifica el estado de los contenedores
        /// </summary>
        public async Task<bool> CheckStatusAsync()
        {
            try
            {
                var processInfo = new ProcessStartInfo
                {
                    FileName = "docker-compose",
                    Arguments = $"-f {_dockerComposePath} ps",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processInfo))
                {
                    if (process == null)
                        throw new Exception("No se pudo iniciar docker-compose");

                    string output = await process.StandardOutput.ReadToEndAsync();
                    await process.WaitForExitAsync();

                    Console.WriteLine("📊 Estado de los contenedores:");
                    Console.WriteLine(output);
                    return process.ExitCode == 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error al verificar estado: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Abre la aplicación en el navegador predeterminado
        /// </summary>
        public void OpenBrowser(string url = "http://localhost:5000")
        {
            try
            {
                Console.WriteLine($"🌐 Abriendo {url} en el navegador...");
                
                if (System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(
                    System.Runtime.InteropServices.OSPlatform.Windows))
                {
                    Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
                }
                else if (System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(
                    System.Runtime.InteropServices.OSPlatform.Linux))
                {
                    Process.Start("xdg-open", url);
                }
                else if (System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(
                    System.Runtime.InteropServices.OSPlatform.OSX))
                {
                    Process.Start("open", url);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"⚠️ No se pudo abrir el navegador: {ex.Message}");
            }
        }
    }
}