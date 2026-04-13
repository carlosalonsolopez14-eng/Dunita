using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace DuneDominion.Client.Controllers
{
    [ApiController]
    [Route("api")]
    public class DeploymentApiController : ControllerBase
    {
        private readonly ILogger<DeploymentApiController> _logger;

        public DeploymentApiController(ILogger<DeploymentApiController> logger)
        {
            _logger = logger;
        }

        [HttpPost("deploy")]
        public async Task<IActionResult> Deploy()
        {
            try
            {
                _logger.LogInformation("Iniciando despliegue de servicios Docker...");

                // Ejecutar docker-compose up -d desde el directorio raíz del proyecto
                var projectRoot = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..");
                var composePath = Path.Combine(projectRoot, "docker-compose.yml");

                if (!System.IO.File.Exists(composePath))
                {
                    _logger.LogError($"docker-compose.yml no encontrado en {composePath}");
                    return BadRequest(new { error = "Configuración de Docker no encontrada" });
                }

                var processInfo = new ProcessStartInfo
                {
                    FileName = "docker-compose",
                    Arguments = $"-f {composePath} up -d",
                    WorkingDirectory = projectRoot,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processInfo))
                {
                    if (process == null)
                    {
                        _logger.LogError("No se pudo iniciar docker-compose");
                        return StatusCode(500, new { error = "No se pudo iniciar docker-compose" });
                    }

                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();

                    await process.WaitForExitAsync();

                    if (process.ExitCode != 0)
                    {
                        _logger.LogError($"Error en docker-compose: {error}");
                        return StatusCode(500, new { error = error });
                    }

                    _logger.LogInformation("Servicios levantados exitosamente");
                    return Ok(new { message = "Servicios levantados correctamente", output = output });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error al desplegar servicios");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpGet("deploy/status")]
        public async Task<IActionResult> Status()
        {
            try
            {
                var projectRoot = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..");
                var composePath = Path.Combine(projectRoot, "docker-compose.yml");

                var processInfo = new ProcessStartInfo
                {
                    FileName = "docker-compose",
                    Arguments = $"-f {composePath} ps",
                    WorkingDirectory = projectRoot,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processInfo))
                {
                    if (process == null)
                        return StatusCode(500, new { error = "No se pudo verificar estado" });

                    string output = await process.StandardOutput.ReadToEndAsync();
                    await process.WaitForExitAsync();

                    return Ok(new { status = output });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}