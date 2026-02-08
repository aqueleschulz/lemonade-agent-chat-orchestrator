using System.Text.Json.Serialization;

namespace Gaia.Orchestrator.DTOs;

public class ChatCompletionRequest
{
    [JsonPropertyName("model")]
    public string Model { get; set; } = string.Empty;

    [JsonPropertyName("messages")]
    public List<Message> Messages { get; set; } = new();
    
    public ChatCompletionRequest(string model, string userPrompt)
    {
        Model = model;
        Messages = new List<Message> { new Message { Role = "user", Content = userPrompt } };
    }
}

public class Message
{
    [JsonPropertyName("role")]
    public string Role { get; set; } = string.Empty;

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;
}