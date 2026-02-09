using System.Net.Http.Json;
using Lumina.Api.DTOs;
using Lumina.Api.Services.Interfaces;

namespace Lumina.Api.Services
{
    public class LemonadeService : ILemonadeService
    {
        private readonly HttpClient _httpClient;
        public LemonadeService (HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<string> GetCompletionAsync(string prompt)
        {
            var requestPayload = new ChatCompletionRequest(
                        model: "Gemma-3-4b-it-GGUF",
                        userPrompt: prompt
                    );

            var response = await _httpClient.PostAsJsonAsync("/api/v1/chat/completions", requestPayload);

            response.EnsureSuccessStatusCode();

            var responseData = await response.Content.ReadFromJsonAsync<ChatCompletionResponse>();
            return responseData?.Choices?.FirstOrDefault()?.Message?.Content ?? "Erro: Sem resposta da IA.";
        }
    }
}