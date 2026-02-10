namespace Lumina.Api.Services.Interfaces
{
    public interface ILemonadeService
    {
        public Task<string> GetCompletionAsync(string prompt, int recursionDepth = 0);
    }
}
