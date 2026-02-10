using System.Text.Json.Serialization;

namespace Lumina.Api.DTOs;

public class ChatCompletionRequest
{
    [JsonPropertyName("model")]
    public string Model { get; set; } = string.Empty;

    [JsonPropertyName("tools")]
    public List<ToolRequest> Tools { get; set; } = new();

    [JsonPropertyName("messages")]
    public List<Message> Messages { get; set; } = new();
    
    public ChatCompletionRequest(string model, List<ToolRequest> tools, string userPrompt)
    {
        Model = model;
        Tools = tools;
        Messages = new List<Message> { new Message { Role = "user", Content = userPrompt } };
    }
}

public class Message
{
    [JsonPropertyName("role")]
    public string Role { get; set; } = string.Empty;

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    [JsonPropertyName("tool_calls")]
    public List<ToolCall>? ToolCalls { get; set; }
}