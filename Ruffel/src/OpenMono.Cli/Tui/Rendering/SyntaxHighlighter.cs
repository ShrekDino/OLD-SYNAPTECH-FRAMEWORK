using System.Text.RegularExpressions;

namespace OpenMono.Tui.Rendering;

public enum TokenType
{
    Plain,
    Keyword,
    String,
    Comment,
    Number,
    Function
}

public readonly struct ColoredSpan
{
    public TokenType Token { get; }
    public int Start { get; }
    public int Length { get; }

    public ColoredSpan(TokenType token, int start, int length)
    {
        Token = token;
        Start = start;
        Length = length;
    }

    public void Deconstruct(out TokenType token, out int start, out int length)
    {
        token = Token;
        start = Start;
        length = Length;
    }
}

public static partial class SyntaxHighlighter
{
    private static readonly Dictionary<string, List<(Regex Pattern, TokenType Type)>> LanguageRules = new()
    {
        ["csharp"] = CSharpRules(),
        ["cs"] = CSharpRules(),
        ["c#"] = CSharpRules(),
        ["python"] = PythonRules(),
        ["json"] = JsonRules(),
        ["bash"] = BashRules(),
        ["go"] = SharedKeywordRules(
            "break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go|goto|if|import|interface|map|package|range|return|select|struct|switch|type|var"
        ),
        ["rust"] = SharedKeywordRules(
            "as|break|const|continue|crate|else|enum|extern|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return|self|static|struct|super|trait|true|type|unsafe|use|where|while"
        ),
        ["sql"] = SharedKeywordRules(
            "SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|ALTER|DROP|INDEX|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|IS|NULL|AS|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|UNION|ALL|DISTINCT|COUNT|SUM|AVG|MIN|MAX|BETWEEN|LIKE|EXISTS|CASE|WHEN|THEN|ELSE|END|WITH|RECURSIVE"
        ),
        ["yaml"] = new()
        {
            (KeyValueRe(), TokenType.Keyword),
        },
        ["typescript"] = SharedKeywordRules(
            "abstract|any|as|asserts|async|await|boolean|break|case|catch|class|const|constructor|continue|declare|default|delete|do|else|enum|export|extends|false|finally|for|from|function|get|if|implements|import|in|infer|instanceof|interface|is|keyof|let|module|namespace|never|new|null|number|object|of|package|private|protected|public|readonly|record|return|require|satisfies|set|static|string|super|switch|symbol|this|throw|true|try|type|typeof|undefined|unique|unknown|var|void|while|with|yield"
        ),
    };

    public static IReadOnlyList<ColoredSpan> Highlight(string code, string language)
    {
        if (string.IsNullOrEmpty(code))
            return Array.Empty<ColoredSpan>();

        if (!LanguageRules.TryGetValue(language, out var rules))
            return new[] { new ColoredSpan(TokenType.Plain, 0, code.Length) };

        var tokens = new List<ColoredSpan>();
        var commentRanges = new List<(int Start, int End)>();

        foreach (var (pattern, type) in rules)
        {
            if (type == TokenType.Comment)
            {
                foreach (Match m in pattern.Matches(code))
                    commentRanges.Add((m.Index, m.Index + m.Length));
            }
        }

        foreach (var (pattern, type) in rules)
        {
            foreach (Match m in pattern.Matches(code))
            {
                int start = m.Index;
                int end = start + m.Length;

                bool insideComment = false;
                foreach (var (cs, ce) in commentRanges)
                {
                    if (start >= cs && end <= ce) { insideComment = true; break; }
                }

                if (type == TokenType.Comment)
                {
                    tokens.Add(new ColoredSpan(type, start, m.Length));
                }
                else if (!insideComment)
                {
                    tokens.Add(new ColoredSpan(type, start, m.Length));
                }
            }
        }

        if (tokens.Count == 0)
            return new[] { new ColoredSpan(TokenType.Plain, 0, code.Length) };

        tokens.Sort((a, b) => a.Start.CompareTo(b.Start));
        tokens = MergeOverlapping(tokens);

        var result = new List<ColoredSpan>();
        int pos = 0;
        foreach (var t in tokens)
        {
            if (t.Start > pos)
                result.Add(new ColoredSpan(TokenType.Plain, pos, t.Start - pos));
            result.Add(t);
            pos = t.Start + t.Length;
        }
        if (pos < code.Length)
            result.Add(new ColoredSpan(TokenType.Plain, pos, code.Length - pos));

        return result;
    }

    private static List<ColoredSpan> MergeOverlapping(List<ColoredSpan> spans)
    {
        if (spans.Count <= 1) return spans;
        var result = new List<ColoredSpan> { spans[0] };
        for (int i = 1; i < spans.Count; i++)
        {
            var last = result[^1];
            var cur = spans[i];
            if (cur.Start < last.Start + last.Length)
            {
                int overlapEnd = Math.Max(last.Start + last.Length, cur.Start + cur.Length);
                result[^1] = new ColoredSpan(last.Token, last.Start, overlapEnd - last.Start);
            }
            else
            {
                result.Add(cur);
            }
        }
        return result;
    }

