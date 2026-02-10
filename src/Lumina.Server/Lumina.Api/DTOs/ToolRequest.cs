using System.Text.Json.Serialization;
using Microsoft.VisualBasic;

namespace Lumina.Api.DTOs
{
    public class ToolRequest
    {
        [JsonPropertyName("type")]
        public string type { get; set; } = "function";
        [JsonPropertyName("function")]
        public ToolFunction Function { get; set; } = new ToolFunction();

        public ToolRequest(string type, ToolFunction function)
        {
            this.type = type;
            this.Function = function;
        }

    }

    public class ToolFunction
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;

        [JsonPropertyName("parameters")]
        public Parameters Parameters { get; set; } = new Parameters();
    }

    public class Parameters
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "object";
        [JsonPropertyName("required")]
        public List<string> Required { get; set; } = new List<string>();
        [JsonPropertyName("properties")]
        public Dictionary<string, Property> Properties { get; set; } = new Dictionary<string, Property>();
    }

    public class Property
    {
        [JsonPropertyName("type")]
        public object Type { get; set; } = "string";
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
    }
}