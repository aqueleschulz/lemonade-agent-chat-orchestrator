namespace Gaia.Orchestrator.Services.Interfaces
{
    public interface ILemonadeService
    {
        public Task<string> GetCompletionAsync(string prompt);
    }
}
