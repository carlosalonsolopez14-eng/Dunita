using Microsoft.EntityFrameworkCore;
using DuneDominion.Shared;

namespace DuneDominion.Persistence
{
    public class DunitaDbContext : DbContext
    {
        public DunitaDbContext(DbContextOptions<DunitaDbContext> options) : base(options) { }

        public DbSet<Partida> Partidas { get; set; }
        public DbSet<Enclave> Enclaves { get; set; }
        public DbSet<Instalacion> Instalaciones { get; set; }
        public DbSet<Criatura> Criaturas { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configurar Partida
            modelBuilder.Entity<Partida>()
                .HasKey(p => p.Id);
            modelBuilder.Entity<Partida>()
                .Property(p => p.AliasJugador)
                .IsRequired();
            modelBuilder.Entity<Partida>()
                .Property(p => p.RegistroEventos)
                .HasConversion(
                    v => string.Join(";", v),
                    v => v.Split(';', StringSplitOptions.RemoveEmptyEntries).ToList()
                );

            // Configurar Enclave
            modelBuilder.Entity<Enclave>()
                .HasKey(e => e.Id);
            modelBuilder.Entity<Enclave>()
                .Property(e => e.Nombre)
                .IsRequired();
            modelBuilder.Entity<Enclave>()
                .HasMany(e => e.Instalaciones)
                .WithOne()
                .OnDelete(DeleteBehavior.Cascade);

            // Configurar Instalacion
            modelBuilder.Entity<Instalacion>()
                .HasKey(i => i.Codigo);
            modelBuilder.Entity<Instalacion>()
                .HasMany(i => i.CriaturasAlojadas)
                .WithOne()
                .OnDelete(DeleteBehavior.Cascade);

            // Configurar Criatura
            modelBuilder.Entity<Criatura>()
                .HasKey(c => c.Id);
            modelBuilder.Entity<Criatura>()
                .Property(c => c.NombreEspecie)
                .IsRequired();
        }
    }
}