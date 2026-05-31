namespace OpenMono.Tui;

public class StreamingMetrics
{
    private long _totalTokens;
    private DateTime _streamStart;
    private DateTime _lastTokenTime;
    private double _lastTokenCount;
    private bool _isStreaming;

    public bool IsStreaming => _isStreaming;

    public long TotalCompletionTokens => _totalTokens;

    public double TokensPerSecond
    {
        get
        {
            if (!_isStreaming || _totalTokens == 0)
                return 0;

            var elapsed = (DateTime.UtcNow - _lastTokenTime).TotalSeconds;
            if (elapsed <= 0)
                return 0;

            var recentTokens = _totalTokens - _lastTokenCount;
            return recentTokens / Math.Max(elapsed, 0.001);
        }
    }

    public void OnStreamStart()
    {
        _totalTokens = 0;
        _streamStart = DateTime.UtcNow;
        _lastTokenTime = _streamStart;
        _lastTokenCount = 0;
        _isStreaming = true;
    }

    public void OnTokenReceived(long totalCompletionTokens)
    {
        var now = DateTime.UtcNow;
        _totalTokens = totalCompletionTokens;
        _lastTokenTime = now;
    }

    public void OnStreamEnd()
    {
        _isStreaming = false;
    }
}
