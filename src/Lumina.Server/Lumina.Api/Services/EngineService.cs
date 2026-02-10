using System.Net.Http.Json;
using Lumina.Api.DTOs;
using Lumina.Api.Services.Interfaces;

namespace Lumina.Api.Services
{
    public class EngineService : IEngineService
    {
        private readonly HttpClient _httpClient;

        public EngineService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public Task<bool> CheckHealthAsync()
        {
            return Task.FromResult(true);
        }

        public async Task<List<string>> ListFilesAsync()
        {
            var response = await _httpClient.GetAsync("/tools/list-files");
            response.EnsureSuccessStatusCode();

            var responseData = await response.Content.ReadFromJsonAsync<EngineListFilesResponse>();
            
            var files = responseData?.Files ?? new List<string>();

            return files;
        }

        public async Task<string> ReadFileAsync(string filename)
        {
            var response = await _httpClient.GetAsync("/tools/read-file");
            response.EnsureSuccessStatusCode();

            if(response == null)
                throw new Exception($"Resposta nula ao ler arquivo: {filename}");

            var content = await response.Content.ReadAsStringAsync();
            return content;
        }
    }
}