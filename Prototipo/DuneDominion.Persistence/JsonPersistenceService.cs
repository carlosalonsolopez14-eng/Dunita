using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Persistence
{
    public class JsonPersistenceService
    {
        private readonly string _filePath = "estado_partida.json";

        public async Task GuardarPartidaAsync(Partida partida)
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(partida, options);
                await File.WriteAllTextAsync(_filePath, json);
                partida.RegistroEventos.Add($"[{DateTime.Now}] Partida guardada con éxito.");
            }
            catch (Exception ex)
            {
                throw new Exception($"Error de persistencia al guardar: {ex.Message}");
            }
        }

        public async Task<Partida> CargarPartidaAsync()
        {
            if (!File.Exists(_filePath))
                throw new FileNotFoundException("No se encontró ninguna partida guardada.");

            try
            {
                string json = await File.ReadAllTextAsync(_filePath);
                return JsonSerializer.Deserialize<Partida>(json);
            }
            catch (Exception ex)
            {
                throw new Exception($"Estado corrupto o error de lectura: {ex.Message}");
            }
        }
    }
}
