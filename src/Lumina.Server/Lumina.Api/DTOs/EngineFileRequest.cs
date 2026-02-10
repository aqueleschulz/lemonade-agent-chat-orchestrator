using System.Text.Json.Serialization;

namespace Lumina.Api.DTOs
{
    public class EngineFileRequest
    {
        [JsonPropertyName("filename")]
        public string FileName = string.Empty;
    }
}