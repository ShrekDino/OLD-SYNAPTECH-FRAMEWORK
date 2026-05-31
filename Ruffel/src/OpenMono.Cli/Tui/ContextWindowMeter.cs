namespace OpenMono.Tui;

public class ContextWindowMeter
{
    private const int DefaultContextSize = 128_000;
    private readonly int _contextSize;
    private int _promptTokens;

    public int PromptTokens => _promptTokens;
    public int RemainingTokens => Math.Max(0, _contextSize - _promptTokens);

    public double UsagePercent
    {
        get
        {
            if (_contextSize <= 0) return 0;
            return (double)_promptTokens / _contextSize * 100;
        }
    }

    public ContextWindowMeter(int? contextSize = null)
    {
        var size = contextSize.GetValueOrDefault();
        _contextSize = size > 0 ? size : DefaultContextSize;
    }

    public void Update(int promptTokens)
    {
        _promptTokens = Math.Min(promptTokens, _contextSize);
    }

    public string FormatRemaining()
    {
        var remaining = RemainingTokens;
        if (remaining >= 1_000)
            return $"{remaining / 1_000}K remaining";
        return $"{remaining} remaining";
    }

    public string FormatProgressBar(int width)
    {
        if (width <= 0) return string.Empty;

        var filledCount = _contextSize > 0
            ? (int)Math.Round((double)_promptTokens / _contextSize * width)
            : 0;
        filledCount = Math.Clamp(filledCount, 0, width);

        var emptyCount = width - filledCount;

        var bar = new char[width];
        for (var i = 0; i < filledCount; i++)
            bar[i] = '\u2588';
        for (var i = filledCount; i < width; i++)
            bar[i] = '\u2591';

        return new string(bar);
    }
}
