using Lumina.Api.Services;
using Lumina.Api.Services.Interfaces;
using Lumina.Api.Endpoints;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

builder.Services.AddHttpClient<ILemonadeService, LemonadeService>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["LemonadeService:BaseUrl"] ?? "http://localhost:8000");
});

var app = builder.Build();

app.MapChatEndpoints();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/openapi/v1.json", "Gaia Orchestrator v1");
    });
}

app.UseHttpsRedirection();

app.Run();