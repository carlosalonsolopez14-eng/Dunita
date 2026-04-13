FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY ["DuneDominion.Shared/DuneDominion.Shared.csproj", "DuneDominion.Shared/"]
COPY ["DuneDominion.Simulation/DuneDominion.Simulation.csproj", "DuneDominion.Simulation/"]
COPY ["DuneDominion.Persistence/DuneDominion.Persistence.csproj", "DuneDominion.Persistence/"]
COPY ["DuneDominion.Client/DuneDominion.Client.csproj", "DuneDominion.Client/"]

RUN dotnet restore "DuneDominion.Client/DuneDominion.Client.csproj"

COPY . .
WORKDIR "/src/DuneDominion.Client"
RUN dotnet build "DuneDominion.Client.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "DuneDominion.Client.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=publish /app/publish .

EXPOSE 5000
ENV ASPNETCORE_URLS=http://+:5000
ENV ASPNETCORE_ENVIRONMENT=Production

ENTRYPOINT ["dotnet", "DuneDominion.Client.dll"]