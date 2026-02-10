namespace Lumina.Api.Services.Interfaces
{
    public interface IEngineService
    {
        Task<bool> CheckHealthAsync();
        Task<List<string>> ListFilesAsync();
        Task<string> ReadFileAsync(string filename);    
    }
}
