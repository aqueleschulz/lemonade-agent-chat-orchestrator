using Lumina.Api.DTOs;
using Lumina.Api.Services.Interfaces;

namespace Lumina.Api.Services
{
    public class LemonadeService : ILemonadeService
    {
        private readonly HttpClient _httpClient;
        private readonly IEngineService _engineService;
        public LemonadeService (HttpClient httpClient, IEngineService engineService)
        {
            _httpClient = httpClient;
            _engineService = engineService;
        }
        public async Task<string> GetCompletionAsync(string prompt, int recursionDepth = 0)
        {
            if(recursionDepth > 1)
                return "Erro: Não há mais tentativas de chamada de função disponíveis para evitar loops infinitos.";

            var tools = recursionDepth == 0 ? GetAvailableToolsAsync() : new List<ToolRequest>();
            var requestPayload = new ChatCompletionRequest(
                        model: "Gemma-3-4b-it-GGUF",
                        tools: tools,
                        userPrompt: prompt
                    );

            var response = await _httpClient.PostAsJsonAsync("/api/v1/chat/completions", requestPayload);

            response.EnsureSuccessStatusCode();

            var responseData = await response.Content.ReadFromJsonAsync<ChatCompletionResponse>();
            
            List<ToolCall>? toolCalls = responseData?.Choices.FirstOrDefault()?.Message?.ToolCalls;
            if(toolCalls != null && toolCalls.Count > 0)
            {
                var toolCall = toolCalls.First();
                if(toolCall.Function != null)
                {
                    string functionName = toolCall.Function.Name;
                    string arguments = toolCall.Function.Arguments;

                    if(functionName == "read_files" && arguments.Contains("filename"))
                    {
                        var argsDict = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(arguments);

                        if(argsDict == null)
                            throw new Exception($"Falha ao desserializar os argumentos da função: {arguments}"); 

                        if(argsDict != null && argsDict.ContainsKey("filename"))
                        {
                            string filename = argsDict["filename"];
                            string fileContent = await _engineService.ReadFileAsync(filename);

                            if(string.IsNullOrEmpty(fileContent))
                                throw new Exception($"O conteúdo do arquivo '{filename}' está vazio ou não pôde ser lido.");

                            recursionDepth++;
                            return await GetCompletionAsync($"[Sistema] O conteúdo do arquivo '{filename}' é:\n{fileContent}\n" +
                            "[Sistema] Use essas informações para responder à pergunta do usuário, se necessário.\n" +
                            "A pergunta do usuário é:" + prompt, recursionDepth);
                        }
                    }
                }

                return "Erro: Chamada de função não reconhecida ou argumentos inválidos.";
            }

            else
            {
                return responseData?.Choices?.FirstOrDefault()?.Message?.Content ?? "Erro: Sem resposta da IA.";
            }
        }

        private List<ToolRequest> GetAvailableToolsAsync()
        {
            ToolRequest? readFiles = new ToolRequest(
                "function",
                new ToolFunction
                {
                    Name = "read_files",
                    Description ="Lê o conteúdo de um arquivo que está no diretório de dados para extrair informações.",
                    Parameters = new Parameters
                    {
                        Type = "object",
                        Required = new List<string>() { "filename" },
                        Properties = new Dictionary<string, Property>()
                        {
                            {
                                "filename", new Property
                                {
                                    Type = "string",
                                    Description = "O nome com extensão do arquivo a ser lido. O arquivo deve estar localizado no diretório de dados."
                                }
                            }   
                        }
                    }
                }
            );

            return new List<ToolRequest> { readFiles };
        }
    }
}