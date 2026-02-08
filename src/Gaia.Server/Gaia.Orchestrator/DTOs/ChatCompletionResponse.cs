using System.Text.Json.Serialization;
namespace Gaia.Orchestrator.DTOs
{
    public class ChatCompletionResponse
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;

        [JsonPropertyName("object")]
        public string Object { get; set; } = string.Empty;

        [JsonPropertyName("created")]
        public long Created { get; set; }

        [JsonPropertyName("model")]
        public string Model { get; set; } = string.Empty;

        [JsonPropertyName("choices")]
        public List<LemonadeChoice> Choices { get; set; } = new();

        [JsonPropertyName("usage")]
        public LemonadeUsage? Usage { get; set; }

        [JsonPropertyName("timings")]
        public LemonadeTimings? Timings { get; set; }
    }
    
    public class LemonadeChoice
    {
        [JsonPropertyName("index")]
        public int Index { get; set; }

        [JsonPropertyName("message")]
        public Message Message { get; set; } = new();

        [JsonPropertyName("finish_reason")]
        public string FinishReason { get; set; } = string.Empty;
    }

    public record LemonadeUsage(
        int PromptTokens,
        int CompletionTokens,
        int TotalTokens
    );

    public record LemonadeTimings(
        int Prompt_N,
        int Predicted_N,
        double Prompt_Ms,
        double Predicted_Ms,
        double Predicted_Per_Second
    );
}