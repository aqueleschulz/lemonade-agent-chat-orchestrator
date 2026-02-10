using System.Text.Json.Serialization;

namespace Lumina.Api.DTOs
{
    public class EngineListFilesResponse
    {
        [JsonPropertyName("files")]
        public List<string> Files { get; set;} = new List<string>();
    }
}