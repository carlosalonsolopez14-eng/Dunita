using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace DuneDominion.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Partidas",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    AliasJugador = table.Column<string>(type: "text", nullable: false),
                    Solaris = table.Column<int>(type: "integer", nullable: false),
                    MesActual = table.Column<int>(type: "integer", nullable: false),
                    RegistroEventos = table.Column<string>(type: "text", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Partidas", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Enclaves",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Nombre = table.Column<string>(type: "text", nullable: false),
                    Tipo = table.Column<int>(type: "integer", nullable: false),
                    Hectareas = table.Column<int>(type: "integer", nullable: false),
                    Suministros = table.Column<int>(type: "integer", nullable: false),
                    VisitantesMensuales = table.Column<int>(type: "integer", nullable: false),
                    NivelPublico = table.Column<int>(type: "integer", nullable: false),
                    PartidaId = table.Column<Guid>(type: "uuid", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Enclaves", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Enclaves_Partidas_PartidaId",
                        column: x => x.PartidaId,
                        principalTable: "Partidas",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateTable(
                name: "Instalaciones",
                columns: table => new
                {
                    Codigo = table.Column<string>(type: "text", nullable: false),
                    Coste = table.Column<int>(type: "integer", nullable: false),
                    TipoRecinto = table.Column<int>(type: "integer", nullable: false),
                    MedioSoportado = table.Column<int>(type: "integer", nullable: false),
                    AlimentacionSoportada = table.Column<int>(type: "integer", nullable: false),
                    HectareasOcupadas = table.Column<int>(type: "integer", nullable: false),
                    CapacidadCriaturas = table.Column<int>(type: "integer", nullable: false),
                    EnclaveId = table.Column<Guid>(type: "uuid", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Instalaciones", x => x.Codigo);
                    table.ForeignKey(
                        name: "FK_Instalaciones_Enclaves_EnclaveId",
                        column: x => x.EnclaveId,
                        principalTable: "Enclaves",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Criaturas",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    NombreEspecie = table.Column<string>(type: "text", nullable: false),
                    MedioRequerido = table.Column<int>(type: "integer", nullable: false),
                    PatronAlimentacion = table.Column<int>(type: "integer", nullable: false),
                    EdadActual = table.Column<int>(type: "integer", nullable: false),
                    EdadAdulta = table.Column<int>(type: "integer", nullable: false),
                    ApetitoBase = table.Column<int>(type: "integer", nullable: false),
                    Salud = table.Column<int>(type: "integer", nullable: false),
                    VecesFavorita = table.Column<int>(type: "integer", nullable: false),
                    CosteCompra = table.Column<int>(type: "integer", nullable: false),
                    InstalacionCodigo = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Criaturas", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Criaturas_Instalaciones_InstalacionCodigo",
                        column: x => x.InstalacionCodigo,
                        principalTable: "Instalaciones",
                        principalColumn: "Codigo",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Criaturas_InstalacionCodigo",
                table: "Criaturas",
                column: "InstalacionCodigo");

            migrationBuilder.CreateIndex(
                name: "IX_Enclaves_PartidaId",
                table: "Enclaves",
                column: "PartidaId");

            migrationBuilder.CreateIndex(
                name: "IX_Instalaciones_EnclaveId",
                table: "Instalaciones",
                column: "EnclaveId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Criaturas");

            migrationBuilder.DropTable(
                name: "Instalaciones");

            migrationBuilder.DropTable(
                name: "Enclaves");

            migrationBuilder.DropTable(
                name: "Partidas");
        }
    }
}
