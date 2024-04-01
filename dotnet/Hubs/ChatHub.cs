using Microsoft.AspNetCore.SignalR;

namespace SignalRWebpack.Hubs;

public class ChatHub : Hub
{
    private static string pythonClientConnectionId = "";
    public override async Task OnConnectedAsync()
    {
        await Clients.Client(Context.ConnectionId).SendAsync("connectionId", Context.ConnectionId);

        await base.OnConnectedAsync();
    }

    public Task conectClientPython(string clientConnectionId)
    {
        pythonClientConnectionId = clientConnectionId;
        return Task.CompletedTask;
    }

    public async Task NewMessage(long username, string message, string connectionId)
    {
        if (Context.ConnectionId != pythonClientConnectionId)
        {
            await Clients.Client(pythonClientConnectionId).SendAsync("messageForIA", username, message, connectionId);
        }
        //await Clients.All.SendAsync("messageReceived", username, message);

        await Clients.Client(connectionId).SendAsync("messageReceived", username, message);

    }

    private string ToString(ISingleClientProxy singleClientProxy)
    {
        throw new NotImplementedException();
    }
}