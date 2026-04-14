using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;
using DuneDominion.Shared;

namespace DuneDominion.Persistence
{
    public class DatabasePersistenceService
    {
        private readonly DunitaDbContext _context;

        public DatabasePersistenceService(DunitaDbContext context)
        {
            _context = context;
        }

        public async Task GuardarPartidaAsync(Partida partida)
        {
            try
            {
                // Verificar si ya existe
                var existing = await _context.Partidas.FindAsync(partida.Id);
                if (existing != null)
                {
                    _context.Partidas.Remove(existing);
                }

                // Agregar la nueva partida con todas las relaciones
                await _context.Partidas.AddAsync(partida);
                await _context.SaveChangesAsync();

                partida.RegistroEventos.Add($"[{DateTime.Now}] Partida guardada en base de datos con éxito.");
            }
            catch (Exception ex)
            {
                throw new Exception($"Error de persistencia al guardar: {ex.Message}");
            }
        }

        public async Task<Partida> CargarPartidaAsync()
        {
            try
            {
                var partida = await _context.Partidas
                    .Include(p => p.Enclaves)
                        .ThenInclude(e => e.Instalaciones)
                            .ThenInclude(i => i.CriaturasAlojadas)
                    .FirstOrDefaultAsync();

                if (partida == null)
                    throw new Exception("No se encontró ninguna partida guardada.");

                return partida;
            }
            catch (Exception ex)
            {
                throw new Exception($"Error al cargar partida: {ex.Message}");
            }
        }

        public async Task<List<Partida>> ListarPartidasAsync()
        {
            return await _context.Partidas
                .Select(p => new Partida { Id = p.Id, AliasJugador = p.AliasJugador, MesActual = p.MesActual })
                .ToListAsync();
        }
    }
}