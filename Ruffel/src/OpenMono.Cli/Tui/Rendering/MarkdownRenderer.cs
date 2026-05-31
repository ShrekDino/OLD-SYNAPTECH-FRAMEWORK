namespace OpenMono.Tui.Rendering;

public enum BlockKind
{
    Text,
    Heading,
    CodeBlock,
    ListItem,
    BlockQuote,
    HorizontalRule
}

public class RenderAttribute
{
    public Terminal.Gui.Drawing.TextStyle Style { get; set; }
}

public class RenderSpan
{
    public string Text { get; set; } = string.Empty;
    public RenderAttribute? Attribute { get; set; }
}

public class RenderBlock
{
    public BlockKind Kind { get; set; }
    public List<RenderSpan> Spans { get; set; } = new();
    public string? Language { get; set; }
    public string? RawCode { get; set; }
    public IReadOnlyList<ColoredSpan>? HighlightedSpans { get; set; }
}

public static class MarkdownRenderer
{
    public static IReadOnlyList<RenderBlock> Render(string markdown)
    {
        if (string.IsNullOrEmpty(markdown))
            return Array.Empty<RenderBlock>();

        var blocks = new List<RenderBlock>();
        var lines = markdown.Split('\n');
        var inCodeBlock = false;
        var codeLines = new List<string>();
        var codeLang = string.Empty;

        foreach (var rawLine in lines)
        {
            var line = rawLine;

            if (line.TrimStart().StartsWith("```"))
            {
                if (!inCodeBlock)
                {
                    inCodeBlock = true;
                    codeLang = line.TrimStart()[3..].Trim();
                    codeLines = new List<string>();
                }
                else
                {
                    inCodeBlock = false;
                    var rawCode = string.Join("\n", codeLines);
                    var highlighted = SyntaxHighlighter.Highlight(rawCode, codeLang);
                    blocks.Add(new RenderBlock
                    {
                        Kind = BlockKind.CodeBlock,
                        Language = codeLang,
                        RawCode = rawCode,
                        HighlightedSpans = highlighted.Count > 1 || (highlighted.Count == 1 && highlighted[0].Token != TokenType.Plain)
                            ? highlighted : null,
                        Spans = { new RenderSpan { Text = rawCode } }
                    });
                    codeLang = string.Empty;
                }
                continue;
            }

            if (inCodeBlock)
            {
                codeLines.Add(line);
                continue;
            }

            if (string.IsNullOrWhiteSpace(line))
                continue;

            if (line.TrimStart().StartsWith("> "))
            {
                blocks.Add(new RenderBlock
                {
                    Kind = BlockKind.BlockQuote,
                    Spans = { new RenderSpan { Text = "\u2502 " + line.TrimStart()[2..].Trim() } }
                });
                continue;
            }

            if (line.TrimStart().StartsWith("- ") || line.TrimStart().StartsWith("* "))
            {
                var content = line.TrimStart()[2..];
                blocks.Add(new RenderBlock
                {
                    Kind = BlockKind.ListItem,
                    Spans =
                    {
                        new RenderSpan { Text = "\u2022 " },
                        new RenderSpan { Text = content }
                    }
                });
                continue;
            }

            if (line.TrimStart().StartsWith("1. ") || char.IsDigit(line.TrimStart()[0]) && line.TrimStart().Contains(". "))
            {
                var dotIdx = line.TrimStart().IndexOf(". ");
                var num = line.TrimStart()[..(dotIdx + 2)];
                var content = line.TrimStart()[(dotIdx + 2)..];
                blocks.Add(new RenderBlock
                {
                    Kind = BlockKind.ListItem,
                    Spans =
                    {
                        new RenderSpan { Text = num + " " },
                        new RenderSpan { Text = content }
                    }
                });
                continue;
            }

            if (line.Trim().All(c => c == '-'))
            {
                blocks.Add(new RenderBlock { Kind = BlockKind.HorizontalRule });
                continue;
            }

            if (line.StartsWith("### "))
            {
                blocks.Add(MakeHeading(line[4..], BlockKind.Heading));
                continue;
            }
            if (line.StartsWith("## "))
            {
                blocks.Add(MakeHeading(line[3..], BlockKind.Heading));
                continue;
            }
            if (line.StartsWith("# "))
            {
                blocks.Add(MakeHeading(line[2..], BlockKind.Heading));
                continue;
            }

            blocks.Add(MakeTextBlock(line));
        }

        if (inCodeBlock)
        {
            var rawCode = string.Join("\n", codeLines);
            blocks.Add(new RenderBlock
            {
                Kind = BlockKind.CodeBlock,
                Language = codeLang,
                RawCode = rawCode,
                Spans = { new RenderSpan { Text = rawCode } }
            });
        }

        return blocks;
    }

    public static bool HasIncompleteCodeFence(string text)
    {
        if (string.IsNullOrEmpty(text))
            return false;

        var openCount = 0;
        foreach (var line in text.Split('\n'))
        {
            if (line.TrimStart().StartsWith("```"))
                openCount++;
        }
        return openCount % 2 == 1;
    }

    private static RenderBlock MakeHeading(string text, BlockKind kind)
    {
        var spans = new List<RenderSpan>();
        ParseInlineFormatting(text, spans);
        return new RenderBlock { Kind = kind, Spans = spans };
    }

    private static RenderBlock MakeTextBlock(string text)
    {
        var spans = new List<RenderSpan>();
        ParseInlineFormatting(text, spans);
        return new RenderBlock { Kind = BlockKind.Text, Spans = spans };
    }

    private static void ParseInlineFormatting(string text, List<RenderSpan> spans)
    {
        var boldPattern = @"\*\*([^*]+)\*\*";
        var codePattern = @"`([^`]+)`";

        int pos = 0;
        while (pos < text.Length)
        {
            var boldMatch = System.Text.RegularExpressions.Regex.Match(text[pos..], boldPattern);
            var codeMatch = System.Text.RegularExpressions.Regex.Match(text[pos..], codePattern);

            int nextBold = boldMatch.Success ? boldMatch.Index : int.MaxValue;
            int nextCode = codeMatch.Success ? codeMatch.Index : int.MaxValue;

            if (nextBold == int.MaxValue && nextCode == int.MaxValue)
            {
                spans.Add(new RenderSpan { Text = text[pos..] });
                break;
            }

            int nextMatch = Math.Min(nextBold, nextCode);

            if (nextMatch > 0)
                spans.Add(new RenderSpan { Text = text.Substring(pos, nextMatch) });

            if (nextCode < nextBold)
            {
                spans.Add(new RenderSpan { Text = codeMatch.Groups[1].Value });
                pos += nextMatch + codeMatch.Length;
            }
            else
            {
                var attr = new RenderAttribute { Style = Terminal.Gui.Drawing.TextStyle.Bold };
                spans.Add(new RenderSpan { Text = boldMatch.Groups[1].Value, Attribute = attr });
                pos += nextMatch + boldMatch.Length;
            }
        }
    }
}
