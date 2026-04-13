using Microsoft.EntityFrameworkCore;
using DuneDominion.Persistence;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddSession();

// Configurar Entity Framework Core con PostgreSQL
builder.Services.AddDbContext<DunitaDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Registrar servicios de persistencia
builder.Services.AddScoped<DatabasePersistenceService>();
builder.Services.AddScoped<PersistenceAgent>();
builder.Services.AddScoped<PersistenceOrchestrator>();

// Registrar orquestradores
builder.Services.AddScoped<MainOrchestrator>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseDefaultFiles();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.UseSession();

// Ejecutar migraciones automáticamente
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<DunitaDbContext>();
    await dbContext.Database.MigrateAsync();
}

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
