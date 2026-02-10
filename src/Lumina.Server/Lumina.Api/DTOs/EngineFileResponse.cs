using System.Text.Json.Serialization;

namespace Lumina.Api.DTOs
{
    public class EngineFileResponse
    {
        [JsonPropertyName("filename")]
        public string FileName = string.Empty;

        [JsonPropertyName("content")]
        public string Content = string.Empty;
    }
}