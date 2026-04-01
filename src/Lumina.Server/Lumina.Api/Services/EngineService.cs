using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
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
            return responseData?.Files ?? new List<string>();
        }

        public async Task<string> ReadFileAsync(string filename)
        {
            var response = await _httpClient.PostAsync(
                $"/tools/read-file?filename={Uri.EscapeDataString(filename)}", null);

            response.EnsureSuccessStatusCode();

            var content = await response.Content.ReadAsStringAsync();
            return content;
        }

        /// <summary>
        /// Performs a semantic search on the chunks indexed in the Engine's ChromaDB.
        /// Returns the most relevant snippets formatted as text for prompt injection.
        /// </summary>
        public async Task<string> SearchContentAsync(string query, string? filename = null)
        {
            var requestBody = new
            {
                query,
                filename,
                top_k = 4
            };

            var json    = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("/tools/search", content);
            response.EnsureSuccessStatusCode();

            var results = await response.Content.ReadFromJsonAsync<List<SearchResultItem>>();

            if (results == null || results.Count == 0)
                return string.Empty;

            var sb = new StringBuilder();
            foreach (var (item, index) in results.Select((r, i) => (r, i + 1)))
            {
                sb.AppendLine($"--- Trecho {index} (fonte: {item.Source}, relevância: {1 - item.Distance:P0}) ---");
                sb.AppendLine(item.Content);
                sb.AppendLine();
            }

            return sb.ToString();
        }

        private record SearchResultItem(
            string Source,
            int ChunkIndex,
            string Content,
            double Distance);
    }
}
