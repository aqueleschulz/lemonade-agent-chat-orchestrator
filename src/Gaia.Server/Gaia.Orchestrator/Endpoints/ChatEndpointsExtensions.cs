using Gaia.Orchestrator.Services.Interfaces;
using Gaia.Orchestrator.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace Gaia.Orchestrator.Endpoints;

public static class ChatEndpointsExtensions
{
    public static void MapChatEndpoints(this WebApplication app)
    {
        var chatGroup = app.MapGroup("/chat").WithTags("Chat");

        chatGroup.MapPost("/ask", async (UserPromptRequest request, ILemonadeService lemonadeService) =>
        {
            if (string.IsNullOrWhiteSpace(request.Prompt))
            {
                return Results.BadRequest("O prompt não pode estar vazio.");
            }

            var aiResponse = await lemonadeService.GetCompletionAsync(request.Prompt);

            return Results.Ok(new { response = aiResponse });
        })
        .WithName("Chatbot")
        .WithDescription("Envia um prompt para a IA e recebe uma resposta limpa, sem metadados ou informações adicionais.");
    }
}