    public static ThemeScheme GetAttribute(TokenType token)
    {
        return ThemeManager.Current.GetSyntaxAttribute(token);
    }

    public static string? DetectLanguage(string fenceLine)
    {
        var trimmed = fenceLine.TrimStart();
        if (!trimmed.StartsWith("```") || trimmed.Length <= 3)
            return null;

        var lang = trimmed[3..].Trim().ToLowerInvariant();
        return lang.Length > 0 ? lang : null;
    }

    private static List<(Regex, TokenType)> CSharpRules() => new()
    {
        (CommentRe(), TokenType.Comment),
        (StringRe(), TokenType.String),
        (NumberRe(), TokenType.Number),
        (CSharpKeywordRe(), TokenType.Keyword),
        (CSharpFuncRe(), TokenType.Function),
    };

    private static List<(Regex, TokenType)> PythonRules() => new()
    {
        (PythonCommentRe(), TokenType.Comment),
        (PythonStringRe(), TokenType.String),
        (NumberRe(), TokenType.Number),
        (PythonKeywordRe(), TokenType.Keyword),
        (PythonFuncRe(), TokenType.Function),
    };

    private static List<(Regex, TokenType)> JsonRules() => new()
    {
        (JsonStringRe(), TokenType.String),
        (JsonNumberRe(), TokenType.Number),
        (JsonKeyValueRe(), TokenType.Keyword),
    };

    private static List<(Regex, TokenType)> BashRules() => new()
    {
        (BashCommentRe(), TokenType.Comment),
        (StringRe(), TokenType.String),
        (NumberRe(), TokenType.Number),
        (BashKeywordRe(), TokenType.Keyword),
    };

    private static List<(Regex, TokenType)> SharedKeywordRules(string keywords) => new()
    {
        (CommentRe(), TokenType.Comment),
        (StringRe(), TokenType.String),
        (NumberRe(), TokenType.Number),
        (new Regex($@"\b({keywords})\b"), TokenType.Keyword),
    };

    [GeneratedRegex(@"//[^\n]*")]
    private static partial Regex CommentRe();
    [GeneratedRegex(@"\x22(?:[^""\\]|\\.)*\x22|'(?:[^'\\]|\\.)*'")]
    private static partial Regex StringRe();
    [GeneratedRegex(@"\b\d+\.?\d*\b")]
    private static partial Regex NumberRe();
    [GeneratedRegex(@"\b(abstract|as|base|bool|break|byte|case|catch|char|checked|class|const|continue|decimal|default|delegate|do|double|else|enum|event|explicit|extern|false|finally|fixed|float|for|foreach|goto|if|implicit|in|int|interface|internal|is|lock|long|namespace|new|null|object|operator|out|override|params|private|protected|public|readonly|ref|return|sbyte|sealed|short|sizeof|stackalloc|static|string|struct|switch|this|throw|true|try|typeof|uint|ulong|unchecked|unsafe|ushort|using|var|virtual|void|volatile|while)\b")]
    private static partial Regex CSharpKeywordRe();
    [GeneratedRegex(@"(?<=[\s.(])([A-Za-z_]\w*)\s*\(")]
    private static partial Regex CSharpFuncRe();
    [GeneratedRegex(@"#[^\n]*")]
    private static partial Regex PythonCommentRe();
    [GeneratedRegex(@"\x22(?:[^""\\]|\\.)*\x22|'(?:[^'\\]|\\.)*'|\x22\x22\x22(?:[^""\\]|\\.)*?\x22\x22\x22")]
    private static partial Regex PythonStringRe();
    [GeneratedRegex(@"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b")]
    private static partial Regex PythonKeywordRe();
    [GeneratedRegex(@"(?<=[\s.(])([A-Za-z_]\w*)\s*\(")]
    private static partial Regex PythonFuncRe();
    [GeneratedRegex(@"\x22([^""\\]|\\.)*\x22")]
    private static partial Regex JsonStringRe();
    [GeneratedRegex(@"(?<=[:\s,])\d+(\.\d+)?(?=\s*[,}\]])")]
    private static partial Regex JsonNumberRe();
    [GeneratedRegex(@"\x22[^""]+\x22\s*:")]
    private static partial Regex JsonKeyValueRe();
    [GeneratedRegex(@"!![^\n]*")]
    private static partial Regex BashCommentRe();
    [GeneratedRegex(@"\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|select|until|in|return|exit|continue|break|export|local|readonly|declare|typeset|unset|eval|exec|shift|source|trap|wait)\b")]
    private static partial Regex BashKeywordRe();
    [GeneratedRegex(@"(?<=\s|^)[A-Za-z_]\w*(?=\s*:)")]
    private static partial Regex KeyValueRe();
}
