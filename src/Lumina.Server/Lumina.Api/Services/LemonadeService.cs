using System.Net.Http.Json;
using System.Text.Json;
using Lumina.Api.DTOs;
using Lumina.Api.Services.Interfaces;

namespace Lumina.Api.Services
{
    public class LemonadeService : ILemonadeService
    {
        private readonly HttpClient _httpClient;
        private readonly IEngineService _engineService;

        private readonly string _modelName;
        private readonly int _maxToolCallDepth;

        public LemonadeService(
            HttpClient httpClient,
            IEngineService engineService,
            IConfiguration configuration)
        {
            _httpClient = httpClient;
            _engineService = engineService;

            _modelName = configuration["LemonadeSettings:ModelName"]
                ?? throw new InvalidOperationException("LemonadeSettings:ModelName não está configurado em appsettings.json.");

            _maxToolCallDepth = configuration.GetValue<int>("LemonadeSettings:MaxToolCallDepth", 5);
        }

        public async Task<string> GetCompletionAsync(string prompt, int recursionDepth = 0)
        {
            if (recursionDepth >= _maxToolCallDepth)
                return "Erro: Limite máximo de chamadas de ferramenta atingido para evitar loops infinitos.";

            var tools = recursionDepth == 0 ? GetAvailableTools() : new List<ToolRequest>();

            var requestPayload = new ChatCompletionRequest(
                model: _modelName,
                tools: tools,
                userPrompt: prompt
            );

            var response = await _httpClient.PostAsJsonAsync("/api/v1/chat/completions", requestPayload);
            response.EnsureSuccessStatusCode();

            var responseData = await response.Content.ReadFromJsonAsync<ChatCompletionResponse>();

            List<ToolCall>? toolCalls = responseData?.Choices.FirstOrDefault()?.Message?.ToolCalls;

            if (toolCalls is { Count: > 0 })
            {
                var toolCall = toolCalls.First();

                if (toolCall.Function is null)
                    return "Erro: Chamada de função recebida sem objeto Function.";

                string functionName = toolCall.Function.Name;
                string arguments   = toolCall.Function.Arguments;

                if (functionName == "read_files")
                {
                    string? filename = ExtractStringArgument(arguments, "filename");

                    if (string.IsNullOrWhiteSpace(filename))
                        return $"Erro: argumento 'filename' ausente ou inválido. JSON recebido: {arguments}";

                    string fileContent = await _engineService.ReadFileAsync(filename);

                    if (string.IsNullOrEmpty(fileContent))
                        throw new InvalidOperationException(
                            $"O conteúdo do arquivo '{filename}' está vazio ou não pôde ser lido.");

                    return await GetCompletionAsync(
                        $"[Sistema] O conteúdo do arquivo '{filename}' é:\n{fileContent}\n\n" +
                        "[Sistema] Use essas informações para responder à pergunta do usuário.\n" +
                        "A pergunta do usuário é: " + prompt,
                        recursionDepth + 1);
                }

                if (functionName == "search_content")
                {
                    string? query    = ExtractStringArgument(arguments, "query");
                    string? filename = ExtractStringArgument(arguments, "filename");

                    if (string.IsNullOrWhiteSpace(query))
                        return $"Erro: argumento 'query' ausente. JSON recebido: {arguments}";

                    string searchResults = await _engineService.SearchContentAsync(query, filename);

                    if (string.IsNullOrEmpty(searchResults))
                        return $"Nenhum resultado encontrado para a query: '{query}'.";

                    return await GetCompletionAsync(
                        $"[Sistema] Trechos relevantes encontrados para '{query}':\n{searchResults}\n\n" +
                        "[Sistema] Use esses trechos para responder à pergunta do usuário.\n" +
                        "A pergunta do usuário é: " + prompt,
                        recursionDepth + 1);
                }

                return $"Erro: Função '{functionName}' não reconhecida pelo orquestrador.";
            }

            return responseData?.Choices?.FirstOrDefault()?.Message?.Content
                   ?? "Erro: Sem resposta da IA.";
        }

        private static string? ExtractStringArgument(string jsonArguments, string key)
        {
            if (string.IsNullOrWhiteSpace(jsonArguments))
                return null;

            try
            {
                using var doc = JsonDocument.Parse(jsonArguments);
                if (doc.RootElement.TryGetProperty(key, out JsonElement prop))
                {
                    return prop.ValueKind switch
                    {
                        JsonValueKind.String => prop.GetString(),
                        JsonValueKind.Null   => null,
                        _                    => prop.ToString()
                    };
                }
            }
            catch (JsonException)
            {
                // The LLM occasionally returns non-JSON arguments; returns null safely.
            }

            return null;
        }

        private List<ToolRequest> GetAvailableTools()
        {
            var readFiles = new ToolRequest(
                "function",
                new ToolFunction
                {
                    Name = "read_files",
                    Description = "Lê o conteúdo COMPLETO de um ficheiro do diretório de dados. " +
                                  "Use apenas para ficheiros pequenos. Para manuais ou planilhas grandes, prefira search_content.",
                    Parameters = new Parameters
                    {
                        Type = "object",
                        Required = new List<string> { "filename" },
                        Properties = new Dictionary<string, Property>
                        {
                            {
                                "filename", new Property
                                {
                                    Type = "string",
                                    Description = "Nome com extensão do ficheiro a ler (ex: 'manual.pdf')."
                                }
                            }
                        }
                    }
                }
            );

            var searchContent = new ToolRequest(
                "function",
                new ToolFunction
                {
                    Name = "search_content",
                    Description = "Faz busca semântica nos documentos indexados e retorna os trechos mais relevantes. " +
                                  "Ideal para ficheiros grandes onde injetar o conteúdo completo excederia o limite de tokens.",
                    Parameters = new Parameters
                    {
                        Type = "object",
                        Required = new List<string> { "query" },
                        Properties = new Dictionary<string, Property>
                        {
                            {
                                "query", new Property
                                {
                                    Type = "string",
                                    Description = "Pergunta ou assunto a pesquisar nos documentos (ex: 'prazo de garantia do produto X')."
                                }
                            },
                            {
                                "filename", new Property
                                {
                                    Type = "string",
                                    Description = "Opcional. Restringe a busca a um ficheiro específico."
                                }
                            }
                        }
                    }
                }
            );

            return new List<ToolRequest> { readFiles, searchContent };
        }
    }
}
